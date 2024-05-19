import re

import pytest
from slack_sdk.socket_mode.request import SocketModeRequest

from machine.handlers.interactive_handler import _matches, create_interactive_handler
from machine.plugins.block_action import BlockAction


def _gen_block_action_request(action_id, block_id):
    payload = {
        "type": "block_actions",
        "user": {"id": "U12345678", "username": "user1", "name": "user1", "team_id": "T12345678"},
        "api_app_id": "A12345678",
        "token": "verification_token",
        "container": {
            "type": "message",
            "message_ts": "1234567890.123456",
            "channel_id": "C12345678",
            "is_ephemeral": False,
        },
        "channel": {"id": "C12345678", "name": "channel-name"},
        "message": {
            "type": "message",
            "user": "U87654321",
            "ts": "1234567890.123456",
            "bot_id": "B12345678",
            "app_id": "A12345678",
            "text": "Hello, world!",
            "team": "T12345678",
            "blocks": [
                {
                    "type": "actions",
                    "block_id": block_id,
                    "elements": [
                        {
                            "type": "button",
                            "action_id": action_id,
                            "text": {"type": "plain_text", "text": "Yes, please.", "emoji": True},
                            "style": "primary",
                            "value": "U12345678",
                        },
                    ],
                },
            ],
        },
        "state": {"values": {}},
        "trigger_id": "1234567890.123456",
        "team": {"id": "T12345678", "domain": "workspace-domain"},
        "enterprise": None,
        "is_enterprise_install": False,
        "actions": [
            {
                "type": "button",
                "action_id": action_id,
                "block_id": block_id,
                "action_ts": "1234567890.123456",
                "text": {"type": "plain_text", "text": "Yes, please.", "emoji": True},
                "value": "U12345678",
                "style": "primary",
            }
        ],
        "response_url": "https://hooks.slack.com/actions/T12345678/1234567890/1234567890",
    }
    return SocketModeRequest(type="interactive", envelope_id="x", payload=payload)


def test_matches():
    assert _matches(None, "my_action_1") is True
    assert _matches("my_action_1", "my_action_1") is True
    assert _matches("my_action_1", "my_action_2") is False
    assert _matches(re.compile("my_action.*"), "my_action_3") is True
    assert _matches(re.compile("my_action.*"), "my_block_4") is False


@pytest.mark.asyncio
async def test_create_interactive_handler_for_block_actions(
    plugin_actions, fake_plugin, socket_mode_client, slack_client
):
    handler = create_interactive_handler(plugin_actions, slack_client)
    request = _gen_block_action_request("my_action_1", "my_block")
    await handler(socket_mode_client, request)
    assert fake_plugin.block_action_function.call_count == 1
    args = fake_plugin.block_action_function.call_args
    assert isinstance(args[0][0], BlockAction)
    assert args[0][0].triggered_action.action_id == "my_action_1"
    assert args[0][0].triggered_action.block_id == "my_block"
    socket_mode_client.send_socket_mode_response.assert_called_once()
    resp = socket_mode_client.send_socket_mode_response.call_args.args[0]
    assert resp.envelope_id == "x"
    assert resp.payload is None
