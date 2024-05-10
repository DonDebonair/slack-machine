import pytest
from slack_sdk.socket_mode.request import SocketModeRequest

from machine.handlers import create_generic_event_handler


def _gen_event_request(event_type: str):
    return SocketModeRequest(type="events_api", envelope_id="x", payload={"event": {"type": event_type, "foo": "bar"}})


@pytest.mark.asyncio
async def test_create_generic_event_handler(plugin_actions, fake_plugin, socket_mode_client):
    handler = create_generic_event_handler(plugin_actions)
    await handler(socket_mode_client, _gen_event_request("other_event"))
    assert fake_plugin.process_function.call_count == 0
    await handler(socket_mode_client, _gen_event_request("some_event"))
    assert fake_plugin.process_function.call_count == 1
    args = fake_plugin.process_function.call_args
    assert len(args[0]) == 1
    assert len(args[1]) == 0
    assert args[0][0] == {"type": "some_event", "foo": "bar"}
