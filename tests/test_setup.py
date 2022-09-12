import pytest

from machine import Machine
from machine.storage.backends.memory import MemoryStorage


@pytest.fixture
def socket_mode_client(mocker):
    socket_mode_client = mocker.patch("machine.core.SocketModeClient", autospec=True)
    socket_mode_client.return_value.socket_mode_request_listeners = []
    return socket_mode_client


@pytest.fixture
def slack_client(mocker):
    socket_mode_client = mocker.patch("machine.core.SlackClient", autospec=True)
    socket_mode_client.return_value.socket_mode_request_listeners = []
    return slack_client


@pytest.fixture
def os_environ(mocker):
    os_environ = mocker.patch("machine.core.os.environ", new={"SM_SETTINGS_MODULE": "tests.local_setup_settings"})
    return os_environ


@pytest.mark.asyncio
async def test_setup(os_environ, socket_mode_client, slack_client):
    m = Machine()
    assert m._settings is None
    await m._setup()
    assert m._settings is not None
    assert m._settings["PLUGINS"] == ["tests.fake_plugins"]
    assert m._settings["SLACK_BOT_TOKEN"] == "xoxb-abc123"
    assert m._settings["SLACK_APP_TOKEN"] == "xapp-abc123"
    assert m._settings["STORAGE_BACKEND"] == "machine.storage.backends.memory.MemoryStorage"
    assert isinstance(m._storage_backend, MemoryStorage)
    assert "manual" in m._storage_backend._storage
