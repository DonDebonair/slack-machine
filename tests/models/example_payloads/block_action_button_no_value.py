payload = {
    "type": "block_actions",
    "user": {"id": "UQEUMSA0K", "username": "daan", "name": "daan", "team_id": "TQSD32X16"},
    "api_app_id": "A039QKQ6G1E",
    "token": "ZMBw88SmAGYGpwguEEH4bZ84",
    "container": {
        "type": "message",
        "message_ts": "1716206801.973899",
        "channel_id": "CQEUMSV7D",
        "is_ephemeral": False,
    },
    "trigger_id": "7146094638420.842445099040.8fbb84c74d488a7ec2646219cbb845a1",
    "team": {"id": "TQSD32X16", "domain": "dandydev"},
    "enterprise": None,
    "is_enterprise_install": False,
    "channel": {"id": "CQEUMSV7D", "name": "general"},
    "message": {
        "user": "U038Y1G7745",
        "type": "message",
        "ts": "1716206801.973899",
        "bot_id": "B0390TCABQB",
        "app_id": "A039QKQ6G1E",
        "text": "Vote for lunch",
        "team": "TQSD32X16",
        "blocks": [
            {
                "type": "section",
                "block_id": "5wxLW",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Where should we order lunch from?* Poll by <fakeLink.toUser.com|Mark>",
                    "verbatim": False,
                },
            },
            {"type": "divider", "block_id": "VcIxg"},
            {
                "type": "section",
                "block_id": "q3Yif",
                "text": {
                    "type": "mrkdwn",
                    "text": ":sushi: *Ace Wasabi Rock-n-Roll Sushi Bar*\nThe best landlocked sushi restaurant.",
                    "verbatim": False,
                },
                "accessory": {
                    "type": "button",
                    "action_id": "sushi",
                    "text": {"type": "plain_text", "text": "Vote", "emoji": True},
                },
            },
            {
                "type": "context",
                "block_id": "aLe7H",
                "elements": [
                    {
                        "type": "image",
                        "image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_1.png",
                        "alt_text": "Michael Scott",
                    },
                    {
                        "type": "image",
                        "image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_2.png",
                        "alt_text": "Dwight Schrute",
                    },
                    {
                        "type": "image",
                        "image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_3.png",
                        "alt_text": "Pam Beasely",
                    },
                    {"type": "plain_text", "text": "3 votes", "emoji": True},
                ],
            },
            {
                "type": "section",
                "block_id": "iwv9r",
                "text": {
                    "type": "mrkdwn",
                    "text": ":hamburger: *Super Hungryman Hamburgers*\nOnly for the hungriest of the hungry.",
                    "verbatim": False,
                },
                "accessory": {
                    "type": "button",
                    "action_id": "hamburger",
                    "text": {"type": "plain_text", "text": "Vote", "emoji": True},
                },
            },
            {
                "type": "context",
                "block_id": "IUs3i",
                "elements": [
                    {
                        "type": "image",
                        "image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_4.png",
                        "alt_text": "Angela",
                    },
                    {
                        "type": "image",
                        "image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_2.png",
                        "alt_text": "Dwight Schrute",
                    },
                    {"type": "plain_text", "text": "2 votes", "emoji": True},
                ],
            },
            {
                "type": "section",
                "block_id": "n5Exn",
                "text": {
                    "type": "mrkdwn",
                    "text": ":ramen: *Kagawa-Ya Udon Noodle Shop*\nDo you like to shop for noodles? We have noodles.",
                    "verbatim": False,
                },
                "accessory": {
                    "type": "button",
                    "action_id": "ramen",
                    "text": {"type": "plain_text", "text": "Vote", "emoji": True},
                },
            },
            {
                "type": "context",
                "block_id": "DRo0X",
                "elements": [{"type": "mrkdwn", "text": "No votes", "verbatim": False}],
            },
            {"type": "divider", "block_id": "fSYFi"},
            {
                "type": "actions",
                "block_id": "C7q4o",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "hsnL4",
                        "text": {"type": "plain_text", "text": "Add a suggestion", "emoji": True},
                        "value": "click_me_123",
                    }
                ],
            },
        ],
    },
    "state": {"values": {}},
    "response_url": "https://hooks.slack.com/actions/TQSD32X16/7156287676161/TySSUfp835V0G9PQk8Z5pN3w",
    "actions": [
        {
            "action_id": "sushi",
            "block_id": "q3Yif",
            "text": {"type": "plain_text", "text": "Vote", "emoji": True},
            "type": "button",
            "action_ts": "1716206811.107343",
        }
    ],
}
