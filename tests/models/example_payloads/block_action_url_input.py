payload = {
    "type": "block_actions",
    "user": {"id": "UQEUMSA0K", "username": "daan", "name": "daan", "team_id": "TQSD32X16"},
    "api_app_id": "A039QKQ6G1E",
    "token": "ZMBw88SmAGYGpwguEEH4bZ84",
    "container": {
        "type": "message",
        "message_ts": "1715360075.165019",
        "channel_id": "CQEUMSV7D",
        "is_ephemeral": False,
    },
    "trigger_id": "7100031247362.842445099040.afd2daecb0de633a0006afd4eaef8a27",
    "team": {"id": "TQSD32X16", "domain": "dandydev"},
    "enterprise": None,
    "is_enterprise_install": False,
    "channel": {"id": "CQEUMSV7D", "name": "general"},
    "message": {
        "user": "U038Y1G7745",
        "type": "message",
        "ts": "1715360075.165019",
        "bot_id": "B0390TCABQB",
        "app_id": "A039QKQ6G1E",
        "text": "<@UQEUMSA0K>: Hey <@UQEUMSA0K>, you wanna see some interactive goodness? I can show you!",
        "team": "TQSD32X16",
        "blocks": [
            {
                "type": "header",
                "block_id": "7wq18",
                "text": {"type": "plain_text", "text": "Interactivity :tada:", "emoji": True},
            },
            {
                "type": "section",
                "block_id": "hOjar",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hey <@UQEUMSA0K>, you wanna see some interactive goodness? I can show you!",
                    "verbatim": False,
                },
            },
            {"type": "divider", "block_id": "H5Jbh"},
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
                    "action_id": "multi_select_menu_options",
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
            {
                "type": "section",
                "block_id": "xJwX4",
                "text": {"type": "mrkdwn", "text": "Pick a number", "verbatim": False},
                "accessory": {
                    "type": "overflow",
                    "action_id": "pick_overflow_option",
                    "options": [
                        {"text": {"type": "plain_text", "text": "One", "emoji": True}, "value": "one"},
                        {"text": {"type": "plain_text", "text": "Two", "emoji": True}, "value": "two"},
                        {"text": {"type": "plain_text", "text": "Three", "emoji": True}, "value": "three"},
                    ],
                },
            },
            {
                "type": "input",
                "block_id": "feelings",
                "label": {"type": "plain_text", "text": "Your feelings", "emoji": True},
                "hint": {"type": "plain_text", "text": "Be honest...", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "provide_feelings",
                    "dispatch_action_config": {"trigger_actions_on": ["on_enter_pressed"]},
                },
            },
            {
                "type": "input",
                "block_id": "radio_demonstration",
                "label": {
                    "type": "plain_text",
                    "text": "You enjoy this selection of input elements",
                    "emoji": True,
                },
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "radio_buttons",
                    "action_id": "select_radio_option",
                    "options": [
                        {"text": {"type": "plain_text", "text": "Strongly agree", "emoji": True}, "value": "1"},
                        {"text": {"type": "plain_text", "text": "Agree", "emoji": True}, "value": "2"},
                        {
                            "text": {"type": "plain_text", "text": "Neither agree nor disagree", "emoji": True},
                            "value": "3",
                        },
                        {"text": {"type": "plain_text", "text": "Disagree", "emoji": True}, "value": "4"},
                        {"text": {"type": "plain_text", "text": "Strongly disagree", "emoji": True}, "value": "5"},
                    ],
                },
            },
            {
                "type": "input",
                "block_id": "alphabet",
                "label": {
                    "type": "plain_text",
                    "text": "What is your favorite character in the alphabet?",
                    "emoji": True,
                },
                "hint": {"type": "plain_text", "text": "Choose wisely...", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "static_select",
                    "action_id": "select_menu_options",
                    "options": [
                        {"text": {"type": "plain_text", "text": "AAAA", "emoji": True}, "value": "A"},
                        {"text": {"type": "plain_text", "text": "BBBB", "emoji": True}, "value": "B"},
                        {"text": {"type": "plain_text", "text": "CCCC", "emoji": True}, "value": "C"},
                    ],
                },
            },
            {
                "type": "input",
                "block_id": "time_picker",
                "label": {"type": "plain_text", "text": "Pick a time", "emoji": True},
                "hint": {"type": "plain_text", "text": "Choose your time wisely...", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {"type": "timepicker", "action_id": "pick_time", "initial_time": "13:37"},
            },
            {
                "type": "input",
                "block_id": "url",
                "label": {"type": "plain_text", "text": "Provide a URL", "emoji": True},
                "hint": {"type": "plain_text", "text": "URLs are cool...", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "url_text_input",
                    "action_id": "provide_url",
                    "dispatch_action_config": {"trigger_actions_on": ["on_character_entered"]},
                },
            },
            {"type": "divider", "block_id": "GuWGz"},
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
            "date_picker": {"pick_date": {"type": "datepicker", "selected_date": "2024-05-24"}},
            "checkboxes": {
                "select_options": {
                    "type": "checkboxes",
                    "selected_options": [
                        {"text": {"type": "mrkdwn", "text": "*juicy apple*", "verbatim": False}, "value": "apple"},
                        {"text": {"type": "plain_text", "text": "fresh orange", "emoji": True}, "value": "orange"},
                    ],
                }
            },
            "email": {"provide_email": {"type": "email_text_input", "value": "daan@dv.email"}},
            "startrek": {
                "multi_select_menu_options": {
                    "type": "multi_static_select",
                    "selected_options": [
                        {"text": {"type": "plain_text", "text": "Data", "emoji": True}, "value": "data"},
                        {"text": {"type": "plain_text", "text": "Picard", "emoji": True}, "value": "picard"},
                    ],
                }
            },
            "number": {"enter_number": {"type": "number_input", "value": "55"}},
            "feelings": {"provide_feelings": {"type": "plain_text_input", "value": "I'm great!"}},
            "radio_demonstration": {
                "select_radio_option": {
                    "type": "radio_buttons",
                    "selected_option": {
                        "text": {"type": "plain_text", "text": "Disagree", "emoji": True},
                        "value": "4",
                    },
                }
            },
            "alphabet": {
                "select_menu_options": {
                    "type": "static_select",
                    "selected_option": {
                        "text": {"type": "plain_text", "text": "BBBB", "emoji": True},
                        "value": "B",
                    },
                }
            },
            "time_picker": {"pick_time": {"type": "timepicker", "selected_time": "03:00"}},
            "url": {"provide_url": {"type": "url_text_input", "value": "https://source.ag"}},
        }
    },
    "response_url": "https://hooks.slack.com/actions/TQSD32X16/7085472689175/VXwSrfkgY3GzEqG6wayvCFne",
    "actions": [
        {
            "type": "url_text_input",
            "block_id": "url",
            "action_id": "provide_url",
            "value": "https://source.ag",
            "action_ts": "1715360782.357206",
        }
    ],
}
