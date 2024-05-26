import re

import pytest

from machine import Machine
from machine.clients.slack import SlackClient
from machine.models.core import BlockActionHandler, CommandHandler, MessageHandler, ModalHandler, RegisteredActions
from machine.plugins.decorators import required_settings
from machine.utils.collections import CaseInsensitiveDict
from machine.utils.logging import configure_logging


@pytest.fixture(scope="module")
def settings():
    settings = CaseInsensitiveDict()
    settings["PLUGINS"] = ["tests.fake_plugins"]
    settings["SLACK_BOT_TOKEN"] = "xoxb-abc123"
    settings["SLACK_APP_TOKEN"] = "xapp-abc123"
    settings["STORAGE_BACKEND"] = "machine.storage.backends.memory.MemoryStorage"
    return settings


@pytest.fixture
def slack_client(mocker):
    return mocker.MagicMock(spec=SlackClient)


@pytest.fixture(scope="module")
def settings_with_required(settings):
    settings["setting_1"] = "foo"
    return settings


@pytest.fixture(scope="module")
def required_settings_class():
    @required_settings(["setting_1", "setting_2"])
    class C:
        pass

    return C


@pytest.mark.asyncio
async def test_load_and_register_plugins(settings, slack_client):
    configure_logging(settings)
    machine = Machine(settings=settings)
    machine._client = slack_client
    await machine._setup_storage()
    await machine._load_plugins()
    actions = machine._registered_actions

    # Test general structure of _plugin_actions
    assert isinstance(actions, RegisteredActions)

    # Test registration of respond_to actions
    respond_to_key = "tests.fake_plugins.FakePlugin.respond_function-hello"
    assert respond_to_key in actions.respond_to
    assert isinstance(actions.respond_to[respond_to_key], MessageHandler)
    assert actions.respond_to[respond_to_key].class_name == "tests.fake_plugins.FakePlugin"
    assert actions.respond_to[respond_to_key].regex == re.compile("hello", re.IGNORECASE)

    # Test registration of listen_to actions
    listen_to_key = "tests.fake_plugins.FakePlugin.listen_function-hi"
    assert listen_to_key in actions.listen_to
    assert isinstance(actions.listen_to[listen_to_key], MessageHandler)
    assert actions.listen_to[listen_to_key].class_name == "tests.fake_plugins.FakePlugin"
    assert actions.listen_to[listen_to_key].regex == re.compile("hi", re.IGNORECASE)

    # Test registration of process actions
    process_key = "tests.fake_plugins.FakePlugin.process_function-some_event"
    assert "some_event" in actions.process
    assert process_key in actions.process["some_event"]

    # Test registration of command actions
    command_key = "/test"
    assert command_key in actions.command
    assert isinstance(actions.command[command_key], CommandHandler)
    assert actions.command[command_key].class_name == "tests.fake_plugins.FakePlugin"
    assert actions.command[command_key].command == "/test"
    assert not actions.command[command_key].is_generator

    # Test registration of generator command actions
    generator_command_key = "/test-generator"
    assert generator_command_key in actions.command
    assert isinstance(actions.command[generator_command_key], CommandHandler)
    assert actions.command[generator_command_key].class_name == "tests.fake_plugins.FakePlugin"
    assert actions.command[generator_command_key].command == "/test-generator"
    assert actions.command[generator_command_key].is_generator

    # Test registration of block actions
    block_action_key = "tests.fake_plugins.FakePlugin.block_action_function-my_action.*-my_block"
    assert block_action_key in actions.block_actions
    assert isinstance(actions.block_actions[block_action_key], BlockActionHandler)
    assert actions.block_actions[block_action_key].class_name == "tests.fake_plugins.FakePlugin"
    assert isinstance(actions.block_actions[block_action_key].action_id_matcher, re.Pattern)
    assert actions.block_actions[block_action_key].action_id_matcher == re.compile("my_action.*", re.IGNORECASE)
    assert isinstance(actions.block_actions[block_action_key].block_id_matcher, str)
    assert actions.block_actions[block_action_key].block_id_matcher == "my_block"

    # Test registration of modal actions
    modal_key = "tests.fake_plugins.FakePlugin.modal_function-my_modal.*"
    assert modal_key in actions.modal
    assert isinstance(actions.modal[modal_key], ModalHandler)
    assert actions.modal[modal_key].class_name == "tests.fake_plugins.FakePlugin"
    assert isinstance(actions.modal[modal_key].callback_id_matcher, re.Pattern)
    assert actions.modal[modal_key].callback_id_matcher == re.compile("my_modal.*", re.IGNORECASE)
    assert not actions.modal[modal_key].is_generator

    # Test registration of generator modal actions
    generator_modal_key = "tests.fake_plugins.FakePlugin.generator_modal_function-my_generator_modal"
    assert generator_modal_key in actions.modal
    assert isinstance(actions.modal[generator_modal_key], ModalHandler)
    assert actions.modal[generator_modal_key].class_name == "tests.fake_plugins.FakePlugin"
    assert actions.modal[generator_modal_key].callback_id_matcher == "my_generator_modal"
    assert actions.modal[generator_modal_key].is_generator

    # Test registration of modal_closed actions
    modal_closed_key = "tests.fake_plugins.FakePlugin.modal_closed_function-my_modal_2"
    assert modal_closed_key in actions.modal_closed
    assert isinstance(actions.modal_closed[modal_closed_key], ModalHandler)
    assert actions.modal_closed[modal_closed_key].class_name == "tests.fake_plugins.FakePlugin"
    assert actions.modal_closed[modal_closed_key].callback_id_matcher == "my_modal_2"
    assert not actions.modal_closed[modal_closed_key].is_generator


@pytest.mark.asyncio
async def test_plugin_storage_fq_plugin_name(settings, slack_client):
    machine = Machine(settings=settings)
    machine._client = slack_client
    await machine._setup_storage()
    await machine._load_plugins()
    actions = machine._registered_actions
    plugin1_cls = actions.respond_to["tests.fake_plugins.FakePlugin.respond_function-hello"].class_
    plugin2_cls = actions.listen_to["tests.fake_plugins.FakePlugin2.another_listen_function-doit"].class_
    assert plugin1_cls.storage._fq_plugin_name == "tests.fake_plugins.FakePlugin"
    assert plugin2_cls.storage._fq_plugin_name == "tests.fake_plugins.FakePlugin2"


@pytest.mark.asyncio
async def test_plugin_init(settings, slack_client):
    machine = Machine(settings=settings)
    machine._client = slack_client
    await machine._setup_storage()
    await machine._load_plugins()
    actions = machine._registered_actions
    plugin_cls = actions.listen_to["tests.fake_plugins.FakePlugin2.another_listen_function-doit"].class_
    assert plugin_cls.x == 42


def test_required_settings(settings_with_required, required_settings_class):
    machine = Machine(settings=settings_with_required)
    missing = machine._check_missing_settings(required_settings_class)
    assert "SETTING_1" not in missing
    assert "SETTING_2" in missing
