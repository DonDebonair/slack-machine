from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence, cast

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from slack_sdk.web.async_slack_response import AsyncSlackResponse

from machine.clients.slack import SlackClient
from machine.models import Channel, User


# TODO: fix docstrings (return types are wrong, replace RST with Markdown)
class Message:
    """A message that was received by the bot

    This class represents a message that was received by the bot and passed to one or more
    plugins. It contains the message (text) itself, and metadata about the message, such as the
    sender of the message, the channel the message was sent to.

    The ``Message`` class also contains convenience methods for replying to the message in the
    right channel, replying to the sender, etc.
    """

    # TODO: create proper class for msg_event
    def __init__(self, client: SlackClient, msg_event: dict[str, Any]):
        self._client = client
        self._msg_event = msg_event

    @property
    def sender(self) -> User:
        """The sender of the message

        :return: the User the message was sent by
        """
        return self._client.users[self._msg_event["user"]]

    @property
    def channel(self) -> Channel:
        """The channel the message was sent to

        :return: the Channel the message was sent to
        """
        return self._client.channels[self._msg_event["channel"]]

    @property
    def is_dm(self) -> bool:
        channel_id = self._msg_event["channel"]
        return not (channel_id.startswith("C") or channel_id.startswith("G"))

    @property
    def text(self) -> str:
        """The body of the actual message

        :return: the body (text) of the actual message
        """
        return self._msg_event["text"]

    @property
    def at_sender(self) -> str:
        """The sender of the message formatted as mention

        :return: a string representation of the sender of the message, formatted as `mention`_,
            to be used in messages

        .. _mention: https://api.slack.com/docs/message-formatting#linking_to_channels_and_users
        """
        return self.sender.fmt_mention()

    async def say(
        self,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        thread_ts: str | None = None,
        ephemeral: bool = False,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Send a new message to the channel the original message was received in

        Send a new message to the channel the original message was received in, using the WebAPI.
        Allows for rich formatting using `blocks`_ and/or `attachments`_. You can provide blocks
        and attachments as Python dicts or you can use the `convenient classes`_ that the
        underlying slack client provides.
        Can also reply to a thread and send an ephemeral message only visible to the sender of the
        original message. Ephemeral messages and threaded messages are mutually exclusive, and
        ``ephemeral`` takes precedence over ``thread_ts``
        Any extra kwargs you provide, will be passed on directly to the `chat.postMessage`_ or
        `chat.postEphemeral`_ request.

        .. _attachments: https://api.slack.com/docs/message-attachments
        .. _blocks: https://api.slack.com/reference/block-kit/blocks
        .. _convenient classes:
            https://github.com/slackapi/python-slackclient/tree/master/slack/web/classes

        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param blocks: optional blocks (see `blocks`_)
        :param thread_ts: optional timestamp of thread, to send a message in that thread
        :param ephemeral: ``True/False`` wether to send the message as an ephemeral message, only
            visible to the sender of the original message
        :return: Dictionary deserialized from `chat.postMessage`_ request, or `chat.postEphemeral`_
            if `ephemeral` is True.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        .. _chat.postEphemeral: https://api.slack.com/methods/chat.postEphemeral
        """
        ephemeral_user = self.sender.id if ephemeral else None

        return await self._client.send(
            self.channel.id,
            text=text,
            attachments=attachments,
            blocks=blocks,
            thread_ts=thread_ts,
            ephemeral_user=ephemeral_user,
            **kwargs,
        )

    async def say_scheduled(
        self,
        when: datetime,
        text: str,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        thread_ts: str | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Schedule a message

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.say`.
        It behaves the same, but will send the message at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param blocks: optional blocks (see `blocks`_)
        :param thread_ts: optional timestamp of thread, to send a message in that thread
        :return: None

        .. _attachments: https://api.slack.com/docs/message-attachments
        .. _blocks: https://api.slack.com/reference/block-kit/blocks
        """
        return await self._client.send_scheduled(
            when,
            self.channel.id,
            text=text,
            attachments=attachments,
            blocks=blocks,
            thread_ts=thread_ts,
            **kwargs,
        )

    async def reply(
        self,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        in_thread: bool = False,
        ephemeral: bool = False,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Reply to the sender of the original message

        Reply to the sender of the original message with a new message, mentioning that user. Rich
        formatting using `blocks`_ and/or `attachments`_ is possible. You can provide blocks
        and attachments as Python dicts or you can use the `convenient classes`_ that the
        underlying slack client provides.
        Can also reply to a thread and send an ephemeral message only visible to the sender of the
        original message. In the case of in-thread response, the sender of the original message
        will not be mentioned. Ephemeral messages and threaded messages are mutually exclusive,
        and ``ephemeral`` takes precedence over ``in_thread``
        Any extra kwargs you provide, will be passed on directly to the `chat.postMessage`_ or
        `chat.postEphemeral`_ request.

        .. _attachments: https://api.slack.com/docs/message-attachments
        .. _blocks: https://api.slack.com/reference/block-kit/blocks
        .. _convenient classes:
            https://github.com/slackapi/python-slackclient/tree/master/slack/web/classes

        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param blocks: optional blocks (see `blocks`_)
        :param in_thread: ``True/False`` wether to reply to the original message in-thread
        :param ephemeral: ``True/False`` wether to send the message as an ephemeral message, only
            visible to the sender of the original message
        :return: Dictionary deserialized from `chat.postMessage`_ request, or `chat.postEphemeral`_
            if `ephemeral` is True.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        .. _chat.postEphemeral: https://api.slack.com/methods/chat.postEphemeral
        """
        if in_thread and not ephemeral:
            return await self.say(text, attachments=attachments, blocks=blocks, thread_ts=self.ts, **kwargs)
        else:
            text = self._create_reply(text)
            return await self.say(text, attachments=attachments, blocks=blocks, ephemeral=ephemeral, **kwargs)

    async def reply_scheduled(
        self,
        when: datetime,
        text: str,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        in_thread: bool = False,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Schedule a reply and send it

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.reply`.
        It behaves the same, but will send the reply at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param blocks: optional blocks (see `blocks`_)
        :param in_thread: ``True/False`` wether to reply to the original message in-thread
        :return: None

        .. _attachments: https://api.slack.com/docs/message-attachments
        .. _blocks: https://api.slack.com/reference/block-kit/blocks
        """
        if in_thread:
            return await self.say_scheduled(
                when, text, attachments=attachments, blocks=blocks, thread_ts=self.ts, **kwargs
            )
        else:
            text = cast(str, self._create_reply(text))
            return await self.say_scheduled(when, text, attachments=attachments, blocks=blocks, **kwargs)

    async def reply_dm(
        self,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Reply to the sender of the original message with a DM

        Reply in a Direct Message to the sender of the original message by opening a DM channel and
        sending a message to it. Allows for rich formatting using `blocks`_ and/or `attachments`_.
        You can provide blocks and attachments as Python dicts or you can use the
        `convenient classes`_ that the underlying slack client provides.
        Any extra kwargs you provide, will be passed on directly to the `chat.postMessage`_ request.

        .. _attachments: https://api.slack.com/docs/message-attachments
        .. _blocks: https://api.slack.com/reference/block-kit/blocks
        .. _convenient classes:
            https://github.com/slackapi/python-slackclient/tree/master/slack/web/classes

        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param blocks: optional blocks (see `blocks`_)
        :return: Dictionary deserialized from `chat.postMessage`_ request.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        """
        return await self._client.send_dm(self.sender.id, text, attachments=attachments, blocks=blocks, **kwargs)

    async def reply_dm_scheduled(
        self,
        when: datetime,
        text: str,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Schedule a DM reply and send it

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.reply_dm`.
        It behaves the same, but will send the DM at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param blocks: optional blocks (see `blocks`_)
        :return: None

        .. _attachments: https://api.slack.com/docs/message-attachments
        .. _blocks: https://api.slack.com/reference/block-kit/blocks
        """
        return await self._client.send_dm_scheduled(
            when, self.sender.id, text=text, attachments=attachments, blocks=blocks, **kwargs
        )

    async def react(self, emoji: str) -> AsyncSlackResponse:
        """React to the original message

        Add a reaction to the original message

        :param emoji: what emoji to react with (should be a string, like 'angel', 'thumbsup', etc.)
        :return: Dictionary deserialized from `reactions.add`_ request.

        .. _reactions.add: https://api.slack.com/methods/reactions.add
        """
        return await self._client.react(self.channel.id, self._msg_event["ts"], emoji)

    def _create_reply(self, text: str | None) -> str | None:
        if not self.is_dm and text is not None:
            return f"{self.at_sender}: {text}"
        else:
            return text

    @property
    def ts(self) -> str:
        """The timestamp of the message

        :return: the timestamp of the message
        """
        return self._msg_event["ts"]

    @property
    def in_thread(self) -> bool:
        """Is message in a thread

        :return: bool
        """
        return "thread_ts" in self._msg_event

    async def pin_message(self) -> AsyncSlackResponse:
        """Pin message

        Pin the current message in the channel it was posted in
        """
        return await self._client.pin_message(self.channel, self.ts)

    def __str__(self) -> str:
        if self.channel.is_im:
            message = f"Message '{self.text}', sent by user @{self.sender.profile.real_name} in DM"
        else:
            message = (
                f"Message '{self.text}', sent by user @{self.sender.profile.real_name} in channel #{self.channel.name}"
            )
        return message

    def __repr__(self) -> str:
        return f"Message(text={self.text!r}, sender={self.sender.profile.real_name!r}, channel={self.channel.name!r})"
