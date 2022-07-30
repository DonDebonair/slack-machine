import re
import pytest

from machine_v2 import Machine
from machine_v2.models.core import RegisteredActions
from machine_v2.plugins.decorators import required_settings
from machine.utils.collections import CaseInsensitiveDict


@pytest.fixture(scope='module')
def settings(module_mocker):
    settings = CaseInsensitiveDict()
    settings['PLUGINS'] = ['tests.machine_v2.fake_plugins']
    settings['SLACK_BOT_TOKEN'] = 'xoxb-abc123'
    settings['SLACK_APP_TOKEN'] = 'xapp-abc123'
    settings['STORAGE_BACKEND'] = 'machine_v2.storage.backends.memory.MemoryStorage'
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
    machine._setup_storage()
    machine._load_plugins()
    actions = machine._registered_actions

    # Test general structure of _plugin_actions
    assert isinstance(actions, RegisteredActions)

    # Test registration of respond_to actions
    respond_to_key = 'tests.machine_v2.fake_plugins:FakePlugin.respond_function-hello'
    assert respond_to_key in actions.respond_to
    assert actions.respond_to[respond_to_key].class_name == 'tests.machine_v2.fake_plugins:FakePlugin'
    assert actions.respond_to[respond_to_key].regex == re.compile('hello', re.IGNORECASE)

    # Test registration of listen_to actions
    listen_to_key = 'tests.machine_v2.fake_plugins:FakePlugin.listen_function-hi'
    assert listen_to_key in actions.listen_to
    assert actions.listen_to[listen_to_key].class_name == 'tests.machine_v2.fake_plugins:FakePlugin'
    assert actions.listen_to[listen_to_key].regex == re.compile('hi', re.IGNORECASE)


def test_plugin_storage_fq_plugin_name(settings):
    machine = Machine(settings=settings)
    machine._setup_storage()
    machine._load_plugins()
    actions = machine._registered_actions
    plugin1_cls = actions.respond_to['tests.machine_v2.fake_plugins:FakePlugin.respond_function-hello'].class_
    plugin2_cls = actions.listen_to['tests.machine_v2.fake_plugins:FakePlugin2.another_listen_function-doit'].class_
    assert plugin1_cls.storage._fq_plugin_name == 'tests.machine_v2.fake_plugins:FakePlugin'
    assert plugin2_cls.storage._fq_plugin_name == 'tests.machine_v2.fake_plugins:FakePlugin2'


def test_plugin_init(settings):
    machine = Machine(settings=settings)
    machine._setup_storage()
    machine._load_plugins()
    actions = machine._registered_actions
    plugin_cls = actions.listen_to['tests.machine_v2.fake_plugins:FakePlugin2.another_listen_function-doit'].class_
    assert plugin_cls.x == 42


def test_required_settings(settings_with_required, required_settings_class):
    machine = Machine(settings=settings_with_required)
    missing = machine._check_missing_settings(required_settings_class)
    assert 'SETTING_1' not in missing
    assert 'SETTING_2' in missing
