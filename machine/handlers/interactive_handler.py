from __future__ import annotations

import asyncio
import contextlib
import re
from collections.abc import AsyncGenerator, Awaitable
from typing import Callable, Union, cast

from slack_sdk.models.views import View
from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from structlog.stdlib import get_logger

from machine.clients.slack import SlackClient
from machine.handlers.logging import create_scoped_logger
from machine.models.core import RegisteredActions
from machine.models.interactive import (
    Action,
    BlockActionsPayload,
    InteractivePayload,
    ViewClosedPayload,
    ViewSubmissionPayload,
)
from machine.plugins.block_action import BlockAction
from machine.plugins.modals import ModalClosure, ModalSubmission

logger = get_logger(__name__)


def create_interactive_handler(
    plugin_actions: RegisteredActions,
    slack_client: SlackClient,
) -> Callable[[AsyncBaseSocketModeClient, SocketModeRequest], Awaitable[None]]:
    async def handle_interactive_request(client: AsyncBaseSocketModeClient, request: SocketModeRequest) -> None:
        if request.type == "interactive":
            logger.debug("interactive trigger received", payload=request.payload)
            parsed_payload = InteractivePayload.validate_python(request.payload)
            if parsed_payload.type == "block_actions":
                # Acknowledge the request
                response = SocketModeResponse(envelope_id=request.envelope_id)
                await client.send_socket_mode_response(response)
                await handle_block_actions(parsed_payload, plugin_actions, slack_client)
            if parsed_payload.type == "view_submission":
                await handle_view_submission(parsed_payload, request.envelope_id, client, plugin_actions, slack_client)
            if parsed_payload.type == "view_closed":
                # Acknowledge the request
                response = SocketModeResponse(envelope_id=request.envelope_id)
                await client.send_socket_mode_response(response)
                await handle_view_closed(parsed_payload, plugin_actions, slack_client)

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


async def handle_view_submission(
    payload: ViewSubmissionPayload,
    envelope_id: str,
    socket_mode_client: AsyncBaseSocketModeClient,
    plugin_actions: RegisteredActions,
    slack_client: SlackClient,
) -> None:
    handler_funcs = []
    modal_submission_obj = _gen_modal_submission(payload, slack_client)
    for handler in plugin_actions.modal.values():
        if _matches(handler.callback_id_matcher, payload.view.callback_id):
            if "logger" in handler.function_signature.parameters:
                view_submission_logger = create_scoped_logger(
                    handler.class_name,
                    handler.function.__name__,
                    user_id=payload.user.id,
                    user_name=payload.user.name,
                )
                extra_args = {"logger": view_submission_logger}
            else:
                extra_args = {}
            # Check if the handler is a generator. In this case we have an immediate response we can send back
            if handler.is_generator:
                gen_fn = cast(Callable[..., AsyncGenerator[Union[dict, View], None]], handler.function)
                logger.debug("Modal submission handler is generator, returning immediate ack")
                gen = gen_fn(modal_submission_obj, **extra_args)
                # return immediate reponse
                response = await gen.__anext__()
                ack_response = SocketModeResponse(envelope_id=envelope_id, payload=response)
                await socket_mode_client.send_socket_mode_response(ack_response)
                # Now run the rest of the function
                with contextlib.suppress(StopAsyncIteration):
                    await gen.__anext__()
            else:
                logger.debug("Modal submission is regular async function")
                ack_response = SocketModeResponse(envelope_id=envelope_id)
                await socket_mode_client.send_socket_mode_response(ack_response)
                handler_funcs.append(handler.function(modal_submission_obj, **extra_args))
    await asyncio.gather(*handler_funcs)


async def handle_view_closed(
    payload: ViewClosedPayload,
    plugin_actions: RegisteredActions,
    slack_client: SlackClient,
) -> None:
    handler_funcs = []
    modal_submission_obj = _gen_modal_closure(payload, slack_client)
    for handler in plugin_actions.modal_closed.values():
        if _matches(handler.callback_id_matcher, payload.view.callback_id):
            if "logger" in handler.function_signature.parameters:
                view_closure_logger = create_scoped_logger(
                    handler.class_name,
                    handler.function.__name__,
                    user_id=payload.user.id,
                    user_name=payload.user.name,
                )
                extra_args = {"logger": view_closure_logger}
            else:
                extra_args = {}
            handler_funcs.append(handler.function(modal_submission_obj, **extra_args))
    await asyncio.gather(*handler_funcs)


def _matches(matcher: Union[re.Pattern[str], str, None], input_: str) -> bool:
    if matcher is None:
        return True
    if isinstance(matcher, re.Pattern):
        return matcher.match(input_) is not None
    return matcher == input_


def _gen_block_action(payload: BlockActionsPayload, triggered_action: Action, slack_client: SlackClient) -> BlockAction:
    return BlockAction(slack_client, payload, triggered_action)


def _gen_modal_submission(payload: ViewSubmissionPayload, slack_client: SlackClient) -> ModalSubmission:
    return ModalSubmission(slack_client, payload)


def _gen_modal_closure(payload: ViewClosedPayload, slack_client: SlackClient) -> ModalClosure:
    return ModalClosure(slack_client, payload)
