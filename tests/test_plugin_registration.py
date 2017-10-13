import re
import pytest

from machine import Machine
from machine.utils.collections import CaseInsensitiveDict


@pytest.fixture()
def settings():
    settings = CaseInsensitiveDict()
    settings['PLUGINS'] = ['tests.fake_plugins']
    settings['SLACK_API_TOKEN'] = 'xoxo-abc123'
    settings['STORAGE_BACKEND'] = 'machine.storage.backends.memory.MemoryStorage'
    return settings


def test_load_and_register_plugins(settings):
    machine = Machine(settings=settings)
    actions = machine._plugin_actions

    # Test general structure of _plugin_actions
    assert set(actions.keys()) == {'process', 'listen_to', 'respond_to', 'catch_all'}

    # Test registration of process actions
    assert 'some_event' in actions['process']
    assert 'tests.fake_plugins:FakePlugin.process_function' in actions['process']['some_event']
    assert 'class' in actions['process']['some_event']['tests.fake_plugins:FakePlugin.process_function']
    assert 'function' in actions['process']['some_event']['tests.fake_plugins:FakePlugin.process_function']

    # Test registration of respond_to actions
    respond_to_key = 'tests.fake_plugins:FakePlugin.respond_function-hello'
    assert respond_to_key in actions['respond_to']
    assert 'class' in actions['respond_to'][respond_to_key]
    assert 'function' in actions['respond_to'][respond_to_key]
    assert 'regex' in actions['respond_to'][respond_to_key]
    assert actions['respond_to'][respond_to_key]['regex'] == re.compile('hello', re.IGNORECASE)

    # Test registration of listen_to actions
    listen_to_key = 'tests.fake_plugins:FakePlugin.listen_function-hi'
    assert listen_to_key in actions['listen_to']
    assert 'class' in actions['listen_to'][listen_to_key]
    assert 'function' in actions['listen_to'][listen_to_key]
    assert 'regex' in actions['listen_to'][listen_to_key]
    assert actions['listen_to'][listen_to_key]['regex'] == re.compile('hi', re.IGNORECASE)

    # Test registration of catch_all actions
    assert 'tests.fake_plugins:FakePlugin2' in actions['catch_all']
    assert 'tests.fake_plugins:FakePlugin' not in actions['catch_all']
    assert 'class' in actions['catch_all']['tests.fake_plugins:FakePlugin2']
    assert 'function' in actions['catch_all']['tests.fake_plugins:FakePlugin2']

def test_plugin_storage_fq_plugin_name(settings):
    machine = Machine(settings=settings)
    actions = machine._plugin_actions
    plugin1_cls = actions['respond_to']['tests.fake_plugins:FakePlugin.respond_function-hello']['class']
    plugin2_cls = actions['catch_all']['tests.fake_plugins:FakePlugin2']['class']
    assert plugin1_cls.storage._fq_plugin_name == 'tests.fake_plugins:FakePlugin'
    assert plugin2_cls.storage._fq_plugin_name == 'tests.fake_plugins:FakePlugin2'