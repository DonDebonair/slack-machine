from __future__ import annotations

import sys
from typing import Any

import pytest
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.web.async_client import AsyncWebClient

from machine.clients.slack import SlackClient, id_for_channel, id_for_user
from machine.models.channel import Channel
from machine.models.user import User

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo
else:
    from backports.zoneinfo import ZoneInfo

# TODO: more tests


@pytest.fixture
def user_dict():
    return {
        "id": "U1",
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
            "email": "john@my-team.org",
        },
    }


@pytest.fixture
def user_dict_no_email():
    return {
        "id": "U1",
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
def user(user_dict):
    return User.model_validate(user_dict)


@pytest.fixture
def channel_dict():
    return {"id": "C1", "created": 0, "is_archived": False, "is_org_shared": False, "name": "channel-1"}


@pytest.fixture
def channel(channel_dict):
    return Channel.model_validate(channel_dict)


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
    mocker.spy(client, "_on_channel_updated")
    return client


def create_req(event: dict[str, Any]) -> SocketModeRequest:
    return SocketModeRequest("events_api", "my_id", {"event": event})


def test_id_for_user(user):
    assert id_for_user(user) == "U1"
    assert id_for_user("U2") == "U2"


def test_id_for_channel(channel):
    assert id_for_channel(channel) == "C1"
    assert id_for_channel("C2") == "C2"


def test_register_handler(slack_client, socket_mode_client):
    assert isinstance(socket_mode_client.socket_mode_request_listeners, list)
    assert len(socket_mode_client.socket_mode_request_listeners) == 0

    async def my_handler(client, req):
        return None

    slack_client.register_handler(my_handler)
    assert len(socket_mode_client.socket_mode_request_listeners) == 1


@pytest.mark.asyncio
async def test_process_users_channels(slack_client, socket_mode_client):
    req = create_req({"type": "foo"})
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()


@pytest.mark.asyncio
async def test_process_users_channels_team_join(slack_client, socket_mode_client, user_dict):
    event = {"type": "team_join", "user": user_dict}
    req = create_req(event)
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()
    slack_client._on_team_join.assert_called_once_with(event)
    assert len(slack_client._users) == 1
    assert "U1" in slack_client._users
    assert slack_client._users["U1"] == User.model_validate(user_dict)
    assert len(slack_client._users_by_email) == 1
    assert "john@my-team.org" in slack_client._users_by_email
    assert slack_client._users_by_email["john@my-team.org"] == User.model_validate(user_dict)


@pytest.mark.asyncio
async def test_process_users_channels_team_join_no_email(slack_client, socket_mode_client, user_dict_no_email):
    event = {"type": "team_join", "user": user_dict_no_email}
    req = create_req(event)
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()
    slack_client._on_team_join.assert_called_once_with(event)
    assert len(slack_client._users) == 1
    assert "U1" in slack_client._users
    assert slack_client._users["U1"] == User.model_validate(user_dict_no_email)
    assert len(slack_client._users_by_email) == 0


@pytest.mark.asyncio
async def test_process_users_channels_user_change(slack_client, socket_mode_client, user_dict):
    event = {"type": "user_change", "user": user_dict}
    req = create_req(event)
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()
    slack_client._on_user_change.assert_called_once_with(event)
    assert len(slack_client._users) == 1
    assert "U1" in slack_client._users
    assert slack_client._users["U1"] == User.model_validate(user_dict)


@pytest.mark.asyncio
async def test_process_users_channels_channel_created(slack_client, socket_mode_client, web_client, channel_dict):
    web_client.conversations_info.return_value = {"channel": channel_dict}
    event = {"type": "channel_created", "channel": channel_dict}
    req = create_req(event)
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()
    slack_client._on_channel_created.assert_called_once_with(event)
    assert len(slack_client._channels) == 1
    assert "C1" in slack_client._channels
    assert slack_client._channels["C1"] == Channel.model_validate(channel_dict)


@pytest.mark.asyncio
async def test_process_users_channels_channel_deleted(slack_client, socket_mode_client, channel):
    slack_client._channels["C1"] = channel
    assert len(slack_client._channels) == 1
    assert "C1" in slack_client._channels
    event = {"type": "channel_deleted", "channel": "C1"}
    req = create_req(event)
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()
    slack_client._on_channel_deleted.assert_called_once_with(event)
    assert len(slack_client._channels) == 0
    assert "C1" not in slack_client._channels


@pytest.mark.asyncio
async def test_process_users_channels_channel_rename(
    slack_client, socket_mode_client, web_client, channel_dict, channel
):
    slack_client._channels["C1"] = channel
    assert len(slack_client._channels) == 1
    assert "C1" in slack_client._channels
    assert slack_client._channels["C1"].name == "channel-1"
    modified_channel = {**channel_dict, **{"name": "channel-2"}}
    web_client.conversations_info.return_value = {"channel": modified_channel}
    event = {"type": "channel_rename", "channel": channel_dict}
    req = create_req(event)
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()
    slack_client._on_channel_updated.assert_called_once_with(event)
    assert len(slack_client._channels) == 1
    assert "C1" in slack_client._channels
    assert slack_client._channels["C1"].name == "channel-2"


@pytest.mark.asyncio
async def test_process_users_channels_channel_archive(
    slack_client, socket_mode_client, web_client, channel_dict, channel
):
    slack_client._channels["C1"] = channel
    assert len(slack_client._channels) == 1
    assert "C1" in slack_client._channels
    assert slack_client._channels["C1"].is_archived is False
    modified_channel = {**channel_dict, **{"is_archived": True}}
    web_client.conversations_info.return_value = {"channel": modified_channel}
    event = {"type": "channel_rename", "channel": "C1"}
    req = create_req(event)
    await slack_client._process_users_channels(socket_mode_client, req)
    socket_mode_client.send_socket_mode_response.assert_called_once()
    slack_client._on_channel_updated.assert_called_once_with(event)
    assert len(slack_client._channels) == 1
    assert "C1" in slack_client._channels
    assert slack_client._channels["C1"].is_archived is True


@pytest.mark.asyncio
async def test_get_user_by_id(slack_client, socket_mode_client, user_dict):
    event = {"type": "team_join", "user": user_dict}
    req = create_req(event)
    await slack_client._process_users_channels(socket_mode_client, req)
    assert slack_client.get_user_by_id("U1") == User.model_validate(user_dict)


@pytest.mark.asyncio
async def test_get_user_by_email(slack_client, socket_mode_client, user_dict):
    event_with_email = {"type": "team_join", "user": user_dict}
    req_with_email = create_req(event_with_email)
    await slack_client._process_users_channels(socket_mode_client, req_with_email)
    assert slack_client.get_user_by_email("john@my-team.org") == User.model_validate(user_dict)
