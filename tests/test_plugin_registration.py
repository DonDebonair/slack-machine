import re
import pytest

from machine import Machine
from machine.plugins.decorators import required_settings
from machine.utils.collections import CaseInsensitiveDict


@pytest.fixture(scope='module')
def settings(module_mocker):
    settings = CaseInsensitiveDict()
    settings['PLUGINS'] = ['tests.fake_plugins']
    settings['SLACK_API_TOKEN'] = 'xoxo-abc123'
    settings['STORAGE_BACKEND'] = 'machine.storage.backends.memory.MemoryStorage'
    slack_settings = module_mocker.patch('machine.clients.singletons.slack.import_settings')
    storage_settings = module_mocker.patch('machine.clients.singletons.storage.import_settings')
    slack_settings.return_value = (settings, True)
    storage_settings.return_value = (settings, True)
    return settings


@pytest.fixture(scope='module')
def settings_with_required(settings):
    settings['setting_1'] = 'foo'
    return settings


@pytest.fixture(scope='module')
def required_settings_class():
    @required_settings(['setting_1', 'setting_2'])
    class C:
        pass
    return C


def test_load_and_register_plugins(settings):
    machine = Machine(settings=settings)
    actions = machine._plugin_actions

    # Test general structure of _plugin_actions
    assert set(actions.keys()) == {'listen_to', 'respond_to'}

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


def test_plugin_storage_fq_plugin_name(settings):
    machine = Machine(settings=settings)
    actions = machine._plugin_actions
    plugin1_cls = actions['respond_to']['tests.fake_plugins:FakePlugin.respond_function-hello']['class']
    plugin2_cls = actions['listen_to']['tests.fake_plugins:FakePlugin2.another_listen_function-doit']['class']
    assert plugin1_cls.storage._fq_plugin_name == 'tests.fake_plugins:FakePlugin'
    assert plugin2_cls.storage._fq_plugin_name == 'tests.fake_plugins:FakePlugin2'


def test_plugin_init(settings):
    machine = Machine(settings=settings)
    actions = machine._plugin_actions
    plugin_cls = actions['listen_to']['tests.fake_plugins:FakePlugin2.another_listen_function-doit']['class']
    assert plugin_cls.x == 42


def test_required_settings(settings_with_required, required_settings_class):
    machine = Machine(settings=settings_with_required)
    missing = machine._check_missing_settings(required_settings_class)
    assert 'SETTING_1' not in missing
    assert 'SETTING_2' in missing
