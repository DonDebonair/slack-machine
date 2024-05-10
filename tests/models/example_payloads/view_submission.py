payload = {
    "type": "view_submission",
    "team": {"id": "TQSD32X16", "domain": "dandydev"},
    "user": {"id": "UQEUMSA0K", "username": "daan", "name": "daan", "team_id": "TQSD32X16"},
    "api_app_id": "A039QKQ6G1E",
    "token": "ZMBw88SmAGYGpwguEEH4bZ84",
    "trigger_id": "7098980171730.842445099040.997436e4e2827c9430b8c9c36882b3b4",
    "view": {
        "id": "V072WURP7LJ",
        "team_id": "TQSD32X16",
        "type": "modal",
        "blocks": [
            {
                "type": "section",
                "block_id": "x5guW",
                "text": {
                    "type": "plain_text",
                    "text": ":wave: Hey David!\n\nWe'd love to hear from you how we can make this place the best place you’ve ever worked.",  # noqa: E501
                    "emoji": True,
                },
            },
            {"type": "divider", "block_id": "wdCiM"},
            {
                "type": "input",
                "block_id": "working_here",
                "label": {"type": "plain_text", "text": "You enjoy working here at Pistachio & Co", "emoji": True},
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "radio_buttons",
                    "action_id": "working_here_options",
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
                "block_id": "4j/Gd",
                "label": {
                    "type": "plain_text",
                    "text": "What do you want for our team weekly lunch?",
                    "emoji": True,
                },
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "multi_static_select",
                    "placeholder": {"type": "plain_text", "text": "Select your favorites", "emoji": True},
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": ":pizza: Pizza", "emoji": True},
                            "value": "value-0",
                        },
                        {
                            "text": {"type": "plain_text", "text": ":fried_shrimp: Thai food", "emoji": True},
                            "value": "value-1",
                        },
                        {
                            "text": {"type": "plain_text", "text": ":desert_island: Hawaiian", "emoji": True},
                            "value": "value-2",
                        },
                        {
                            "text": {"type": "plain_text", "text": ":meat_on_bone: Texas BBQ", "emoji": True},
                            "value": "value-3",
                        },
                        {
                            "text": {"type": "plain_text", "text": ":hamburger: Burger", "emoji": True},
                            "value": "value-4",
                        },
                        {"text": {"type": "plain_text", "text": ":taco: Tacos", "emoji": True}, "value": "value-5"},
                        {
                            "text": {"type": "plain_text", "text": ":green_salad: Salad", "emoji": True},
                            "value": "value-6",
                        },
                        {
                            "text": {"type": "plain_text", "text": ":stew: Indian", "emoji": True},
                            "value": "value-7",
                        },
                    ],
                    "action_id": "nfisX",
                },
            },
            {
                "type": "input",
                "block_id": "it2e/",
                "label": {
                    "type": "plain_text",
                    "text": "What can we do to improve your experience working here?",
                    "emoji": True,
                },
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "dispatch_action_config": {"trigger_actions_on": ["on_enter_pressed"]},
                    "action_id": "Ni5tz",
                },
            },
            {
                "type": "input",
                "block_id": "DVhIO",
                "label": {"type": "plain_text", "text": "Anything else you want to tell us?", "emoji": True},
                "optional": True,
                "dispatch_action": False,
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "dispatch_action_config": {"trigger_actions_on": ["on_enter_pressed"]},
                    "action_id": "zJn8J",
                },
            },
            {
                "type": "section",
                "block_id": "sLIvA",
                "text": {"type": "mrkdwn", "text": "Pick a date for the deadline.", "verbatim": False},
                "accessory": {
                    "type": "datepicker",
                    "action_id": "datepicker-action",
                    "initial_date": "1990-04-28",
                    "placeholder": {"type": "plain_text", "text": "Select a date", "emoji": True},
                },
            },
        ],
        "private_metadata": "",
        "callback_id": "",
        "state": {
            "values": {
                "working_here": {
                    "working_here_options": {
                        "type": "radio_buttons",
                        "selected_option": {
                            "text": {"type": "plain_text", "text": "Agree", "emoji": True},
                            "value": "2",
                        },
                    }
                },
                "4j/Gd": {
                    "nfisX": {
                        "type": "multi_static_select",
                        "selected_options": [
                            {
                                "text": {"type": "plain_text", "text": ":desert_island: Hawaiian", "emoji": True},
                                "value": "value-2",
                            },
                            {
                                "text": {"type": "plain_text", "text": ":fried_shrimp: Thai food", "emoji": True},
                                "value": "value-1",
                            },
                        ],
                    }
                },
                "it2e/": {"Ni5tz": {"type": "plain_text_input", "value": "Pay better"}},
                "DVhIO": {"zJn8J": {"type": "plain_text_input", "value": "Nothing"}},
                "sLIvA": {"datepicker-action": {"type": "datepicker", "selected_date": "1990-04-28"}},
            }
        },
        "hash": "1715350171.Gc2dwnJZ",
        "title": {"type": "plain_text", "text": "Workplace check-in", "emoji": True},
        "clear_on_close": False,
        "notify_on_close": False,
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
        "previous_view_id": None,
        "root_view_id": "V072WURP7LJ",
        "app_id": "A039QKQ6G1E",
        "external_id": "",
        "app_installed_team_id": "TQSD32X16",
        "bot_id": "B0390TCABQB",
    },
    "response_urls": [],
    "is_enterprise_install": False,
    "enterprise": None,
}
