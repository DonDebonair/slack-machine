import asyncio
import logging
import sys
from typing import Dict, Optional, Any

from machine.settings import import_settings
from machine.utils.text import show_valid, warn, error, announce
from clint.textui import puts, indent
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.aiohttp import SocketModeClient

from machine_v2.clients.slack import SlackClient


class Machine:
    _socket_mode_client: SocketModeClient
    _settings: Optional[Dict[str, Any]] = None

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        if settings:
            self._settings = settings

    async def setup(self):
        announce("Initializing Slack Machine:")

        with indent(4):
            puts("Loading settings...")
            if self._settings is not None:
                found_local_settings = True
            else:
                self._settings, found_local_settings = import_settings()
            fmt = '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d |' \
                  ' %(message)s'
            date_fmt = '%Y-%m-%d %H:%M:%S'
            log_level = self._settings.get('LOGLEVEL', logging.ERROR)
            logging.basicConfig(
                level=log_level,
                format=fmt,
                datefmt=date_fmt,
            )
            logging.getLogger("slack_sdk.socket_mode.aiohttp").setLevel(logging.INFO)
            if not found_local_settings:
                warn("No local_settings found! Are you sure this is what you want?")
            if 'SLACK_APP_TOKEN' not in self._settings:
                error("No SLACK_APP_TOKEN found in settings! I need that to work...")
                sys.exit(1)
            if 'SLACK_BOT_TOKEN' not in self._settings:
                error("No SLACK_BOT_TOKEN found in settings! I need that to work...")
                sys.exit(1)

            self._socket_mode_client = SocketModeClient(
                app_token=self._settings['SLACK_APP_TOKEN'],
                web_client=AsyncWebClient(token=self._settings["SLACK_BOT_TOKEN"])
            )

    async def run(self):
        announce("\nStarting Slack Machine:")

        from slack_sdk.socket_mode.response import SocketModeResponse
        from slack_sdk.socket_mode.request import SocketModeRequest

        # Use async method
        async def process(client: SocketModeClient, req: SocketModeRequest):
            if req.type == "events_api":
                # Acknowledge the request anyway
                response = SocketModeResponse(envelope_id=req.envelope_id)
                # Don't forget having await for method calls
                await client.send_socket_mode_response(response)

                # Add a reaction to the message if it's a new message
                if req.payload["event"]["type"] == "message" \
                        and req.payload["event"].get("subtype") is None:
                    await client.web_client.reactions_add(
                        name="eyes",
                        channel=req.payload["event"]["channel"],
                        timestamp=req.payload["event"]["ts"],
                    )
            if req.type == "interactive" and req.payload.get("type") == "shortcut":
                if req.payload["callback_id"] == "hello-shortcut":
                    # Acknowledge the request
                    response = SocketModeResponse(envelope_id=req.envelope_id)
                    await client.send_socket_mode_response(response)
                    # Open a welcome modal
                    await client.web_client.views_open(
                        trigger_id=req.payload["trigger_id"],
                        view={
                            "type": "modal",
                            "callback_id": "hello-modal",
                            "title": {
                                "type": "plain_text",
                                "text": "Greetings!"
                            },
                            "submit": {
                                "type": "plain_text",
                                "text": "Good Bye"
                            },
                            "blocks": [
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "Hello!"
                                    }
                                }
                            ]
                        }
                    )

            if req.type == "interactive" \
                    and req.payload.get("type") == "view_submission":
                if req.payload["view"]["callback_id"] == "hello-modal":
                    # Acknowledge the request and close the modal
                    response = SocketModeResponse(envelope_id=req.envelope_id)
                    await client.send_socket_mode_response(response)

        # Add a new listener to receive messages from Slack
        # You can add more listeners like this
        client = SlackClient(self._socket_mode_client)
        client.register_handler(process)
        await client.setup()
        # Establish a WebSocket connection to the Socket Mode servers
        await self._socket_mode_client.connect()

        with indent(4):
            show_valid("Connected to Slack")

        # Just not to stop this process
        await asyncio.sleep(float("inf"))

    async def close(self):
        await self._socket_mode_client.close()
