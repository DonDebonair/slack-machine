import sys

import pytest
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest

from machine.asyncio.models.user import User, Profile
from machine.asyncio.models.channel import Channel
from machine.asyncio.clients.slack import id_for_channel, id_for_user, SlackClient

from slack_sdk.web.async_client import AsyncWebClient

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo
else:
    from backports.zoneinfo import ZoneInfo

# TODO: more tests


@pytest.fixture
def user(mocker):
    p = mocker.MagicMock(spec=Profile)
    return User(
        id="1",
        team_id="t1",
        name="john",
        deleted=False,
        profile=p,
        is_bot=False,
        is_stranger=False,
        updated=0,
        is_app_user=False,
    )


@pytest.fixture
def user_dict():
    return {
        "id": "1",
        "name": "john",
        "is_bot": False,
        "updated": 0,
        "is_app_user": False,
        "profile": {
            "avatar_hash": "abc",
            "real_name": "John Doe",
            "display_name": "Johnny",
            "real_name_normalized": "John Doe",
            "display_name_normalized": "Johnny",
            "team": "my-team",
        },
    }


@pytest.fixture
def channel(mocker):
    c = mocker.MagicMock(spec=Channel)
    c.id = "c1"
    return c


@pytest.fixture
def web_client(mocker):
    client = mocker.create_autospec(spec=AsyncWebClient, spec_set=True, instance=True)
    return client


@pytest.fixture
def socket_mode_client(mocker, web_client):
    client = mocker.MagicMock(spec=SocketModeClient)
    client.web_client = web_client
    client.socket_mode_request_listeners = []
    return client


@pytest.fixture
def slack_client(mocker, socket_mode_client, web_client):
    utc = ZoneInfo("UTC")
    client = SlackClient(socket_mode_client, utc)
    mocker.spy(client, "_on_team_join")
    mocker.spy(client, "_on_user_change")
    mocker.spy(client, "_on_channel_created")
    mocker.spy(client, "_on_channel_deleted")
    return client


def test_id_for_user(user):
    assert id_for_user(user) == "1"
    assert id_for_user("2") == "2"


def test_id_for_channel(channel):
    assert id_for_channel(channel) == "c1"
    assert id_for_channel("c2") == "c2"


def test_register_handler(slack_client, socket_mode_client):
    assert isinstance(socket_mode_client.socket_mode_request_listeners, list)
    assert len(socket_mode_client.socket_mode_request_listeners) == 0

    async def my_handler(client, req):
        return None

    slack_client.register_handler(my_handler)
    assert len(socket_mode_client.socket_mode_request_listeners) == 1


@pytest.mark.asyncio
async def test_process_users_channels(slack_client, socket_mode_client):
    req = SocketModeRequest("events_api", "my_id", {"event": {"type": "foo"}})
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()


@pytest.mark.asyncio
async def test_process_users_channels_team_join(slack_client, socket_mode_client, user_dict):
    event = {"type": "team_join", "user": user_dict}
    req = SocketModeRequest("events_api", "my_id", {"event": event})
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()
    slack_client._on_team_join.assert_called_once_with(event)
    assert len(slack_client._users) == 1
    assert "1" in slack_client._users
    assert slack_client._users["1"] == User.from_api_response(user_dict)


@pytest.mark.asyncio
async def test_process_users_channels_user_change(slack_client, socket_mode_client, user_dict):
    event = {"type": "user_change", "user": user_dict}
    req = SocketModeRequest("events_api", "my_id", {"event": event})
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()
    slack_client._on_user_change.assert_called_once_with(event)
    assert len(slack_client._users) == 1
    assert "1" in slack_client._users
    assert slack_client._users["1"] == User.from_api_response(user_dict)
