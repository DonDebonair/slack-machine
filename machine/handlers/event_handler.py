from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from structlog.stdlib import get_logger

from machine.models.core import RegisteredActions

logger = get_logger(__name__)


def create_generic_event_handler(
    plugin_actions: RegisteredActions,
) -> Callable[[AsyncBaseSocketModeClient, SocketModeRequest], Awaitable[None]]:
    async def handle_event_request(client: AsyncBaseSocketModeClient, request: SocketModeRequest) -> None:
        if request.type == "events_api":
            # Acknowledge the request anyway
            response = SocketModeResponse(envelope_id=request.envelope_id)
            # Don't forget having await for method calls
            await client.send_socket_mode_response(response)

            # only process message events
            if request.payload["event"]["type"] in plugin_actions.process:
                await dispatch_event_handlers(
                    request.payload["event"], list(plugin_actions.process[request.payload["event"]["type"]].values())
                )

    return handle_event_request


async def dispatch_event_handlers(
    event: dict[str, Any], event_handlers: list[Callable[[dict[str, Any]], Awaitable[None]]]
) -> None:
    handler_funcs = [f(event) for f in event_handlers]
    await asyncio.gather(*handler_funcs)
