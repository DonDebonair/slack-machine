# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional, Sequence

from async_lru import alru_cache
from slack.web.slack_response import SlackResponse

from machine.singletons import Scheduler, Slack
from machine.utils.aio import run_coro_until_complete


class MessagingClient:
    @staticmethod
    def retrieve_bot_info() -> Optional[dict]:
        return Slack.get_instance().login_data.get("self")

    @staticmethod
    async def send(
        channel_id: str,
        text: str,
        *,
        attachments: Optional[Sequence[dict]] = None,
        thread_ts: Optional[str] = None,
        ephemeral_user: Optional[str] = None,
    ) -> SlackResponse:
        method = "chat.postEphemeral" if ephemeral_user else "chat.postMessage"
        payload = {
            "channel": channel_id,
            "text": text,
            "blocks": attachments,
            "as_user": True,
        }

        if ephemeral_user:
            payload["user"] = ephemeral_user
        else:
            if thread_ts:
                payload["thread_ts"] = thread_ts

        return await Slack.get_instance().web.api_call(method, json=payload)

    @staticmethod
    async def react(channel_id: str, ts: str, emoji: str) -> SlackResponse:
        payload = {"name": emoji, "channel": channel_id, "timestamp": ts}

        return await Slack.get_instance().web.api_call("reactions.add", json=payload)

    @staticmethod
    async def open_im(user_id: str) -> str:
        response = await Slack.get_instance().web.api_call(
            "im.open", json={"user": user_id}
        )
        return response["channel"]["id"]

    @property
    def channels(self) -> SlackResponse:
        return run_coro_until_complete(self.get_channels())

    @property
    def users(self) -> SlackResponse:
        return run_coro_until_complete(self.get_users())

    async def get_channels(self) -> SlackResponse:
        return await Slack.get_instance().web.channels_list()

    @alru_cache(maxsize=32)
    async def find_channel_by_id(self, channel_id: str) -> Optional[dict]:
        for channel in (await self.get_channels())["channels"]:
            if channel["id"] == channel_id:
                return channel

        return None

    async def get_users(self) -> SlackResponse:
        return await Slack.get_instance().web.users_list()

    @alru_cache(maxsize=32)
    async def find_user_by_id(self, user_id: str) -> Optional[dict]:
        user_response = await Slack.get_instance().web.users_info(user=user_id)
        return user_response.get("user")

    def fmt_mention(self, user: dict) -> str:
        return f"<@{user['id']}>"

    def send_scheduled(self, when: datetime, channel_id: str, text: str, **kwargs):
        args = [channel_id, text]
        Scheduler.get_instance().add_job(
            MessagingClient.send,
            trigger="date",
            args=args,
            kwargs=kwargs,
            run_date=when,
        )

    async def send_dm(self, user_id: str, text: str, **kwargs) -> SlackResponse:
        dm_channel = await self.open_im(user_id)
        return await self.send(dm_channel, text=text, **kwargs)

    def send_dm_scheduled(self, when: datetime, user_id: str, text: str, **kwargs):
        args = [self, user_id, text]
        Scheduler.get_instance().add_job(
            MessagingClient.send_dm,
            trigger="date",
            args=args,
            kwargs=kwargs,
            run_date=when,
        )
