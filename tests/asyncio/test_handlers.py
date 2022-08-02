from __future__ import annotations
import re

import pytest
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest

from machine.asyncio.clients.slack import SlackClient
from machine.asyncio.models.core import RegisteredActions, MessageHandler
from machine.asyncio.plugins.base import Message
from machine.asyncio.storage.backends.base import MachineBaseStorage
from machine.utils.collections import CaseInsensitiveDict
from tests.asyncio.fake_plugins import FakePlugin
from machine.asyncio.handlers import (
    _check_bot_mention,
    generate_message_matcher,
    handle_message,
    create_generic_event_handler,
)


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
    return plugin_instance


@pytest.fixture
def plugin_actions(fake_plugin):
    respond_fn = getattr(fake_plugin, "respond_function")
    listen_fn = getattr(fake_plugin, "listen_function")
    process_fn = getattr(fake_plugin, "process_function")
    plugin_actions = RegisteredActions(
        listen_to={
            "TestPlugin.listen_function-hi": MessageHandler(
                class_=fake_plugin,
                class_name="tests.asyncio.fake_plugins.FakePlugin",
                function=listen_fn,
                regex=re.compile("hi", re.IGNORECASE),
            )
        },
        respond_to={
            "TestPlugin.respond_function-hello": MessageHandler(
                class_=fake_plugin,
                class_name="tests.asyncio.fake_plugins.FakePlugin",
                function=respond_fn,
                regex=re.compile("hello", re.IGNORECASE),
            )
        },
        process={"some_event": {"TestPlugin.process_function": process_fn}},
    )
    return plugin_actions


def _gen_msg_event(text: str, channel_type: str = "channel") -> dict[str, str]:
    return {"type": "message", "text": text, "channel_type": channel_type, "user": "user1"}


def test_generate_message_matcher():
    no_aliases_settings = {}
    one_alias_settings = {"ALIASES": "!"}
    two_aliases_settings = {"ALIASES": "!,$"}
    assert generate_message_matcher(no_aliases_settings) == re.compile(
        r"^(?:<@(?P<atuser>\w+)>:?|(?P<username>\w+):) ?(?P<text>.*)$", re.DOTALL
    )
    assert generate_message_matcher(one_alias_settings) == re.compile(
        r"^(?:<@(?P<atuser>\w+)>:?|(?P<username>\w+):|(?P<alias>!)) ?(?P<text>.*)$", re.DOTALL
    )
    assert generate_message_matcher(two_aliases_settings) == re.compile(
        rf"^(?:<@(?P<atuser>\w+)>:?|(?P<username>\w+):|(?P<alias>!|{re.escape('$')})) ?(?P<text>.*)$", re.DOTALL
    )


def test_check_bot_mention():
    bot_name = "superbot"
    bot_id = "123"
    message_matcher = generate_message_matcher({"ALIASES": "!,$"})

    normal_msg_event = _gen_msg_event("hi")
    event = _check_bot_mention(normal_msg_event, bot_name, bot_id, message_matcher)
    assert event is None

    mention_msg_event = _gen_msg_event("<@123> hi")
    event = _check_bot_mention(mention_msg_event, bot_name, bot_id, message_matcher)
    assert event == {"text": "hi", "channel_type": "channel", "type": "message", "user": "user1"}

    mention_msg_event_username = _gen_msg_event("superbot: hi")
    event = _check_bot_mention(mention_msg_event_username, bot_name, bot_id, message_matcher)
    assert event == {"text": "hi", "channel_type": "channel", "type": "message", "user": "user1"}

    mention_msg_event_group = _gen_msg_event("<@123> hi", channel_type="group")
    event = _check_bot_mention(mention_msg_event_group, bot_name, bot_id, message_matcher)
    assert event == {"text": "hi", "channel_type": "group", "type": "message", "user": "user1"}

    mention_msg_event_other_user = _gen_msg_event("<@456> hi")
    event = _check_bot_mention(mention_msg_event_other_user, bot_name, bot_id, message_matcher)
    assert event is None

    mention_msg_event_dm = _gen_msg_event("hi", channel_type="im")
    event = _check_bot_mention(mention_msg_event_dm, bot_name, bot_id, message_matcher)
    assert event == {"text": "hi", "channel_type": "im", "type": "message", "user": "user1"}

    mention_msg_event_dm_with_user = _gen_msg_event("<@123> hi", channel_type="im")
    event = _check_bot_mention(mention_msg_event_dm_with_user, bot_name, bot_id, message_matcher)
    assert event == {"text": "hi", "channel_type": "im", "type": "message", "user": "user1"}

    mention_msg_event_alias_1 = _gen_msg_event("!hi")
    event = _check_bot_mention(mention_msg_event_alias_1, bot_name, bot_id, message_matcher)
    assert event == {"text": "hi", "channel_type": "channel", "type": "message", "user": "user1"}

    mention_msg_event_alias_2 = _gen_msg_event("$hi")
    event = _check_bot_mention(mention_msg_event_alias_2, bot_name, bot_id, message_matcher)
    assert event == {"text": "hi", "channel_type": "channel", "type": "message", "user": "user1"}

    mention_msg_event_wrong_alias = _gen_msg_event("?hi")
    event = _check_bot_mention(mention_msg_event_wrong_alias, bot_name, bot_id, message_matcher)
    assert event is None


def _assert_message(args, text):
    # called with 1 positional arg and 0 kw args
    assert len(args[0]) == 1
    assert len(args[1]) == 0
    # assert called with Message
    assert isinstance(args[0][0], Message)
    # assert message equals expected text
    assert args[0][0].text == text


@pytest.mark.asyncio
async def test_handle_message_listen_to(plugin_actions, fake_plugin, slack_client):
    bot_name = "superbot"
    bot_id = "123"
    message_matcher = generate_message_matcher({})
    msg_event = _gen_msg_event("hi")

    await handle_message(msg_event, bot_name, bot_id, plugin_actions, message_matcher, slack_client)
    assert fake_plugin.listen_function.call_count == 1
    assert fake_plugin.respond_function.call_count == 0
    args = fake_plugin.listen_function.call_args
    _assert_message(args, "hi")


@pytest.mark.asyncio
async def test_handle_message_respond_to(plugin_actions, fake_plugin, slack_client):
    bot_name = "superbot"
    bot_id = "123"
    message_matcher = generate_message_matcher({})
    msg_event = _gen_msg_event("<@123> hello")
    await handle_message(msg_event, bot_name, bot_id, plugin_actions, message_matcher, slack_client)
    assert fake_plugin.respond_function.call_count == 1
    assert fake_plugin.listen_function.call_count == 0
    args = fake_plugin.respond_function.call_args
    _assert_message(args, "hello")


def _gen_request(event_type: str):
    return SocketModeRequest(type="events_api", envelope_id="x", payload={"event": {"type": event_type, "foo": "bar"}})


@pytest.mark.asyncio
async def test_create_generic_event_handler(plugin_actions, fake_plugin, socket_mode_client):
    handler = create_generic_event_handler(plugin_actions)
    await handler(socket_mode_client, _gen_request("other_event"))
    assert fake_plugin.process_function.call_count == 0
    await handler(socket_mode_client, _gen_request("some_event"))
    assert fake_plugin.process_function.call_count == 1
    args = fake_plugin.process_function.call_args
    assert len(args[0]) == 1
    assert len(args[1]) == 0
    assert args[0][0] == {"type": "some_event", "foo": "bar"}
