from __future__ import annotations

import re

import pytest

from machine.handlers.message_handler import _check_bot_mention, generate_message_matcher, handle_message
from machine.plugins.message import Message


@pytest.fixture
def message_matcher():
    return generate_message_matcher({})


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
async def test_handle_message_listen_to(plugin_actions, fake_plugin, slack_client, message_matcher):
    bot_name = "superbot"
    bot_id = "123"
    msg_event = _gen_msg_event("hi")

    await handle_message(msg_event, bot_name, bot_id, plugin_actions, message_matcher, slack_client, True)
    assert fake_plugin.listen_function.call_count == 1
    assert fake_plugin.respond_function.call_count == 0
    args = fake_plugin.listen_function.call_args
    _assert_message(args, "hi")


@pytest.mark.asyncio
async def test_handle_message_respond_to(plugin_actions, fake_plugin, slack_client, message_matcher):
    bot_name = "superbot"
    bot_id = "123"
    msg_event = _gen_msg_event("<@123> hello")
    await handle_message(msg_event, bot_name, bot_id, plugin_actions, message_matcher, slack_client, True)
    assert fake_plugin.respond_function.call_count == 1
    assert fake_plugin.listen_function.call_count == 0
    args = fake_plugin.respond_function.call_args
    _assert_message(args, "hello")


@pytest.mark.asyncio
async def test_handle_message_changed(plugin_actions, fake_plugin, slack_client, message_matcher):
    bot_name = "superbot"
    bot_id = "123"
    msg_event = {
        "type": "message",
        "subtype": "message_changed",
        "message": {
            "text": "hi",
            "user": "user1",
        },
        "channel_type": "channel",
        "channel": "C123",
    }
    await handle_message(msg_event, bot_name, bot_id, plugin_actions, message_matcher, slack_client, True)
    assert fake_plugin.respond_function.call_count == 0
    assert fake_plugin.listen_function.call_count == 1
    args = fake_plugin.listen_function.call_args
    _assert_message(args, "hi")
