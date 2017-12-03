import sys
import inspect
import logging

from clint.textui import puts, indent
from machine.settings import import_settings
from machine.singletons import Slack, Scheduler, Storage
from machine.storage import PluginStorage
from machine.utils.module_loading import import_string
from machine.plugins.base import MachineBasePlugin
from machine.dispatch import EventDispatcher
from machine.slack import MessagingClient
from machine.utils.text import show_valid, warn, error, announce

logger = logging.getLogger(__name__)


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
            self._client = Slack()
            puts("Initializing storage using backend: {}".format(self._settings['STORAGE_BACKEND']))
            self._storage = Storage.get_instance()
            logger.debug("Storage initialized!")

            self._plugin_actions = {
                'process': {},
                'listen_to': {},
                'respond_to': {},
                'catch_all': {}
            }
            puts("Loading plugins...")
            self.load_plugins()
            logger.debug("The following plugin actions were registered: %s", self._plugin_actions)
            self._dispatcher = EventDispatcher(self._plugin_actions)

    def load_plugins(self):
        with indent(4):
            logger.debug("PLUGINS: %s", self._settings['PLUGINS'])
            for plugin in self._settings['PLUGINS']:
                for class_name, cls in import_string(plugin):
                    if MachineBasePlugin in cls.__bases__ and cls is not MachineBasePlugin:
                        logger.debug("Found a Machine plugin: {}".format(plugin))
                        storage = PluginStorage(class_name)
                        instance = cls(self._settings, MessagingClient(),
                                       storage)
                        self._register_plugin(class_name, instance)
                        show_valid(class_name)

    def _register_plugin(self, plugin_class, cls_instance):
        if hasattr(cls_instance, 'catch_all'):
            self._plugin_actions['catch_all'][plugin_class] = {
                'class': cls_instance,
                'class_name': plugin_class,
                'function': getattr(cls_instance, 'catch_all')
            }
        for name, fn in inspect.getmembers(cls_instance, predicate=inspect.ismethod):
            if hasattr(fn, 'metadata'):
                self._register_plugin_actions(plugin_class, fn.metadata, cls_instance, name, fn)

    def _register_plugin_actions(self, plugin_class, metadata, cls_instance, fn_name, fn):
        fq_fn_name = "{}.{}".format(plugin_class, fn_name)
        for action, config in metadata['plugin_actions'].items():
            if action == 'process':
                event_type = config['event_type']
                event_handlers = self._plugin_actions['process'].get(event_type, {})
                event_handlers[fq_fn_name] = {
                    'class': cls_instance,
                    'class_name': plugin_class,
                    'function': fn
                }
                self._plugin_actions['process'][event_type] = event_handlers
            if action == 'respond_to' or action == 'listen_to':
                for regex in config['regex']:
                    event_handler = {
                        'class': cls_instance,
                        'class_name': plugin_class,
                        'function': fn,
                        'regex': regex
                    }
                    key = "{}-{}".format(fq_fn_name, regex.pattern)
                    self._plugin_actions[action][key] = event_handler
            if action == 'schedule':
                Scheduler.get_instance().add_job(fq_fn_name, trigger='cron', args=[cls_instance],
                                                 id=fq_fn_name, replace_existing=True, **config)

    def run(self):
        announce("\nStarting Slack Machine:")
        with indent(4):
            self._client.rtm_connect()
            show_valid("Connected to Slack")
            Scheduler.get_instance().start()
            show_valid("Scheduler started")
            show_valid("Dispatcher started")
            self._dispatcher.start()
