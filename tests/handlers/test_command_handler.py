import pytest

from machine.handlers import create_slash_command_handler
from machine.plugins.command import Command
from tests.handlers.conftest import gen_command_request


def _assert_command(args, command, text):
    # called with 1 positional arg and 0 kw args
    assert len(args[0]) == 1
    assert len(args[1]) == 0
    # assert called with Command
    assert isinstance(args[0][0], Command)
    # assert command equals expected command
    assert args[0][0].command == command
    # assert command text equals expected text
    assert args[0][0].text == text


@pytest.mark.asyncio
async def test_create_slash_command_handler(plugin_actions, fake_plugin, socket_mode_client, slack_client):
    handler = create_slash_command_handler(plugin_actions, slack_client)
    await handler(socket_mode_client, gen_command_request("/test", "foo"))
    assert fake_plugin.command_function.call_count == 1
    args = fake_plugin.command_function.call_args
    _assert_command(args, "/test", "foo")
    socket_mode_client.send_socket_mode_response.assert_called_once()
    resp = socket_mode_client.send_socket_mode_response.call_args.args[0]
    assert resp.envelope_id == "x"
    assert resp.payload is None
    assert fake_plugin.generator_command_function.call_count == 0


@pytest.mark.asyncio
async def test_create_slash_command_handler_generator(plugin_actions, fake_plugin, socket_mode_client, slack_client):
    handler = create_slash_command_handler(plugin_actions, slack_client)
    await handler(socket_mode_client, gen_command_request("/test-generator", "bar"))
    assert fake_plugin.generator_command_function.call_count == 1
    args = fake_plugin.generator_command_function.call_args
    _assert_command(args, "/test-generator", "bar")
    socket_mode_client.send_socket_mode_response.assert_called_once()
    resp = socket_mode_client.send_socket_mode_response.call_args.args[0]
    assert resp.envelope_id == "x"
    # SocketModeResponse will transform a string into a dict with `text` as only key
    assert resp.payload == {"text": "hello"}
    assert fake_plugin.command_function.call_count == 0
