import re
from inspect import Signature

import pytest
from slack_sdk.socket_mode.aiohttp import SocketModeClient

from machine.clients.slack import SlackClient
from machine.models.core import BlockActionHandler, CommandHandler, MessageHandler, ModalHandler, RegisteredActions
from machine.storage import MachineBaseStorage
from machine.utils.collections import CaseInsensitiveDict
from tests.fake_plugins import FakePlugin


@pytest.fixture
def slack_client(mocker):
    return mocker.MagicMock(spec=SlackClient)


@pytest.fixture
def socket_mode_client(mocker):
    return mocker.MagicMock(spec=SocketModeClient)


@pytest.fixture
def storage(mocker):
    return mocker.MagicMock(spec=MachineBaseStorage)


@pytest.fixture
def fake_plugin(mocker, slack_client, storage):
    plugin_instance = FakePlugin(slack_client, CaseInsensitiveDict(), storage)
    mocker.spy(plugin_instance, "respond_function")
    mocker.spy(plugin_instance, "listen_function")
    mocker.spy(plugin_instance, "process_function")
    mocker.spy(plugin_instance, "command_function")
    mocker.spy(plugin_instance, "generator_command_function")
    mocker.spy(plugin_instance, "block_action_function")
    mocker.spy(plugin_instance, "modal_function")
    mocker.spy(plugin_instance, "generator_modal_function")
    mocker.spy(plugin_instance, "modal_closed_function")
    return plugin_instance


@pytest.fixture
def plugin_actions(fake_plugin):
    respond_fn = fake_plugin.respond_function
    listen_fn = fake_plugin.listen_function
    process_fn = fake_plugin.process_function
    command_fn = fake_plugin.command_function
    generator_command_fn = fake_plugin.generator_command_function
    block_action_fn = fake_plugin.block_action_function
    modal_fn = fake_plugin.modal_function
    generator_modal_fn = fake_plugin.generator_modal_function
    modal_closed_fn = fake_plugin.modal_closed_function
    plugin_actions = RegisteredActions(
        listen_to={
            "TestPlugin.listen_function-hi": MessageHandler(
                class_=fake_plugin,
                class_name="tests.fake_plugins.FakePlugin",
                function=listen_fn,
                function_signature=Signature.from_callable(listen_fn),
                regex=re.compile("hi", re.IGNORECASE),
                handle_message_changed=True,
            )
        },
        respond_to={
            "TestPlugin.respond_function-hello": MessageHandler(
                class_=fake_plugin,
                class_name="tests.fake_plugins.FakePlugin",
                function=respond_fn,
                function_signature=Signature.from_callable(respond_fn),
                regex=re.compile("hello", re.IGNORECASE),
                handle_message_changed=False,
            )
        },
        process={"some_event": {"TestPlugin.process_function": process_fn}},
        command={
            "/test": CommandHandler(
                class_=fake_plugin,
                class_name="tests.fake_plugins.FakePlugin",
                function=command_fn,
                function_signature=Signature.from_callable(command_fn),
                command="/test",
                is_generator=False,
            ),
            "/test-generator": CommandHandler(
                class_=fake_plugin,
                class_name="tests.fake_plugins.FakePlugin",
                function=generator_command_fn,
                function_signature=Signature.from_callable(generator_command_fn),
                command="/test-generator",
                is_generator=True,
            ),
        },
        block_actions={
            "TestPlugin.block_action_function-my_action.*-my_block": BlockActionHandler(
                class_=fake_plugin,
                class_name="tests.fake_plugins.FakePlugin",
                function=block_action_fn,
                function_signature=Signature.from_callable(block_action_fn),
                action_id_matcher=re.compile("my_action.*", re.IGNORECASE),
                block_id_matcher="my_block",
            )
        },
        modal={
            "TestPlugin.modal_function-my_modal.*": ModalHandler(
                class_=fake_plugin,
                class_name="tests.fake_plugins.FakePlugin",
                function=modal_fn,
                function_signature=Signature.from_callable(modal_fn),
                callback_id_matcher=re.compile("my_modal.*", re.IGNORECASE),
                is_generator=False,
            ),
            "TestPlugin.generator_modal_function-my_generator_modal": ModalHandler(
                class_=fake_plugin,
                class_name="tests.fake_plugins.FakePlugin",
                function=generator_modal_fn,
                function_signature=Signature.from_callable(generator_modal_fn),
                callback_id_matcher="my_generator_modal",
                is_generator=True,
            ),
        },
        modal_closed={
            "TestPlugin.modal_closed_function-my_modal_2": ModalHandler(
                class_=fake_plugin,
                class_name="tests.fake_plugins.FakePlugin",
                function=modal_closed_fn,
                function_signature=Signature.from_callable(modal_closed_fn),
                callback_id_matcher="my_modal_2",
                is_generator=False,
            )
        },
    )
    return plugin_actions
