from slack_sdk.socket_mode.request import SocketModeRequest


def gen_command_request(command: str, text: str):
    payload = {"command": command, "text": text, "response_url": "https://my.webhook.com"}
    return SocketModeRequest(type="slash_commands", envelope_id="x", payload=payload)


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


def _gen_view_submission_request(callback_id):
    payload = {
        "type": "view_submission",
        "team": {"id": "T12345678", "domain": "workspace-domain"},
        "user": {"id": "U12345678", "username": "user1", "name": "user1", "team_id": "T12345678"},
        "api_app_id": "A12345678",
        "token": "verification_token",
        "trigger_id": "1234567890.123456",
        "enterprise": None,
        "is_enterprise_install": False,
        "response_urls": [],
        "view": {
            "id": "V1234567890",
            "team_id": "T12345678",
            "type": "modal",
            "blocks": [
                {
                    "type": "header",
                    "block_id": "k3dNV",
                    "text": {"type": "plain_text", "text": "What do you want?", "emoji": True},
                },
                {
                    "type": "input",
                    "block_id": "modal_input",
                    "label": {"type": "plain_text", "text": "Give your opinion", "emoji": True},
                    "optional": False,
                    "dispatch_action": False,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "opinion",
                        "multiline": True,
                        "dispatch_action_config": {"trigger_actions_on": ["on_enter_pressed"]},
                    },
                },
            ],
            "private_metadata": "",
            "callback_id": callback_id,
            "state": {"values": {"modal_input": {"opinion": {"type": "plain_text_input", "value": "YYippieee"}}}},
            "hash": "1717180005.lGLYVzOE",
            "title": {"type": "plain_text", "text": "My App", "emoji": True},
            "clear_on_close": False,
            "notify_on_close": True,
            "close": {"type": "plain_text", "text": ":cry: Cancel", "emoji": True},
            "submit": {"type": "plain_text", "text": ":rocket: Submit", "emoji": True},
            "previous_view_id": None,
            "root_view_id": "V1234567890",
            "app_id": "A12345678",
            "external_id": "",
            "app_installed_team_id": "T12345678",
            "bot_id": "B1234567890",
        },
    }
    return SocketModeRequest(type="interactive", envelope_id="x", payload=payload)


def _gen_view_closed_request(callback_id):
    payload = {
        "type": "view_closed",
        "team": {"id": "T12345678", "domain": "workspace-domain"},
        "user": {"id": "U12345678", "username": "user1", "name": "user1", "team_id": "T12345678"},
        "api_app_id": "A12345678",
        "token": "verification_token",
        "enterprise": None,
        "is_enterprise_install": False,
        "is_cleared": True,
        "view": {
            "id": "V1234567890",
            "team_id": "T12345678",
            "type": "modal",
            "blocks": [
                {
                    "type": "header",
                    "block_id": "k3dNV",
                    "text": {"type": "plain_text", "text": "What do you want?", "emoji": True},
                },
                {
                    "type": "input",
                    "block_id": "modal_input",
                    "label": {"type": "plain_text", "text": "Give your opinion", "emoji": True},
                    "optional": False,
                    "dispatch_action": False,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "opinion",
                        "multiline": True,
                        "dispatch_action_config": {"trigger_actions_on": ["on_enter_pressed"]},
                    },
                },
            ],
            "private_metadata": "",
            "callback_id": callback_id,
            "state": {"values": {"modal_input": {"opinion": {"type": "plain_text_input", "value": "YYippieee"}}}},
            "hash": "1717180005.lGLYVzOE",
            "title": {"type": "plain_text", "text": "My App", "emoji": True},
            "clear_on_close": False,
            "notify_on_close": True,
            "close": {"type": "plain_text", "text": ":cry: Cancel", "emoji": True},
            "submit": {"type": "plain_text", "text": ":rocket: Submit", "emoji": True},
            "previous_view_id": None,
            "root_view_id": "V1234567890",
            "app_id": "A12345678",
            "external_id": "",
            "app_installed_team_id": "T12345678",
            "bot_id": "B1234567890",
        },
    }
    return SocketModeRequest(type="interactive", envelope_id="x", payload=payload)
