from __future__ import annotations

import asyncio
import re
from typing import Awaitable, Callable, Union

from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from structlog.stdlib import get_logger

from machine.clients.slack import SlackClient
from machine.handlers.logging import create_scoped_logger
from machine.models.core import RegisteredActions
from machine.models.interactive import Action, BlockActionsPayload, InteractivePayload
from machine.plugins.block_action import BlockAction

logger = get_logger(__name__)


def create_interactive_handler(
    plugin_actions: RegisteredActions,
    slack_client: SlackClient,
) -> Callable[[AsyncBaseSocketModeClient, SocketModeRequest], Awaitable[None]]:
    async def handle_interactive_request(client: AsyncBaseSocketModeClient, request: SocketModeRequest) -> None:
        if request.type == "interactive":
            logger.debug("interactive trigger received", payload=request.payload)
            # Acknowledge the request anyway
            response = SocketModeResponse(envelope_id=request.envelope_id)
            # Don't forget having await for method calls
            await client.send_socket_mode_response(response)
            parsed_payload = InteractivePayload.validate_python(request.payload)
            if parsed_payload.type == "block_actions":
                await handle_block_actions(parsed_payload, plugin_actions, slack_client)

    return handle_interactive_request


async def handle_block_actions(
    payload: BlockActionsPayload,
    plugin_actions: RegisteredActions,
    slack_client: SlackClient,
) -> None:
    handler_funcs = []
    for handler in plugin_actions.block_actions.values():
        # if neither block_id matcher nor action_id matcher is present, we consider it as no match
        # but this is asserted during the registration of the handler
        for action in payload.actions:
            if _matches(handler.block_id_matcher, action.block_id) and _matches(
                handler.action_id_matcher, action.action_id
            ):
                block_action_obj = _gen_block_action(payload, action, slack_client)
                if "logger" in handler.function_signature.parameters:
                    block_action_logger = create_scoped_logger(
                        handler.class_name,
                        handler.function.__name__,
                        user_id=block_action_obj.user.id,
                        user_name=block_action_obj.user.name,
                    )
                    extra_args = {"logger": block_action_logger}
                else:
                    extra_args = {}
                handler_funcs.append(handler.function(block_action_obj, **extra_args))
    await asyncio.gather(*handler_funcs)


def _matches(matcher: Union[re.Pattern[str], str, None], input_: str) -> bool:
    if matcher is None:
        return True
    if isinstance(matcher, re.Pattern):
        return matcher.match(input_) is not None
    return matcher == input_


def _gen_block_action(payload: BlockActionsPayload, triggered_action: Action, slack_client: SlackClient) -> BlockAction:
    return BlockAction(slack_client, payload, triggered_action)
