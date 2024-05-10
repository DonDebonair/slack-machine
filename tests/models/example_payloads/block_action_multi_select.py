payload = {
    "type": "block_actions",
    "user": {"id": "UQEUMSA0K", "username": "daan", "name": "daan", "team_id": "TQSD32X16"},
    "api_app_id": "A039QKQ6G1E",
    "token": "ZMBw88SmAGYGpwguEEH4bZ84",
    "container": {
        "type": "message",
        "message_ts": "1715356149.379229",
        "channel_id": "CQEUMSV7D",
        "is_ephemeral": False,
    },
    "trigger_id": "7122371158416.842445099040.14873656a33cf59dce0b151b9714eb6d",
    "team": {"id": "TQSD32X16", "domain": "dandydev"},
    "enterprise": None,
    "is_enterprise_install": False,
    "channel": {"id": "CQEUMSV7D", "name": "general"},
    "message": {
        "user": "U038Y1G7745",
        "type": "message",
        "ts": "1715356149.379229",
        "bot_id": "B0390TCABQB",
        "app_id": "A039QKQ6G1E",
        "text": "<@UQEUMSA0K>: Hey <@UQEUMSA0K>, you wanna see some interactive goodness? I can show you!",
        "team": "TQSD32X16",
        "blocks": [
            {
                "type": "header",
                "block_id": "E6J8T",
                "text": {"type": "plain_text", "text": "Interactivity :tada:", "emoji": True},
            },
            {
                "type": "section",
                "block_id": "u4lX1",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hey <@UQEUMSA0K>, you wanna see some interactive goodness? I can show you!",
                    "verbatim": False,
                },
            },
            {"type": "divider", "block_id": "f2j6J"},
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
            {
                "type": "input",
                "block_id": "email",
                "label": {"type": "plain_text", "text": "Provide email address", "emoji": True},
                "hint": {"type": "plain_text", "text": "Email is personal...", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {"type": "email_text_input", "action_id": "provide_email"},
            },
            {
                "type": "input",
                "block_id": "startrek",
                "label": {"type": "plain_text", "text": "Select favorite Star Trek characters", "emoji": True},
                "hint": {"type": "plain_text", "text": "Next Generation...", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "multi_static_select",
                    "action_id": "select_menu_options",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Data", "emoji": True}, "value": "data"},
                        {"text": {"type": "plain_text", "text": "Picard", "emoji": True}, "value": "picard"},
                        {"text": {"type": "plain_text", "text": "Worf", "emoji": True}, "value": "worf"},
                    ],
                },
            },
            {
                "type": "input",
                "block_id": "number",
                "label": {"type": "plain_text", "text": "What is your favorite number?", "emoji": True},
                "hint": {"type": "plain_text", "text": "42", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {"type": "number_input", "action_id": "enter_number", "is_decimal_allowed": False},
            },
            {"type": "divider", "block_id": "Gl0qN"},
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
            "date_picker": {"pick_date": {"type": "datepicker", "selected_date": None}},
            "checkboxes": {"select_options": {"type": "checkboxes", "selected_options": []}},
            "email": {"provide_email": {"type": "email_text_input", "value": "daan@dv.email"}},
            "startrek": {
                "select_menu_options": {
                    "type": "multi_static_select",
                    "selected_options": [
                        {"text": {"type": "plain_text", "text": "Data", "emoji": True}, "value": "data"},
                        {"text": {"type": "plain_text", "text": "Picard", "emoji": True}, "value": "picard"},
                    ],
                }
            },
            "number": {"enter_number": {"type": "number_input"}},
        }
    },
    "response_url": "https://hooks.slack.com/actions/TQSD32X16/7096671829205/JIOYTi7RdhNlgbcZmRuPviKL",
    "actions": [
        {
            "type": "multi_static_select",
            "action_id": "select_menu_options",
            "block_id": "startrek",
            "selected_options": [
                {"text": {"type": "plain_text", "text": "Data", "emoji": True}, "value": "data"},
                {"text": {"type": "plain_text", "text": "Picard", "emoji": True}, "value": "picard"},
            ],
            "action_ts": "1715356169.749052",
        }
    ],
}
