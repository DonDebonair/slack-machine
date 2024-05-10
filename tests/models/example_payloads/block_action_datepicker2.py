payload = {
    "type": "block_actions",
    "user": {"id": "UQEUMSA0K", "username": "daan", "name": "daan", "team_id": "TQSD32X16"},
    "api_app_id": "A039QKQ6G1E",
    "token": "ZMBw88SmAGYGpwguEEH4bZ84",
    "container": {
        "type": "message",
        "message_ts": "1715342584.374249",
        "channel_id": "CQEUMSV7D",
        "is_ephemeral": False,
    },
    "trigger_id": "7095422467397.842445099040.cd3bd5114a4256367fb9afda89e67846",
    "team": {"id": "TQSD32X16", "domain": "dandydev"},
    "enterprise": None,
    "is_enterprise_install": False,
    "channel": {"id": "CQEUMSV7D", "name": "general"},
    "message": {
        "user": "U038Y1G7745",
        "type": "message",
        "ts": "1715342584.374249",
        "bot_id": "B0390TCABQB",
        "app_id": "A039QKQ6G1E",
        "text": "<@UQEUMSA0K>: Hey <@UQEUMSA0K>, you wanna see some interactive goodness? I can show you!",
        "team": "TQSD32X16",
        "blocks": [
            {
                "type": "header",
                "block_id": "VSVtX",
                "text": {"type": "plain_text", "text": "Interactivity :tada:", "emoji": True},
            },
            {
                "type": "section",
                "block_id": "IHmrg",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hey <@UQEUMSA0K>, you wanna see some interactive goodness? I can show you!",
                    "verbatim": False,
                },
            },
            {"type": "divider", "block_id": "oGuUs"},
            {
                "type": "input",
                "block_id": "date_picker",
                "label": {"type": "plain_text", "text": "Pick a date", "emoji": True},
                "hint": {"type": "plain_text", "text": "Choose your date wisely...", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {"type": "datepicker", "action_id": "pick_date"},
            },
            {
                "type": "input",
                "block_id": "checkboxes",
                "label": {"type": "plain_text", "text": "Select some fruits", "emoji": True},
                "hint": {"type": "plain_text", "text": "The fruits are healthy...", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "checkboxes",
                    "action_id": "select_options",
                    "options": [
                        {"text": {"type": "mrkdwn", "text": "*juicy apple*", "verbatim": False}, "value": "apple"},
                        {"text": {"type": "plain_text", "text": "fresh orange", "emoji": True}, "value": "orange"},
                        {"text": {"type": "plain_text", "text": "red cherry", "emoji": True}, "value": "cherry"},
                    ],
                },
            },
            {"type": "divider", "block_id": "dGpE7"},
            {
                "type": "actions",
                "block_id": "interactions_confirmation",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "interactions_approve",
                        "text": {"type": "plain_text", "text": "Yes, please.", "emoji": True},
                        "style": "primary",
                        "value": "UQEUMSA0K",
                    },
                    {
                        "type": "button",
                        "action_id": "interactions_deny",
                        "text": {"type": "plain_text", "text": "No, thank you.", "emoji": True},
                        "style": "danger",
                        "value": "UQEUMSA0K",
                    },
                ],
            },
        ],
    },
    "state": {
        "values": {
            "date_picker": {"pick_date": {"type": "datepicker", "selected_date": "2024-05-10"}},
            "checkboxes": {"select_options": {"type": "checkboxes", "selected_options": []}},
        }
    },
    "response_url": "https://hooks.slack.com/actions/TQSD32X16/7100804463908/4X4jn4jZ1n8qPGcZkv2eptyU",
    "actions": [
        {
            "type": "datepicker",
            "action_id": "pick_date",
            "block_id": "date_picker",
            "selected_date": "2024-05-10",
            "action_ts": "1715342625.621904",
        }
    ],
}
