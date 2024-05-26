import re

import pytest

from machine.handlers.interactive_handler import _matches, create_interactive_handler
from machine.plugins.block_action import BlockAction
from machine.plugins.modals import ModalClosure, ModalSubmission
from tests.handlers.requests import _gen_block_action_request, _gen_view_closed_request, _gen_view_submission_request


def test_matches():
    assert _matches(None, "my_action_1") is True
    assert _matches("my_action_1", "my_action_1") is True
    assert _matches("my_action_1", "my_action_2") is False
    assert _matches(re.compile("my_action.*"), "my_action_3") is True
    assert _matches(re.compile("my_action.*"), "my_block_4") is False


@pytest.mark.asyncio
async def test_create_interactive_handler_for_block_actions(
    plugin_actions, fake_plugin, socket_mode_client, slack_client
):
    handler = create_interactive_handler(plugin_actions, slack_client)
    request = _gen_block_action_request("my_action_1", "my_block")
    await handler(socket_mode_client, request)
    assert fake_plugin.block_action_function.call_count == 1
    args = fake_plugin.block_action_function.call_args
    assert isinstance(args[0][0], BlockAction)
    assert args[0][0].triggered_action.action_id == "my_action_1"
    assert args[0][0].triggered_action.block_id == "my_block"
    socket_mode_client.send_socket_mode_response.assert_called_once()
    resp = socket_mode_client.send_socket_mode_response.call_args.args[0]
    assert resp.envelope_id == "x"
    assert resp.payload is None


@pytest.mark.asyncio
async def test_create_interactive_handler_for_view_submission(
    plugin_actions, fake_plugin, socket_mode_client, slack_client
):
    handler = create_interactive_handler(plugin_actions, slack_client)
    request = _gen_view_submission_request("my_modal_1")
    await handler(socket_mode_client, request)
    assert fake_plugin.modal_function.call_count == 1
    args = fake_plugin.modal_function.call_args
    assert isinstance(args[0][0], ModalSubmission)
    assert args[0][0].payload.view.callback_id == "my_modal_1"
    socket_mode_client.send_socket_mode_response.assert_called_once()
    resp = socket_mode_client.send_socket_mode_response.call_args.args[0]
    assert resp.envelope_id == "x"
    assert resp.payload is None
    assert fake_plugin.generator_modal_function.call_count == 0


@pytest.mark.asyncio
async def test_create_interactive_handler_for_view_submission_generator(
    plugin_actions, fake_plugin, socket_mode_client, slack_client
):
    handler = create_interactive_handler(plugin_actions, slack_client)
    request = _gen_view_submission_request("my_generator_modal")
    await handler(socket_mode_client, request)
    assert fake_plugin.generator_modal_function.call_count == 1
    args = fake_plugin.generator_modal_function.call_args
    assert isinstance(args[0][0], ModalSubmission)
    assert args[0][0].payload.view.callback_id == "my_generator_modal"
    socket_mode_client.send_socket_mode_response.assert_called_once()
    resp = socket_mode_client.send_socket_mode_response.call_args.args[0]
    assert resp.envelope_id == "x"
    assert resp.payload == {"text": "hello"}
    assert fake_plugin.modal_function.call_count == 0


@pytest.mark.asyncio
async def test_create_interactive_handler_for_view_closed(
    plugin_actions, fake_plugin, socket_mode_client, slack_client
):
    handler = create_interactive_handler(plugin_actions, slack_client)
    request = _gen_view_closed_request("my_modal_2")
    await handler(socket_mode_client, request)
    assert fake_plugin.modal_closed_function.call_count == 1
    args = fake_plugin.modal_closed_function.call_args
    assert isinstance(args[0][0], ModalClosure)
    assert args[0][0].payload.view.callback_id == "my_modal_2"
    socket_mode_client.send_socket_mode_response.assert_called_once()
    resp = socket_mode_client.send_socket_mode_response.call_args.args[0]
    assert resp.envelope_id == "x"
    assert resp.payload is None
    assert fake_plugin.modal_function.call_count == 0
    assert fake_plugin.generator_modal_function.call_count == 0
