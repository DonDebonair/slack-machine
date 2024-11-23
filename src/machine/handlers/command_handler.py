from __future__ import annotations

import contextlib
from collections.abc import AsyncGenerator, Awaitable
from typing import Any, Callable, Union, cast

from slack_sdk.models import JsonObject
from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from structlog.stdlib import get_logger

from machine.clients.slack import SlackClient
from machine.handlers.logging import create_scoped_logger
from machine.models.core import RegisteredActions
from machine.plugins.command import Command

logger = get_logger(__name__)


def create_slash_command_handler(
    plugin_actions: RegisteredActions,
    slack_client: SlackClient,
) -> Callable[[AsyncBaseSocketModeClient, SocketModeRequest], Awaitable[None]]:
    async def handle_slash_command_request(client: AsyncBaseSocketModeClient, request: SocketModeRequest) -> None:
        if request.type == "slash_commands":
            logger.debug("slash command received", payload=request.payload)
            # We only acknowledge request if we know about this command
            if request.payload["command"] in plugin_actions.command:
                cmd = plugin_actions.command[request.payload["command"]]
                command_obj = _gen_command(request.payload, slack_client)
                if "logger" in cmd.function_signature.parameters:
                    command_logger = create_scoped_logger(
                        cmd.class_name,
                        cmd.function.__name__,
                        user_id=command_obj.sender.id,
                        user_name=command_obj.sender.name,
                    )
                    extra_args = {"logger": command_logger}
                else:
                    extra_args = {}
                # Check if the handler is a generator. In this case we have an immediate response we can send back
                if cmd.is_generator:
                    gen_fn = cast(Callable[..., AsyncGenerator[Union[dict, JsonObject, str], None]], cmd.function)
                    logger.debug("Slash command handler is generator, returning immediate ack")
                    gen = gen_fn(command_obj, **extra_args)
                    # return immediate reponse
                    payload = await gen.__anext__()
                    ack_response = SocketModeResponse(envelope_id=request.envelope_id, payload=payload)
                    await client.send_socket_mode_response(ack_response)
                    # Now run the rest of the function
                    with contextlib.suppress(StopAsyncIteration):
                        await gen.__anext__()
                else:
                    ack_response = SocketModeResponse(envelope_id=request.envelope_id)
                    await client.send_socket_mode_response(ack_response)
                    fn = cast(Callable[..., Awaitable[None]], cmd.function)
                    await fn(command_obj, **extra_args)

    return handle_slash_command_request


def _gen_command(cmd_payload: dict[str, Any], slack_client: SlackClient) -> Command:
    return Command(slack_client, cmd_payload)
