import pytest
from structlog.testing import capture_logs

from machine.handlers import log_request
from tests.handlers.conftest import gen_command_request


@pytest.mark.asyncio
async def test_request_logger_handler(socket_mode_client):
    with capture_logs() as cap_logs:
        await log_request(socket_mode_client, gen_command_request("/test", "foo"))
        log_event = cap_logs[0]
        assert log_event["event"] == "Request received"
        assert log_event["type"] == "slash_commands"
        assert log_event["request"] == {
            "envelope_id": "x",
            "payload": {"command": "/test", "text": "foo", "response_url": "https://my.webhook.com"},
        }
