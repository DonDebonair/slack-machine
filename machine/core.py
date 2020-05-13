# -*- coding: utf-8 -*-

import asyncio
import inspect
import signal
import sys
from functools import partial
from typing import Mapping, Optional

import dill
from aiohttp.web import Application, AppRunner, TCPSite
from loguru import logger

from machine.dispatch import EventDispatcher
from machine.plugins.base import MachineBasePlugin
from machine.settings import import_settings
from machine.singletons import Slack, Scheduler, Storage
from machine.slack import MessagingClient
from machine.storage import PluginStorage
from machine.utils import collections, find_shortest_indent, log_propagate
from machine.utils.module_loading import import_string

__all__ = ["Machine", "start"]


def start(loop: asyncio.AbstractEventLoop, settings: Optional[dict] = None):
    """ Given an `asyncio.AbstractEventLoop` and optional `settings` dictionary,
        create and run a `Machine` instance to completion.
    """

    # Handle INT and TERM by gracefully halting the event loop
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, partial(_prepare_to_stop, loop))

    bot = Machine(loop=loop, settings=settings)
    loop.run_until_complete(bot.run())

    # Once `prepare_to_stop` returns, `loop` is guaranteed
    # to be stopped.
    _prepare_to_stop(loop)

    loop.close()


def _prepare_to_stop(loop: asyncio.AbstractEventLoop):
    # Calling `cancel` on each task in the active loop causes
    # a `CancelledError` to be thrown into each wrapped coroutine during
    # the next iteration, which _should_ halt execution of the coroutine
    # if the coroutine does not explicitly suppress the `CancelledError`.
    for task in asyncio.Task.all_tasks(loop=loop):
        task.cancel()

    # Using `ensure_future` on the `stop` coroutine here ensures that
    # the `stop` coroutine is the last thing to run after each cancelled
    # task has its `CancelledError` emitted.
    asyncio.ensure_future(_stop(), loop=loop)
    loop.run_forever()


async def _stop():
    loop = asyncio.get_event_loop()
    logger.info("Thanks for playing!")

    loop.stop()


class Machine:
    _client: Slack
    _dispatcher: EventDispatcher
    _loop: asyncio.AbstractEventLoop
    _settings: collections.CaseInsensitiveDict
    _storage: Storage

    _help: Mapping[str, dict] = {"human": {}, "robot": {}}
    _http_app: Optional[Application] = None
    _plugin_actions: Mapping[str, dict] = {
        "process": {},
        "listen_to": {},
        "respond_to": {},
    }

    def __init__(self, loop=None, settings=None):
        log_propagate.install()
        logger.info("Initializing Slack Machine")

        self._loop = loop or asyncio.get_event_loop()

        logger.debug("Loading settings...")
        if settings:
            self._settings = settings
            found_local_settings = True
        else:
            self._settings, found_local_settings = import_settings()

        if not found_local_settings:
            logger.warning(
                "No local_settings found! Are you sure this is what you want?"
            )

        if "SLACK_API_TOKEN" not in self._settings:
            logger.error("No SLACK_API_TOKEN found in settings! I need that to work...")
            sys.exit(1)

        self._client = Slack(settings=self._settings, loop=self._loop)

        logger.info(
            "Initializing storage using backend: {}".format(
                self._settings["STORAGE_BACKEND"]
            )
        )
        self._storage = Storage(settings=self._settings)
        logger.debug("Storage initialized!")

        self._loop.run_until_complete(self._storage.connect())

        if not self._settings.get("DISABLE_HTTP", False):
            self._http_app = Application()
        else:
            self._http_app = None

        logger.debug("Loading plugins...")
        self.load_plugins()
        logger.debug(
            f"The following plugin actions were registered: {self._plugin_actions}"
        )

        self._dispatcher = EventDispatcher(self._plugin_actions, self._settings)

    def load_plugins(self):
        for plugin in self._settings["PLUGINS"]:
            for class_name, cls in import_string(plugin):
                if issubclass(cls, MachineBasePlugin) and cls is not MachineBasePlugin:
                    logger.debug("Found a Machine plugin: {}".format(plugin))
                    storage = PluginStorage(class_name)
                    instance = cls(self._settings, MessagingClient(), storage)

                    missing_settings = self._register_plugin(class_name, instance)
                    if missing_settings:
                        error_msg = "The following settings are missing: {}".format(
                            ", ".join(missing_settings)
                        )
                        logger.error(
                            f"{class_name}: {error_msg}. This plugin will not be loaded!"
                        )
                        del instance
                    else:
                        if inspect.iscoroutinefunction(instance.init):
                            self._loop.run_until_complete(instance.init(self._http_app))
                        else:
                            instance.init(self._http_app)

                        logger.info(f"Loaded plugin: {class_name}")

        self._loop.run_until_complete(
            self._storage.set("manual", dill.dumps(self._help))
        )

    async def run(self):
        logger.info("Starting Slack Machine")
        self._dispatcher.start()

        Scheduler(settings=self._settings, loop=self._loop).start()
        logger.info("Scheduler started!")

        keepaliver: Optional[asyncio.Task] = None
        runner: Optional[AppRunner] = None
        try:
            runner = await self._start_http_server()
            # Launch the keepaliver task, keeping a handle to it
            # in the current context so it can be cancelled later.
            keepaliver = await self._start_keepaliver()
            # `rtm.start()` will be continuously waited on and will not
            # return unless the connection is closed.
            logger.info("Connecting to Slack...")
            await self._client.rtm.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Slack Machine shutting down...")

            # Halt the keepaliver task
            if keepaliver and not keepaliver.cancelled():
                keepaliver.cancel()

            # Clean up/shut down the aiohttp AppRunner
            if runner is not None:
                await runner.cleanup()

    async def _start_http_server(self) -> Optional[AppRunner]:
        if self._http_app is not None:
            http_host = self._settings.get("HTTP_SERVER_HOST", "127.0.0.1")
            http_port = int(self._settings.get("HTTP_SERVER_PORT", 3000))
            logger.info(f"Starting web server on {http_host}:{http_port}...")

            runner = AppRunner(self._http_app)
            await runner.setup()

            site = TCPSite(runner, http_host, http_port)
            await site.start()

            return runner

    async def _start_keepaliver(self):
        interval = self._settings.get("KEEP_ALIVE", 30)
        if interval:
            logger.info(f"Starting keepaliver... [Interval: {interval}s]")
            return asyncio.create_task(self._keepaliver(interval))

        return None

    def _register_plugin(self, plugin_class, cls_instance):
        missing_settings = []
        missing_settings.extend(self._check_missing_settings(cls_instance.__class__))
        methods = inspect.getmembers(cls_instance, predicate=inspect.ismethod)
        for _, fn in methods:
            missing_settings.extend(self._check_missing_settings(fn))
        if missing_settings:
            return missing_settings

        if hasattr(cls_instance, "catch_all"):
            self._plugin_actions["catch_all"][plugin_class] = {
                "class": cls_instance,
                "class_name": plugin_class,
                "function": getattr(cls_instance, "catch_all"),
            }

        if cls_instance.__doc__:
            class_help = cls_instance.__doc__.splitlines()[0]
        else:
            class_help = plugin_class

        self._help["human"][class_help] = self._help["human"].get(class_help, {})
        self._help["robot"][class_help] = self._help["robot"].get(class_help, [])
        for name, fn in methods:
            if hasattr(fn, "metadata"):
                self._register_plugin_actions(
                    plugin_class, fn.metadata, cls_instance, name, fn, class_help
                )

    def _check_missing_settings(self, item):
        missing_settings = []
        if hasattr(item, "metadata") and "required_settings" in item.metadata:
            for setting in item.metadata["required_settings"]:
                if setting not in self._settings:
                    missing_settings.append(setting.upper())

        return missing_settings

    def _register_plugin_actions(
        self, plugin_class, metadata, cls_instance, fn_name, fn, class_help
    ):
        fq_fn_name = "{}.{}".format(plugin_class, fn_name)
        if fn.__doc__:
            self._help["human"][class_help][fq_fn_name] = self._parse_human_help(
                fn.__doc__
            )
        for action, config in metadata["plugin_actions"].items():
            if action == "process":
                event_type = config["event_type"]
                event_handlers = self._plugin_actions["process"].get(event_type, {})
                event_handlers[fq_fn_name] = {
                    "class": cls_instance,
                    "class_name": plugin_class,
                    "function": fn,
                }
                self._plugin_actions["process"][event_type] = event_handlers
            elif action == "respond_to" or action == "listen_to":
                for regex in config["regex"]:
                    event_handler = {
                        "class": cls_instance,
                        "class_name": plugin_class,
                        "function": fn,
                        "regex": regex,
                        "lstrip": config["lstrip"],
                    }
                    key = "{}-{}".format(fq_fn_name, regex.pattern)
                    self._plugin_actions[action][key] = event_handler
                    self._help["robot"][class_help].append(
                        self._parse_robot_help(regex, action)
                    )
            elif action == "schedule":
                Scheduler.get_instance().add_job(
                    fq_fn_name,
                    trigger="cron",
                    args=[cls_instance],
                    id=fq_fn_name,
                    replace_existing=True,
                    **config,
                )

    @staticmethod
    def _parse_human_help(doc):
        doclines = doc.splitlines()
        summary = doclines[0].split(":")

        if len(doclines) > 1:
            description = doclines[1:]
            try:
                # Trim off leading/trailing lines if they are empty
                if description[0].strip() == "":
                    description = description[1:]
                if description[-1].strip() == "":
                    description = description[:-1]

                desc_min_indent = find_shortest_indent(description)
                description = [line[desc_min_indent:] for line in description]
            except IndexError:
                pass
        else:
            description = None

        if len(summary) > 1:
            command = summary[0].strip()
            summary = summary[1].strip()
        else:
            command = "??"
            summary = summary[0].strip()

        return {"command": command, "summary": summary, "description": description}

    @staticmethod
    def _parse_robot_help(regex, action):
        if action == "respond_to":
            return "@botname {}".format(regex.pattern)
        else:
            return regex.pattern

    async def _keepaliver(self, interval):
        while True:
            await asyncio.sleep(interval)
            await self._client.rtm.ping()
            logger.debug("Client Ping!")
