from __future__ import annotations

import asyncio
import inspect
import os
import sys
from inspect import Signature
from typing import Awaitable, Callable, Literal, cast

import dill
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
from structlog.stdlib import get_logger

from machine.clients.slack import SlackClient
from machine.handlers import (
    create_generic_event_handler,
    create_interactive_handler,
    create_message_handler,
    create_slash_command_handler,
    log_request,
)
from machine.models.core import (
    BlockActionHandler,
    CommandHandler,
    HumanHelp,
    Manual,
    MessageHandler,
    RegisteredActions,
    action_block_id_to_str,
)
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import ActionConfig, CommandConfig, DecoratedPluginFunc, MatcherConfig, Metadata
from machine.settings import import_settings
from machine.storage import MachineBaseStorage, PluginStorage
from machine.utils.collections import CaseInsensitiveDict
from machine.utils.logging import configure_logging
from machine.utils.module_loading import import_string

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo  # pragma: no cover
else:
    from backports.zoneinfo import ZoneInfo  # pragma: no cover

logger = get_logger(__name__)


class Machine:
    _socket_mode_client: SocketModeClient
    _client: SlackClient | None
    _storage_backend: MachineBaseStorage
    _settings: CaseInsensitiveDict | None
    _help: Manual
    _registered_actions: RegisteredActions
    _tz: ZoneInfo
    _scheduler: AsyncIOScheduler

    def __init__(self, settings: CaseInsensitiveDict | None = None):
        if settings is not None:
            self._settings = settings
        else:
            self._settings = None
        self._help = Manual(human={}, robot={})
        self._registered_actions = RegisteredActions()
        self._client = None

    async def _setup(self) -> None:
        logger.info("Initializing Slack Machine...")

        found_local_settings = self._load_settings()
        assert self._settings is not None
        configure_logging(self._settings)
        if not found_local_settings:
            logger.warning("No local_settings found! Are you sure this is what you want?")
        else:
            logger.debug("Found local settings %s", self._settings)

        # Check if Slack token are present
        if "SLACK_APP_TOKEN" not in self._settings:
            logger.error("No SLACK_APP_TOKEN found in settings! I need that to work...")
            sys.exit(1)
        if "SLACK_BOT_TOKEN" not in self._settings:
            logger.error("No SLACK_BOT_TOKEN found in settings! I need that to work...")
            sys.exit(1)

        # Setup storage
        await self._setup_storage()

        # Setup Slack clients
        await self._setup_slack_clients()

        # Setup scheduling
        self._scheduler = AsyncIOScheduler(timezone=self._tz)

        # Load plugins
        await self._load_plugins()
        logger.debug("Registered plugin actions: %s", self._registered_actions)
        logger.debug("Plugin help: %s", self._help)

    def _load_settings(self) -> bool:
        logger.info("Loading settings...")
        if self._settings is not None:
            found_local_settings = True
        else:
            settings_module = os.environ.get("SM_SETTINGS_MODULE", "local_settings")
            self._settings, found_local_settings = import_settings(settings_module=settings_module)
        self._tz = ZoneInfo(self._settings["TZ"])
        logger.info("Settings loaded!")
        return found_local_settings

    async def _setup_storage(self) -> None:
        assert self._settings is not None
        storage_backend = self._settings.get("STORAGE_BACKEND", "machine.storage.backends.memory.MemoryStorage")
        logger.info("Initializing storage backend %s...", storage_backend)
        _, cls = import_string(storage_backend)[0]
        self._storage_backend = cls(self._settings)
        await self._storage_backend.init()
        logger.info("Storage backend %s initialized!", storage_backend)

    async def _setup_slack_clients(self) -> None:
        assert self._settings is not None
        # Setup Slack socket mode client
        self._socket_mode_client = SocketModeClient(
            app_token=self._settings["SLACK_APP_TOKEN"],
            web_client=AsyncWebClient(token=self._settings["SLACK_BOT_TOKEN"]),
            proxy=self._settings["HTTP_PROXY"],
        )

        # Setup high-level Slack client for plugins
        self._client = SlackClient(self._socket_mode_client, self._tz)
        await self._client.setup()

    # TODO: factor out plugin registration in separate class / set of functions
    async def _load_plugins(self) -> None:
        assert self._settings is not None
        if self._client is None:
            logger.error("Slack client not initialized!")
            sys.exit(1)
        logger.debug("PLUGINS: %s", self._settings["PLUGINS"])
        for plugin in self._settings["PLUGINS"]:
            for class_name, cls in import_string(plugin):
                if issubclass(cls, MachineBasePlugin) and cls is not MachineBasePlugin:
                    logger.debug("Found a Machine plugin: %s", plugin)
                    storage = PluginStorage(class_name, self._storage_backend)
                    instance = cls(self._client, self._settings, storage)
                    missing_settings = self._register_plugin(class_name, instance)
                    if missing_settings:
                        logger.warning("Error loading plugin %s", class_name)
                        error_msg = f"The following settings are missing: {', '.join(missing_settings)}"
                        logger.warning(error_msg)
                        del instance
                    else:
                        await instance.init()
                        logger.info("Plugin %s loaded", class_name)
        await self._storage_backend.set("manual", dill.dumps(self._help))

    def _register_plugin(self, plugin_class_name: str, cls_instance: MachineBasePlugin) -> list[str] | None:
        missing_settings = []
        cls_instance_for_missing_settings = cast(DecoratedPluginFunc, cls_instance)
        missing_settings.extend(self._check_missing_settings(cls_instance_for_missing_settings))
        methods = inspect.getmembers(cls_instance, predicate=inspect.ismethod)
        for _, fn in methods:
            method_for_missing_settings = cast(DecoratedPluginFunc, fn)
            missing_settings.extend(self._check_missing_settings(method_for_missing_settings))
        if missing_settings:
            return missing_settings

        class_help = cls_instance.__doc__.splitlines()[0] if cls_instance.__doc__ else plugin_class_name
        self._help.human[class_help] = self._help.human.get(class_help, {})
        self._help.robot[class_help] = self._help.robot.get(class_help, [])
        for name, fn in methods:
            if hasattr(fn, "metadata"):
                self._register_plugin_actions(plugin_class_name, fn.metadata, cls_instance, name, fn, class_help)
        return None

    def _check_missing_settings(self, fn_or_class: DecoratedPluginFunc) -> list[str]:
        missing_settings = []
        if hasattr(fn_or_class, "metadata") and isinstance(fn_or_class.metadata, Metadata):
            for setting in fn_or_class.metadata.required_settings:
                if self._settings is None or setting not in self._settings:
                    missing_settings.append(setting.upper())
        return missing_settings

    def _register_plugin_actions(
        self,
        plugin_class_name: str,
        metadata: Metadata,
        cls_instance: MachineBasePlugin,
        fn_name: str,
        fn: Callable[..., Awaitable[None]],
        class_help: str,
    ) -> None:
        fq_fn_name = f"{plugin_class_name}.{fn_name}"
        if fn.__doc__:
            self._help.human[class_help][fq_fn_name] = self._parse_human_help(fn.__doc__)
        for matcher_config in metadata.plugin_actions.listen_to:
            self._register_message_handler(
                type_="listen_to",
                class_=cls_instance,
                class_name=plugin_class_name,
                fq_fn_name=fq_fn_name,
                function=fn,
                matcher_config=matcher_config,
                class_help=class_help,
            )
        for matcher_config in metadata.plugin_actions.respond_to:
            self._register_message_handler(
                type_="respond_to",
                class_=cls_instance,
                class_name=plugin_class_name,
                fq_fn_name=fq_fn_name,
                function=fn,
                matcher_config=matcher_config,
                class_help=class_help,
            )
        for event in metadata.plugin_actions.process:
            self._registered_actions.process[event] = self._registered_actions.process.get(event, {})
            key = f"{fq_fn_name}-{event}"
            self._registered_actions.process[event][key] = fn
        for command_config in metadata.plugin_actions.commands:
            self._register_command_handler(
                class_=cls_instance,
                class_name=plugin_class_name,
                fq_fn_name=fq_fn_name,
                function=fn,
                command_config=command_config,
                class_help=class_help,
            )
        for block_action_config in metadata.plugin_actions.actions:
            self._register_block_action_handler(
                class_=cls_instance,
                class_name=plugin_class_name,
                fq_fn_name=fq_fn_name,
                function=fn,
                block_action_config=block_action_config,
                class_help=class_help,
            )

        if metadata.plugin_actions.schedule is not None:
            self._scheduler.add_job(
                fn,
                trigger="cron",
                args=[],
                id=fq_fn_name,
                replace_existing=True,
                **metadata.plugin_actions.schedule,
            )

    def _register_message_handler(
        self,
        type_: Literal["listen_to", "respond_to"],
        class_: MachineBasePlugin,
        class_name: str,
        fq_fn_name: str,
        function: Callable[..., Awaitable[None]],
        matcher_config: MatcherConfig,
        class_help: str,
    ) -> None:
        signature = Signature.from_callable(function)
        handler = MessageHandler(
            class_=class_,
            class_name=class_name,
            function=function,
            function_signature=signature,
            regex=matcher_config.regex,
            handle_message_changed=matcher_config.handle_changed_message,
        )
        key = f"{fq_fn_name}-{matcher_config.regex.pattern}"
        getattr(self._registered_actions, type_)[key] = handler
        self._help.robot[class_help].append(self._parse_robot_help(matcher_config, type_))

    def _register_command_handler(
        self,
        class_: MachineBasePlugin,
        class_name: str,
        fq_fn_name: str,
        function: Callable[..., Awaitable[None]],
        command_config: CommandConfig,
        class_help: str,
    ) -> None:
        signature = Signature.from_callable(function)
        logger.debug("signature of command handler", signature=signature, function=fq_fn_name)
        handler = CommandHandler(
            class_=class_,
            class_name=class_name,
            function=function,
            function_signature=signature,
            command=command_config.command,
            is_generator=command_config.is_generator,
        )
        command = command_config.command
        if command in self._registered_actions.command:
            logger.warning("command was already defined, previous handler will be overwritten!", command=command)
        self._registered_actions.command[command] = handler
        # TODO: add to help

    def _register_block_action_handler(
        self,
        class_: MachineBasePlugin,
        class_name: str,
        fq_fn_name: str,
        function: Callable[..., Awaitable[None]],
        block_action_config: ActionConfig,
        class_help: str,
    ) -> None:
        signature = Signature.from_callable(function)
        logger.debug("signature of block action handler", signature=signature, function=fq_fn_name)
        handler = BlockActionHandler(
            class_=class_,
            class_name=class_name,
            function=function,
            function_signature=signature,
            action_id_matcher=block_action_config.action_id,
            block_id_matcher=block_action_config.block_id,
        )
        action_id = action_block_id_to_str(block_action_config.action_id)
        block_id = action_block_id_to_str(block_action_config.block_id)
        key = f"{fq_fn_name}-{action_id}-{block_id}"
        self._registered_actions.block_actions[key] = handler

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
    def _parse_robot_help(matcher_config: MatcherConfig, action: str) -> str:
        handle_message_changed_suffix = " [includes changed messages]" if matcher_config.handle_changed_message else ""
        if action == "respond_to":
            return f"@botname {matcher_config.regex.pattern}{handle_message_changed_suffix}"
        else:
            return f"{matcher_config.regex.pattern}{handle_message_changed_suffix}"

    async def run(self) -> None:
        await self._setup()
        assert self._settings is not None
        if self._client is None:
            logger.error("Slack client not initialized!")
            sys.exit(1)

        bot_id = self._client.bot_info["user_id"]
        bot_name = self._client.bot_info["name"]

        if self._settings.get("LOGLEVEL", "ERROR").upper() == "DEBUG":
            self._client.register_handler(log_request)

        message_handler = create_message_handler(
            self._registered_actions, self._settings, bot_id, bot_name, self._client
        )
        generic_event_handler = create_generic_event_handler(self._registered_actions)
        slash_command_handler = create_slash_command_handler(self._registered_actions, self._client)
        block_action_handler = create_interactive_handler(self._registered_actions, self._client)

        self._client.register_handler(message_handler)
        self._client.register_handler(generic_event_handler)
        self._client.register_handler(slash_command_handler)
        self._client.register_handler(block_action_handler)
        # Establish a WebSocket connection to the Socket Mode servers
        await self._socket_mode_client.connect()
        logger.info("Connected to Slack")

        self._scheduler.start()
        logger.info("Scheduler started")

        # Just not to stop this process
        await asyncio.sleep(float("inf"))

    async def close(self) -> None:
        closables = [self._socket_mode_client.close(), self._storage_backend.close()]
        await asyncio.gather(*closables)
