from __future__ import annotations

import logging
import sys
from datetime import datetime
from typing import Callable, Awaitable, Any

from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web.async_slack_response import AsyncSlackResponse

from machine.models import Channel
from machine.models import User
from machine.utils.datetime import calculate_epoch

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo  # pragma: no cover
else:
    from backports.zoneinfo import ZoneInfo  # pragma: no cover

logger = logging.getLogger(__name__)


def id_for_user(user: User | str) -> str:
    if isinstance(user, User):
        return user.id
    else:
        return user


def id_for_channel(channel: Channel | str) -> str:
    if isinstance(channel, Channel):
        return channel.id
    else:
        return channel


class SlackClient:
    _client: SocketModeClient
    _users: dict[str, User]
    _channels: dict[str, Channel]
    _bot_info: dict[str, Any]
    _tz: ZoneInfo

    def __init__(self, client: SocketModeClient, tz: ZoneInfo):
        self._client = client
        self._users = {}
        self._channels: dict[str, Channel] = {}
        self._tz = tz

    def register_handler(
        self,
        handler: Callable[[AsyncBaseSocketModeClient, SocketModeRequest], Awaitable[None]],
    ) -> None:
        self._client.socket_mode_request_listeners.append(handler)

    async def _process_users_channels(self, _: AsyncBaseSocketModeClient, req: SocketModeRequest) -> None:
        logger.debug("Request of type %s with payload %s", req.type, req.payload)
        if req.type == "events_api":
            # Acknowledge the request
            response = SocketModeResponse(envelope_id=req.envelope_id)
            await self._client.send_socket_mode_response(response)

            event = req.payload["event"]

            # Handle events to update local channel & user caches
            if event["type"] == "team_join":
                await self._on_team_join(event)
            elif event["type"] == "user_change":
                await self._on_user_change(event)
            elif event["type"] == "channel_created":
                await self._on_channel_created(event)
            elif event["type"] == "channel_deleted" or event["type"] == "group_deleted":
                await self._on_channel_deleted(event)
            elif (
                event["type"] == "channel_rename"
                or event["type"] == "group_rename"
                or event["type"] == "channel_archive"
                or event["type"] == "group_archive"
                or event["type"] == "channel_unarchive"
                or event["type"] == "group_unarchive"
            ):
                await self._on_channel_updated(event)
            elif event["type"] == "channel_id_changed":
                await self._on_channel_id_changed(event)
            elif event["type"] == "member_joined_channel":
                await self._on_member_joined_channel(event)

    async def setup(self) -> None:
        # Setup handlers
        # TODO: use partial?
        self.register_handler(lambda client, req: self._process_users_channels(client, req))

        # Get bot info
        auth_info = await self._client.web_client.auth_test()
        self._bot_info = (await self._client.web_client.bots_info(bot=auth_info["bot_id"]))["bot"]
        logger.debug("Bot info: %s", self._bot_info)

        # Build user cache
        # TODO: can we use an async list comprehension here?
        all_users: list[dict[str, Any]] = []
        async for page in await self._client.web_client.users_list(limit=500):
            all_users = all_users + page["members"]
        for u in all_users:
            self._register_user(u)
        logger.debug("Number of users found: %s", len(self._users))
        logger.debug(
            "Users: %s", ", ".join([f"{u.profile.display_name}|{u.profile.real_name}" for u in self._users.values()])
        )

        all_channels: list[dict[str, Any]] = []
        async for page in await self._client.web_client.conversations_list(
            limit=500, types="public_channel,private_channel,mpim,im"
        ):
            all_channels = all_channels + page["channels"]
        for c in all_channels:
            self._register_channel(c)
        logger.debug("Number of channels found: %s", len(self._channels))
        logger.debug("Channels: %s", ", ".join([c.identifier for c in self._channels.values()]))

    def _register_user(self, user_response: dict[str, Any]) -> User:
        user = User.from_api_response(user_response)
        self._users[user.id] = user
        return user

    def _register_channel(self, channel_response: dict[str, Any]) -> Channel:
        channel = Channel.from_api_response(channel_response)
        self._channels[channel.id] = channel
        return channel

    async def _on_team_join(self, event: dict[str, Any]) -> None:
        logger.debug("team_join: %s", event)
        user = self._register_user(event["user"])
        logger.debug("User joined team: %s", user)

    async def _on_user_change(self, event: dict[str, Any]) -> None:
        logger.debug("user_change: %s", event)
        user = self._register_user(event["user"])
        logger.debug("User changed: %s", user)

    async def _on_channel_created(self, event: dict[str, Any]) -> None:
        logger.debug("channel_created: %s", event)
        channel_resp = await self._client.web_client.conversations_info(channel=event["channel"]["id"])
        channel = self._register_channel(channel_resp["channel"])
        logger.debug("Channel created: %s", channel)

    async def _on_channel_updated(self, event: dict[str, Any]) -> None:
        logger.debug(
            "channel_rename/channel_archive/channel_unarchive/group_rename/group_archive/group_unarchive: %s", event
        )
        if isinstance(event["channel"], dict):
            channel_id = event["channel"]["id"]
        else:
            channel_id = event["channel"]
        channel_resp = await self._client.web_client.conversations_info(channel=channel_id)
        channel = self._register_channel(channel_resp["channel"])
        logger.debug("Channel updated: %s", channel)

    async def _on_channel_deleted(self, event: dict[str, Any]) -> None:
        logger.debug("channel_deleted: %s", event)
        channel = self._channels[event["channel"]]
        del self._channels[event["channel"]]
        logger.debug("Channel %s deleted", channel.name)

    async def _on_member_joined_channel(self, event: dict[str, Any]) -> None:
        logger.debug("member_joined_channel: %s", event)
        if event["user"] == self._bot_info["user_id"]:
            channel_id = event["channel"]
            channel_resp = await self._client.web_client.conversations_info(channel=channel_id)
            channel = self._register_channel(channel_resp["channel"])
            logger.debug("Bot joined %s", channel)

    async def _on_channel_id_changed(self, event: dict[str, Any]) -> None:
        logger.debug("channel_id_changed: %s", event)
        channel = self._channels[event["old_channel_id"]]
        self._channels[event["new_channel_id"]] = channel
        del self._channels[event["old_channel_id"]]

    @property
    def users(self) -> dict[str, User]:
        return self._users

    @property
    def channels(self) -> dict[str, Channel]:
        return self._channels

    @property
    def bot_info(self) -> dict[str, Any]:
        return self._bot_info

    async def send(self, channel: Channel | str, text: str | None, **kwargs: Any) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        if "ephemeral_user" in kwargs and kwargs["ephemeral_user"] is not None:
            ephemeral_user_id = id_for_user(kwargs["ephemeral_user"])
            del kwargs["ephemeral_user"]
            return await self._client.web_client.chat_postEphemeral(
                channel=channel_id, user=ephemeral_user_id, text=text, **kwargs
            )
        else:
            return await self._client.web_client.chat_postMessage(channel=channel_id, text=text, **kwargs)

    async def send_scheduled(
        self, when: datetime, channel: Channel | str, text: str, **kwargs: Any
    ) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        scheduled_ts = calculate_epoch(when, self._tz)
        return await self._client.web_client.chat_scheduleMessage(
            channel=channel_id, text=text, post_at=scheduled_ts, **kwargs
        )

    async def react(self, channel: Channel | str, ts: str, emoji: str) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        return await self._client.web_client.reactions_add(name=emoji, channel=channel_id, timestamp=ts)

    async def open_im(self, user: User | str) -> str:
        user_id = id_for_user(user)
        response = await self._client.web_client.conversations_open(users=user_id)
        return response["channel"]["id"]

    async def send_dm(self, user: User | str, text: str | None, **kwargs: Any) -> AsyncSlackResponse:
        user_id = id_for_user(user)
        dm_channel_id = await self.open_im(user_id)

        return await self._client.web_client.chat_postMessage(channel=dm_channel_id, text=text, as_user=True, **kwargs)

    async def send_dm_scheduled(self, when: datetime, user: User | str, text: str, **kwargs: Any) -> AsyncSlackResponse:
        user_id = id_for_user(user)
        dm_channel_id = await self.open_im(user_id)
        scheduled_ts = calculate_epoch(when, self._tz)

        return await self._client.web_client.chat_scheduleMessage(
            channel=dm_channel_id, text=text, as_user=True, post_at=scheduled_ts, **kwargs
        )

    async def pin_message(self, channel: Channel | str, ts: str) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        return await self._client.web_client.pins_add(channel=channel_id, timestamp=ts)

    async def unpin_message(self, channel: Channel | str, ts: str) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        return await self._client.web_client.pins_remove(channel=channel_id, timestamp=ts)
