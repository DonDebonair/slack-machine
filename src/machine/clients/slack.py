from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Awaitable
from datetime import datetime
from typing import Any, Callable
from zoneinfo import ZoneInfo

from slack_sdk.errors import SlackApiError
from slack_sdk.models.views import View
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse
from structlog.stdlib import get_logger

from machine.models import Channel, User
from machine.utils.datetime import calculate_epoch

logger = get_logger(__name__)


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
    _users_by_email: dict[str, User]
    _channels: dict[str, Channel]
    _bot_info: dict[str, Any]
    _tz: ZoneInfo

    def __init__(self, client: SocketModeClient, tz: ZoneInfo):
        self._client = client
        self._users = {}
        self._users_by_email = {}
        self._channels: dict[str, Channel] = {}
        self._tz = tz

    @property
    def web_client(self) -> AsyncWebClient:
        return self._client.web_client

    def register_handler(
        self,
        handler: Callable[[AsyncBaseSocketModeClient, SocketModeRequest], Awaitable[None]],
    ) -> None:
        self._client.socket_mode_request_listeners.append(handler)

    async def _process_users_channels(self, _: AsyncBaseSocketModeClient, req: SocketModeRequest) -> None:
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

    async def fetch_paginated_data(
        self,
        client_method: Callable[..., Awaitable[AsyncSlackResponse]],
        data_key: str,
        logger_label: str,
        limit: int = 1000,
        **method_kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        cursor = None
        while True:
            try:
                response = await client_method(limit=limit, cursor=cursor, **method_kwargs)
                items = response[data_key]

                for item in items:
                    yield item

                cursor = (response.get("response_metadata") or {}).get("next_cursor")
                logger.info(f"{len(items)} {logger_label} loaded in this batch.")

                if not cursor:
                    break

            except SlackApiError as e:
                if e.response["error"] == "ratelimited":
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                    logger.warning(f"Slack API rate limit hit. Retrying after {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                else:
                    logger.error(f"Error fetching {logger_label}: {e.response['error']}")
                    raise e

    async def cache_all_users(self) -> None:
        """
        Fetches all users and builds the user cache.

        As of writing the rate limit for the Users List API is 20+ per minute
        (Web API Tier 2). This means if you have more than 20,000 users the
        cache may take over a minute to build.
        """
        async for user in self.fetch_paginated_data(
            client_method=self._client.web_client.users_list,
            data_key="members",
            logger_label="users",
        ):
            self._register_user(user)

        logger.debug("Total users cached: %s", len(self._users))
        logger.debug(
            "Users: %s", ", ".join([f"{u.profile.display_name}|{u.profile.real_name}" for u in self._users.values()])
        )

    async def cache_all_channels(self) -> None:
        """
        Fetches all conversations and builds the channels cache.

        As of writing the rate limit for the Conversations API is 20+ per minute
        (Web API Tier 2). This means if you have more than 20,000 channels the
        cache may take over a minute to build.
        """
        async for channel in self.fetch_paginated_data(
            client_method=self._client.web_client.conversations_list,
            data_key="channels",
            logger_label="channels",
            types="public_channel,private_channel,mpim,im",
        ):
            self._register_channel(channel)

        logger.debug("Total channels cached: %s", len(self._channels))
        logger.debug("Channels: %s", ", ".join([c.identifier for c in self._channels.values()]))

    async def setup(self) -> None:
        # Setup handlers
        # TODO: use partial?
        self.register_handler(lambda client, req: self._process_users_channels(client, req))

        # Get bot info
        auth_info = await self._client.web_client.auth_test()
        self._bot_info = (await self._client.web_client.bots_info(bot=auth_info["bot_id"]))["bot"]
        logger.debug("Bot info: %s", self._bot_info)

        await self.cache_all_users()
        await self.cache_all_channels()

    def _register_user(self, user_response: dict[str, Any]) -> User:
        user = User.model_validate(user_response)
        self._users[user.id] = user
        if user.profile.email is not None:
            self._users_by_email[user.profile.email] = user
        else:
            if not user.is_bot:
                logger.warning("User has not provided an email address in their profile", user=user.model_dump())
        return user

    def _register_channel(self, channel_response: dict[str, Any]) -> Channel:
        channel = Channel.model_validate(channel_response)
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
        channel_id = event["channel"]["id"] if isinstance(event["channel"], dict) else event["channel"]
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
    def users_by_email(self) -> dict[str, User]:
        return self._users_by_email

    @property
    def channels(self) -> dict[str, Channel]:
        return self._channels

    @property
    def bot_info(self) -> dict[str, Any]:
        return self._bot_info

    def get_user_by_id(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        return self._users_by_email.get(email)

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

    async def update(self, channel: Channel | str, ts: str, text: str | None, **kwargs: Any) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        return await self._client.web_client.chat_update(channel=channel_id, ts=ts, text=text, **kwargs)

    async def delete(self, channel: Channel | str, ts: str, **kwargs: Any) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        return await self._client.web_client.chat_delete(channel=channel_id, ts=ts, **kwargs)

    async def react(self, channel: Channel | str, ts: str, emoji: str) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        return await self._client.web_client.reactions_add(name=emoji, channel=channel_id, timestamp=ts)

    async def open_im(self, users: User | str | list[User | str]) -> str:
        user_ids = [id_for_user(user) for user in users] if isinstance(users, list) else id_for_user(users)
        response = await self._client.web_client.conversations_open(users=user_ids)
        return response["channel"]["id"]

    async def send_dm(self, user: User | str, text: str | None, **kwargs: Any) -> AsyncSlackResponse:
        user_id = id_for_user(user)

        return await self._client.web_client.chat_postMessage(channel=user_id, text=text, as_user=True, **kwargs)

    async def send_dm_scheduled(self, when: datetime, user: User | str, text: str, **kwargs: Any) -> AsyncSlackResponse:
        user_id = id_for_user(user)
        scheduled_ts = calculate_epoch(when, self._tz)

        return await self._client.web_client.chat_scheduleMessage(
            channel=user_id, text=text, as_user=True, post_at=scheduled_ts, **kwargs
        )

    async def pin_message(self, channel: Channel | str, ts: str) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        return await self._client.web_client.pins_add(channel=channel_id, timestamp=ts)

    async def unpin_message(self, channel: Channel | str, ts: str) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        return await self._client.web_client.pins_remove(channel=channel_id, timestamp=ts)

    async def set_topic(self, channel: Channel | str, topic: str, **kwargs: Any) -> AsyncSlackResponse:
        channel_id = id_for_channel(channel)
        return await self._client.web_client.conversations_setTopic(channel=channel_id, topic=topic, **kwargs)

    async def open_modal(self, trigger_id: str, view: dict | View, **kwargs: Any) -> AsyncSlackResponse:
        return await self._client.web_client.views_open(trigger_id=trigger_id, view=view, **kwargs)

    async def push_modal(self, trigger_id: str, view: dict | View, **kwargs: Any) -> AsyncSlackResponse:
        return await self._client.web_client.views_push(trigger_id=trigger_id, view=view, **kwargs)

    async def update_modal(
        self,
        view: dict | View,
        view_id: str | None = None,
        external_id: str | None = None,
        hash: str | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        return await self._client.web_client.views_update(
            view=view, view_id=view_id, external_id=external_id, hash=hash, **kwargs
        )

    async def publish_home_tab(
        self, user: User | str, view: dict | View, hash: str | None = None, **kwargs: Any
    ) -> AsyncSlackResponse:
        user_id = id_for_user(user)
        return await self._client.web_client.views_publish(user_id=user_id, view=view, hash=hash, **kwargs)
