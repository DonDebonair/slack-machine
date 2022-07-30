from __future__ import annotations

import asyncio
import inspect
import logging
import re
import sys
from typing import Callable, cast

import dill
from clint.textui import puts, indent, colored
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web.async_client import AsyncWebClient

from machine.settings import import_settings
from machine.utils.collections import CaseInsensitiveDict
from machine.utils.module_loading import import_string
from machine.utils.text import show_valid, warn, error, announce, show_invalid
from machine_v2.clients.slack import SlackClient
from machine_v2.models.core import Manual, HumanHelp, MessageHandler, RegisteredActions
from machine_v2.plugins.base import MachineBasePlugin
from machine_v2.plugins.decorators import DecoratedPluginFunc, Metadata
from machine_v2.storage import PluginStorage, MachineBaseStorage

logger = logging.getLogger(__name__)


class Machine:
    _socket_mode_client: SocketModeClient
    _client: SlackClient
    _storage_backend: MachineBaseStorage
    _settings: CaseInsensitiveDict | None = None
    _help: Manual
    _registered_actions: RegisteredActions

    def __init__(self, settings: CaseInsensitiveDict | None = None):
        if settings:
            self._settings = settings
        self._help = Manual(human={}, robot={})
        self._registered_actions = RegisteredActions()

    def _setup_logging(self):
        fmt = "[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s"
        date_fmt = "%Y-%m-%d %H:%M:%S"
        log_level = self._settings.get("LOGLEVEL", logging.ERROR)
        logging.basicConfig(
            level=log_level,
            format=fmt,
            datefmt=date_fmt,
        )
        logging.getLogger("slack_sdk.socket_mode.aiohttp").setLevel(logging.INFO)
        logging.getLogger("slack_sdk.web.async_base_client").setLevel(logging.INFO)

    def _load_settings(self) -> bool:
        puts("Loading settings...")
        if self._settings is not None:
            found_local_settings = True
        else:
            self._settings, found_local_settings = import_settings()
        puts("Settings loaded!")
        return found_local_settings

    def _setup_storage(self):
        storage_backend = self._settings.get("STORAGE_BACKEND")
        logger.debug("Initializing storage backend %s...", storage_backend)
        _, cls = import_string(storage_backend)[0]
        self._storage_backend = cls(self._settings)
        logger.debug("Storage backend %s initialized!", storage_backend)

    async def _setup_slack_clients(self):
        # Setup Slack socket mode client
        self._socket_mode_client = SocketModeClient(
            app_token=self._settings["SLACK_APP_TOKEN"],
            web_client=AsyncWebClient(token=self._settings["SLACK_BOT_TOKEN"]),
        )

        # Setup high-level Slack client for plugins
        self._client = SlackClient(self._socket_mode_client)
        await self._client.setup()

    async def _setup(self):
        announce("Initializing Slack Machine:")

        with indent(4):
            found_local_settings = self._load_settings()
            self._setup_logging()
            if not found_local_settings:
                warn("No local_settings found! Are you sure this is what you want?")
            else:
                logger.debug("Found local settings %s", self._settings)

            # Check if Slack token are present
            if "SLACK_APP_TOKEN" not in self._settings:
                error("No SLACK_APP_TOKEN found in settings! I need that to work...")
                sys.exit(1)
            if "SLACK_BOT_TOKEN" not in self._settings:
                error("No SLACK_BOT_TOKEN found in settings! I need that to work...")
                sys.exit(1)

            # Setup storage
            self._setup_storage()

            # Setup Slack clients
            await self._setup_slack_clients()

            # Load plugins
            self._load_plugins()
            logger.debug("Registered plugin actions: %s", self._registered_actions)
            logger.debug("Plugin help: %s", self._help)

    def _load_plugins(self):
        with indent(4):
            logger.debug("PLUGINS: %s", self._settings["PLUGINS"])
            for plugin in self._settings["PLUGINS"]:
                for class_name, cls in import_string(plugin):
                    if issubclass(cls, MachineBasePlugin) and cls is not MachineBasePlugin:
                        logger.debug("Found a Machine plugin: %s", plugin)
                        storage = PluginStorage(class_name, self._storage_backend)
                        instance = cls(self._client, self._settings, storage)
                        missing_settings = self._register_plugin(class_name, instance)
                        if missing_settings:
                            show_invalid(class_name)
                            with indent(4):
                                error_msg = f"The following settings are missing: {', '.join(missing_settings)}"
                                puts(colored.red(error_msg))
                                puts(colored.red("This plugin will not be loaded!"))
                            del instance
                        else:
                            instance.init()
                            show_valid(class_name)
        self._storage_backend.set("manual", dill.dumps(self._help))

    def _register_plugin(self, plugin_class_name: str, cls_instance: MachineBasePlugin) -> list[str] | None:
        missing_settings = []
        cls_instance_for_missing_settings = cast(DecoratedPluginFunc, cls_instance)
        missing_settings.extend(self._check_missing_settings(cls_instance_for_missing_settings.__class__))
        methods = inspect.getmembers(cls_instance, predicate=inspect.ismethod)
        for _, fn in methods:
            missing_settings.extend(self._check_missing_settings(fn))
        if missing_settings:
            return missing_settings

        if cls_instance.__doc__:
            class_help = cls_instance.__doc__.splitlines()[0]
        else:
            class_help = plugin_class_name
        self._help.human[class_help] = self._help.human.get(class_help, {})
        self._help.robot[class_help] = self._help.robot.get(class_help, [])
        for name, fn in methods:
            if hasattr(fn, "metadata"):
                self._register_plugin_actions(plugin_class_name, fn.metadata, cls_instance, name, fn, class_help)

    def _check_missing_settings(self, fn_or_class: DecoratedPluginFunc) -> list[str]:
        missing_settings = []
        if hasattr(fn_or_class, "metadata") and isinstance(fn_or_class.metadata, Metadata):
            for setting in fn_or_class.metadata.required_settings:
                if setting not in self._settings:
                    missing_settings.append(setting.upper())
        return missing_settings

    def _register_plugin_actions(
        self,
        plugin_class_name: str,
        metadata: Metadata,
        cls_instance: MachineBasePlugin,
        fn_name: str,
        fn: Callable[..., None],
        class_help: str,
    ):
        fq_fn_name = "{}.{}".format(plugin_class_name, fn_name)
        if fn.__doc__:
            self._help.human[class_help][fq_fn_name] = self._parse_human_help(fn.__doc__)
        for regex in metadata.plugin_actions.listen_to:
            self._register_message_handler("listen_to", cls_instance, plugin_class_name, fn, regex, class_help)
        for regex in metadata.plugin_actions.respond_to:
            self._register_message_handler("respond_to", cls_instance, plugin_class_name, fn, regex, class_help)
        for event in metadata.plugin_actions.process:
            self._registered_actions.process[event] = self._registered_actions.process.get(event, [])
            self._registered_actions.process[event].append(fn)

    def _register_message_handler(
        self,
        type_: str,
        class_: MachineBasePlugin,
        class_name: str,
        function: Callable[..., None],
        regex: re.Pattern,
        class_help: str,
    ):
        handler = MessageHandler(class_=class_, class_name=class_name, function=function, regex=regex)
        getattr(self._registered_actions, type_).append(handler)
        self._help.robot[class_help].append(self._parse_robot_help(regex, type_))

    @staticmethod
    def _parse_human_help(doc: str) -> HumanHelp:
        summary = doc.splitlines()[0].split(":")
        if len(summary) > 1:
            command = summary[0].strip()
            cmd_help = summary[1].strip()
        else:
            command = "??"
            cmd_help = summary[0].strip()
        return HumanHelp(command=command, help=cmd_help)

    @staticmethod
    def _parse_robot_help(regex, action):
        if action == "respond_to":
            return "@botname {}".format(regex.pattern)
        else:
            return regex.pattern

    async def run(self):
        announce("\nStarting Slack Machine:")

        await self._setup()

        # Use async method
        async def process(client: SocketModeClient, req: SocketModeRequest):
            if req.type == "events_api":
                # Acknowledge the request anyway
                response = SocketModeResponse(envelope_id=req.envelope_id)
                # Don't forget having await for method calls
                await client.send_socket_mode_response(response)

                # Add a reaction to the message if it's a new message
                if req.payload["event"]["type"] == "message" and req.payload["event"].get("subtype") is None:
                    await client.web_client.reactions_add(
                        name="eyes",
                        channel=req.payload["event"]["channel"],
                        timestamp=req.payload["event"]["ts"],
                    )
            if req.type == "interactive" and req.payload.get("type") == "shortcut":
                if req.payload["callback_id"] == "hello-shortcut":
                    # Acknowledge the request
                    response = SocketModeResponse(envelope_id=req.envelope_id)
                    await client.send_socket_mode_response(response)
                    # Open a welcome modal
                    await client.web_client.views_open(
                        trigger_id=req.payload["trigger_id"],
                        view={
                            "type": "modal",
                            "callback_id": "hello-modal",
                            "title": {"type": "plain_text", "text": "Greetings!"},
                            "submit": {"type": "plain_text", "text": "Good Bye"},
                            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "Hello!"}}],
                        },
                    )

            if req.type == "interactive" and req.payload.get("type") == "view_submission":
                if req.payload["view"]["callback_id"] == "hello-modal":
                    # Acknowledge the request and close the modal
                    response = SocketModeResponse(envelope_id=req.envelope_id)
                    await client.send_socket_mode_response(response)

        # Add a new listener to receive messages from Slack
        # You can add more listeners like this
        self._client.register_handler(process)
        # Establish a WebSocket connection to the Socket Mode servers
        await self._socket_mode_client.connect()

        with indent(4):
            show_valid("Connected to Slack")

        # Just not to stop this process
        await asyncio.sleep(float("inf"))

    async def close(self):
        await self._socket_mode_client.close()
