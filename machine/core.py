import time
import sys
import inspect
from slackclient import SlackClient
from machine.settings import import_settings
from machine.utils.module_loading import import_string


class Machine:
    def __init__(self):
        self._settings = import_settings()
        if not 'SLACK_API_TOKEN' in self._settings:
            print("No SLACK_API_TOKEN found in settings! I need that to work...")
            sys.exit(1)
        self._client = SlackClient(self._settings['SLACK_API_TOKEN'])
        self._plugin_actions = {
            'process': {},
            'catch_all': {}
        }
        self.load_plugins()
        print(self._plugin_actions)

    def load_plugins(self):
        for plugin in self._settings['PLUGINS']:
            for class_name, cls in import_string(plugin):
                if hasattr(cls, 'is_machine_plugin') and cls.is_machine_plugin and class_name != 'MachineBasePlugin':
                    print("Found a Machine plugin: {}".format(plugin))
                    instance = cls(self._settings, self._client)
                    self._register_plugin(plugin, instance)

    def _fqn_fn_name(self, plugin, fn_name):
        return "{}.{}".format(plugin, fn_name)

    def _register_plugin(self, plugin, cls_instance):
        if hasattr(cls_instance, 'catch_all'):
            self._plugin_actions['catch_all'][plugin] = {
                'class': cls_instance,
                'function': getattr(cls_instance, 'catch_all')
            }
        for name, fn in inspect.getmembers(cls_instance, predicate=inspect.ismethod):
            if hasattr(fn, 'metadata'):
                self._register_plugin_action(plugin, fn.metadata, cls_instance, name, fn)

    def _register_plugin_action(self, plugin, metadata, cls_instance, fn_name, fn):
        fq_fn_name = self._fqn_fn_name(plugin, fn_name)
        if metadata['plugin_action_type'] == 'process':
            event_type = metadata['plugin_action_config']['event_type']
            event_handlers = self._plugin_actions['process'].get(event_type, {})
            event_handlers[fq_fn_name] = {
                'class': cls_instance,
                'function': fn
            }
            self._plugin_actions['process'][event_type] = event_handlers

    def run(self):
        self._client.rtm_connect()
        try:
            while True:
                for event in self._client.rtm_read():
                    self.handle_event(event)
                time.sleep(.1)
        except (KeyboardInterrupt, SystemExit):
            print("Thanks for playing!")

    def handle_event(self, event):
        for action in self._plugin_actions['catch_all'].values():
            action['function'](event)
        if 'type' in event:
            if event['type'] in self._plugin_actions['process']:
                for action in self._plugin_actions['process'][event['type']].values():
                    action['function'](event)
