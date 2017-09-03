import sys
import inspect
import logging
from slackclient import SlackClient
from machine.settings import import_settings
from machine.utils.module_loading import import_string
from machine.plugins.base import MachineBasePlugin
from machine.dispatch import EventDispatcher
from machine.client import MessagingClient

logger = logging.getLogger(__name__)


class Machine:
    def __init__(self):
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
            logger.warning("No local_settings found! Are you sure this is what you want?")
        if 'SLACK_API_TOKEN' not in self._settings:
            logger.error("No SLACK_API_TOKEN found in settings! I need that to work...")
            sys.exit(1)
        self._client = SlackClient(self._settings['SLACK_API_TOKEN'])
        self._plugin_actions = {
            'process': {},
            'listen_to': {},
            'respond_to': {},
            'catch_all': {}
        }
        self.load_plugins()
        logger.debug("The following plugin actions were registered: %s", self._plugin_actions)
        self._dispatcher = EventDispatcher(self._client, self._plugin_actions)

    def load_plugins(self):
        for plugin in self._settings['PLUGINS']:
            for class_name, cls in import_string(plugin):
                if MachineBasePlugin in cls.__bases__ and cls is not MachineBasePlugin:
                    logger.debug("Found a Machine plugin: {}".format(plugin))
                    instance = cls(self._settings, MessagingClient(self._client))
                    self._register_plugin(plugin, instance)

    def _register_plugin(self, plugin, cls_instance):
        if hasattr(cls_instance, 'catch_all'):
            self._plugin_actions['catch_all'][plugin] = {
                'class': cls_instance,
                'function': getattr(cls_instance, 'catch_all')
            }
        for name, fn in inspect.getmembers(cls_instance, predicate=inspect.ismethod):
            if hasattr(fn, 'metadata'):
                self._register_plugin_actions(plugin, fn.metadata, cls_instance, name, fn)

    def _register_plugin_actions(self, plugin, metadata, cls_instance, fn_name, fn):
        fq_fn_name = "{}.{}".format(plugin, fn_name)
        for action, config in metadata['plugin_actions'].items():
            if action == 'process':
                event_type = config['event_type']
                event_handlers = self._plugin_actions['process'].get(event_type, {})
                event_handlers[fq_fn_name] = {
                    'class': cls_instance,
                    'function': fn
                }
                self._plugin_actions['process'][event_type] = event_handlers
            if action == 'respond_to' or action == 'listen_to':
                event_handler = {
                    'class': cls_instance,
                    'function': fn,
                    'regex': config['regex']
                }
                self._plugin_actions[action][fq_fn_name] = event_handler

    def run(self):
        self._client.rtm_connect()
        self._dispatcher.start()
