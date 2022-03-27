import inspect
import logging
import sys
import time
from typing import Callable
from threading import Thread

import dill
from clint.textui import puts, indent, colored
from slack_sdk.rtm_v2 import RTMClient

from machine.vendor import bottle

from machine.dispatch import EventDispatcher
from machine.plugins.base import MachineBasePlugin
from machine.settings import import_settings
from machine.clients.singletons.scheduling import Scheduler
from machine.clients.singletons.storage import Storage
from machine.clients.slack import SlackClient
from machine.clients.singletons.slack import LowLevelSlackClient
from machine.storage import PluginStorage
from machine.utils.module_loading import import_string
from machine.utils.text import show_valid, show_invalid, warn, error, announce

logger = logging.getLogger(__name__)


def callable_with_sanitized_event(fn: Callable):
    def sanitzed_call(client: RTMClient, event: dict):
        return fn(event)
    return sanitzed_call


class Machine:
    def __init__(self, settings=None):
        announce("Initializing Slack Machine:")

        with indent(4):
            puts("Loading settings...")
            if settings:
                self._settings = settings
                found_local_settings = True
            else:
                self._settings, found_local_settings = import_settings()
            fmt = '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d |' \
                  ' %(message)s'
            date_fmt = '%Y-%m-%d %H:%M:%S'
            log_level = self._settings.get('LOGLEVEL', logging.ERROR)
            logging.basicConfig(
                level=log_level,
                format=fmt,
                datefmt=date_fmt,
            )
            if not found_local_settings:
                warn("No local_settings found! Are you sure this is what you want?")
            if 'SLACK_API_TOKEN' not in self._settings:
                error("No SLACK_API_TOKEN found in settings! I need that to work...")
                sys.exit(1)
            self._client = LowLevelSlackClient()
            puts("Initializing storage using backend: {}".format(self._settings['STORAGE_BACKEND']))
            self._storage = Storage.get_instance()
            logger.debug("Storage initialized!")

            self._plugin_actions = {
                'listen_to': {},
                'respond_to': {}
            }
            self._help = {
                'human': {},
                'robot': {}
            }
            self._dispatcher = EventDispatcher(self._plugin_actions, self._settings)
            puts("Loading plugins...")
            self.load_plugins()
            logger.debug("The following plugin actions were registered: %s", self._plugin_actions)

    def load_plugins(self):
        with indent(4):
            logger.debug("PLUGINS: %s", self._settings['PLUGINS'])
            for plugin in self._settings['PLUGINS']:
                for class_name, cls in import_string(plugin):
                    if issubclass(cls, MachineBasePlugin) and cls is not MachineBasePlugin:
                        logger.debug("Found a Machine plugin: %s", plugin)
                        storage = PluginStorage(class_name)
                        instance = cls(SlackClient(), self._settings, storage)
                        missing_settings = self._register_plugin(class_name, instance)
                        if missing_settings:
                            show_invalid(class_name)
                            with indent(4):
                                error_msg = "The following settings are missing: {}".format(
                                    ", ".join(missing_settings)
                                )
                                puts(colored.red(error_msg))
                                puts(colored.red("This plugin will not be loaded!"))
                            del instance
                        else:
                            instance.init()
                            show_valid(class_name)
        self._storage.set('manual', dill.dumps(self._help))

    def _register_plugin(self, plugin_class, cls_instance):
        missing_settings = []
        missing_settings.extend(self._check_missing_settings(cls_instance.__class__))
        methods = inspect.getmembers(cls_instance, predicate=inspect.ismethod)
        for _, fn in methods:
            missing_settings.extend(self._check_missing_settings(fn))
        if missing_settings:
            return missing_settings

        if cls_instance.__doc__:
            class_help = cls_instance.__doc__.splitlines()[0]
        else:
            class_help = plugin_class
        self._help['human'][class_help] = self._help['human'].get(class_help, {})
        self._help['robot'][class_help] = self._help['robot'].get(class_help, [])
        for name, fn in methods:
            if hasattr(fn, 'metadata'):
                self._register_plugin_actions(plugin_class, fn.metadata, cls_instance, name, fn,
                                              class_help)

    def _check_missing_settings(self, fn_or_class):
        missing_settings = []
        if hasattr(fn_or_class, 'metadata') and 'required_settings' in fn_or_class.metadata:
            for setting in fn_or_class.metadata['required_settings']:
                if setting not in self._settings:
                    missing_settings.append(setting.upper())
        return missing_settings

    def _register_plugin_actions(self, plugin_class, metadata, cls_instance, fn_name, fn,
                                 class_help):
        fq_fn_name = "{}.{}".format(plugin_class, fn_name)
        if fn.__doc__:
            self._help['human'][class_help][fq_fn_name] = self._parse_human_help(fn.__doc__)
        for action, config in metadata['plugin_actions'].items():
            if action == 'process':
                event_type = config['event_type']
                self._client.rtm_client.on(event_type)(callable_with_sanitized_event(fn))
            if action in ['respond_to', 'listen_to']:
                for regex in config['regex']:
                    event_handler = {
                        'class': cls_instance,
                        'class_name': plugin_class,
                        'function': fn,
                        'regex': regex
                    }
                    key = "{}-{}".format(fq_fn_name, regex.pattern)
                    self._plugin_actions[action][key] = event_handler
                    self._help['robot'][class_help].append(self._parse_robot_help(regex, action))
            if action == 'schedule':
                Scheduler.get_instance().add_job(fq_fn_name, trigger='cron', args=[cls_instance],
                                                 id=fq_fn_name, replace_existing=True, **config)
            if action == 'route':
                for route_config in config:
                    bottle.route(**route_config)(fn)

    @staticmethod
    def _parse_human_help(doc):
        summary = doc.splitlines()[0].split(':')
        if len(summary) > 1:
            command = summary[0].strip()
            cmd_help = summary[1].strip()
        else:
            command = "??"
            cmd_help = summary[0].strip()
        return {
            'command': command,
            'help': cmd_help
        }

    @staticmethod
    def _parse_robot_help(regex, action):
        if action == 'respond_to':
            return "@botname {}".format(regex.pattern)
        else:
            return regex.pattern

    def _keepalive(self):
        while True:
            time.sleep(self._settings['KEEP_ALIVE'])
            self._client.ping()
            logger.debug("Client Ping!")

    def run(self):
        announce("\nStarting Slack Machine:")
        with indent(4):
            show_valid("Connected to Slack")
            Scheduler.get_instance().start()
            show_valid("Scheduler started")
            if not self._settings['DISABLE_HTTP']:
                self._bottle_thread = Thread(
                    target=bottle.run,
                    kwargs=dict(
                        host=self._settings['HTTP_SERVER_HOST'],
                        port=self._settings['HTTP_SERVER_PORT'],
                        server=self._settings['HTTP_SERVER_BACKEND'],
                    )
                )
                self._bottle_thread.daemon = True
                self._bottle_thread.start()
                show_valid("Web server started")

            if self._settings['KEEP_ALIVE']:
                self._keep_alive_thread = Thread(target=self._keepalive)
                self._keep_alive_thread.daemon = True
                self._keep_alive_thread.start()
                show_valid(
                    "Keepalive thread started [Interval: %ss]" % self._settings['KEEP_ALIVE']
                )

            show_valid("Dispatcher started")
            self._dispatcher.start()
