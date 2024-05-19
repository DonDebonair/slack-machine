import re
from inspect import Signature

import pytest
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest

from machine.clients.slack import SlackClient
from machine.models.core import BlockActionHandler, CommandHandler, MessageHandler, RegisteredActions
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
    return plugin_instance


@pytest.fixture
def plugin_actions(fake_plugin):
    respond_fn = fake_plugin.respond_function
    listen_fn = fake_plugin.listen_function
    process_fn = fake_plugin.process_function
    command_fn = fake_plugin.command_function
    generator_command_fn = fake_plugin.generator_command_function
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
                function=fake_plugin.block_action_function,
                function_signature=Signature.from_callable(fake_plugin.block_action_function),
                action_id_matcher=re.compile("my_action.*", re.IGNORECASE),
                block_id_matcher="my_block",
            )
        },
    )
    return plugin_actions


def gen_command_request(command: str, text: str):
    payload = {"command": command, "text": text, "response_url": "https://my.webhook.com"}
    return SocketModeRequest(type="slash_commands", envelope_id="x", payload=payload)
