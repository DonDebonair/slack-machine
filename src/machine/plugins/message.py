from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any, cast

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

    The `Message` class also contains convenience methods for replying to the message in the
    right channel, replying to the sender, etc.
    """

    # TODO: create proper class for msg_event
    def __init__(self, client: SlackClient, msg_event: dict[str, Any]):
        self._client = client
        self._msg_event = msg_event

    @property
    def sender(self) -> User:
        """The sender of the message

        Returns:
            the User the message was sent by
        """
        return self._client.users[self._msg_event["user"]]

    @property
    def channel(self) -> Channel:
        """The channel the message was sent to

        Returns:
            the Channel the message was sent to
        """
        return self._client.channels[self._msg_event["channel"]]

    @property
    def is_dm(self) -> bool:
        """Is the message a direct message

        Returns:
            `True` if the message was _not_ sent in a channel or group, `False` otherwise
        """
        channel_id = self._msg_event["channel"]
        return not (channel_id.startswith("C") or channel_id.startswith("G"))

    @property
    def text(self) -> str:
        """The body of the actual message

        Returns:
            the body (text) of the actual message
        """
        return self._msg_event["text"]

    @property
    def at_sender(self) -> str:
        """The sender of the message formatted as mention

        Returns:
            a string representation of the sender of the message, formatted as
                [mention](https://api.slack.com/docs/message-formatting#linking_to_channels_and_users),
                to be used in messages
        """
        return self.sender.fmt_mention()

    @property
    def ts(self) -> str:
        """The timestamp of the message

        Returns:
            the timestamp of the message
        """
        return self._msg_event["ts"]

    @property
    def in_thread(self) -> bool:
        """Is message in a thread

        Returns:
            the message is in a thread
        """
        return "thread_ts" in self._msg_event

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
        Allows for rich formatting using [blocks] and/or [attachments]. You can provide blocks
        and attachments as Python dicts or you can use the [convenience classes] that the
        underlying slack client provides.
        Can also reply to a thread and send an ephemeral message only visible to the sender of the
        original message. Ephemeral messages and threaded messages are mutually exclusive, and
        `ephemeral` takes precedence over `thread_ts`
        Any extra kwargs you provide, will be passed on directly to the [chat.postMessage] or
        [chat.postEphemeral] request.

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenience classes]:
            https://github.com/slackapi/python-slackclient/tree/master/slack/web/classes
        [chat.postMessage]: https://api.slack.com/methods/chat.postMessage
        [chat.postEphemeral]: https://api.slack.com/methods/chat.postEphemeral

        Args:
            text: message text
            attachments: optional attachments (see [attachments](https://api.slack.com/docs/message-attachments))
            blocks: optional blocks (see [blocks](https://api.slack.com/reference/block-kit/blocks))
            thread_ts: optional timestamp of thread, to send a message in that thread
            ephemeral: `True/False` wether to send the message as an ephemeral message, only
                visible to the sender of the original message

        Returns:
            Dictionary deserialized from [chat.postMessage](https://api.slack.com/methods/chat.postMessage) response,
                or [chat.postEphemeral](https://api.slack.com/methods/chat.postEphemeral) if `ephemeral` is True.


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

        This is the scheduled version of [`say()`][machine.plugins.message.Message.say].
        It behaves the same, but will send the message at the scheduled time.

        Args:
            when: when you want the message to be sent, as [`datetime`][datetime.datetime] instance
            text: message text
            attachments: optional attachments (see [attachments](https://api.slack.com/docs/message-attachments))
            blocks: optional blocks (see [blocks](https://api.slack.com/reference/block-kit/blocks))
            thread_ts: optional timestamp of thread, to send a message in that thread

        Returns:
            Dictionary deserialized from [chat.scheduleMessage](https://api.slack.com/methods/chat.scheduleMessage)
                response.
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
        formatting using [blocks] and/or [attachments] is possible. You can provide blocks
        and attachments as Python dicts or you can use the [convenience classes] that the
        underlying slack client provides.
        Can also reply to a thread and send an ephemeral message only visible to the sender of the
        original message. In the case of in-thread response, the sender of the original message
        will not be mentioned. Ephemeral messages and threaded messages are mutually exclusive,
        and `ephemeral` takes precedence over `in_thread`
        Any extra kwargs you provide, will be passed on directly to the [chat.postMessage] or
        [chat.postEphemeral] request.

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenience classes]:
            https://github.com/slackapi/python-slackclient/tree/master/slack/web/classes
        [chat.postMessage]: https://api.slack.com/methods/chat.postMessage
        [chat.postEphemeral]: https://api.slack.com/methods/chat.postEphemeral

        Args:
            text: message text
            attachments: optional attachments (see [attachments](https://api.slack.com/docs/message-attachments))
            blocks: optional blocks (see [blocks](https://api.slack.com/reference/block-kit/blocks)
            in_thread: `True/False` wether to reply to the original message in-thread
            ephemeral: `True/False` wether to send the message as an ephemeral message, only
                visible to the sender of the original message

        Returns:
            Dictionary deserialized from [chat.postMessage](https://api.slack.com/methods/chat.postMessage) response,
                or [chat.postEphemeral](https://api.slack.com/methods/chat.postEphemeral) if `ephemeral` is True.
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

        This is the scheduled version of [`reply()`][machine.plugins.message.Message.reply].
        It behaves the same, but will send the reply at the scheduled time.

        Args:
            when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
            text: message text
            attachments: optional attachments (see [attachments](https://api.slack.com/docs/message-attachments))
            blocks: optional blocks (see [blocks](https://api.slack.com/reference/block-kit/blocks))
            in_thread: `True/False` wether to reply to the original message in-thread

        Returns:
            Dictionary deserialized from [chat.scheduleMessage](https://api.slack.com/methods/chat.scheduleMessage)
                response.
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
        sending a message to it. Allows for rich formatting using [blocks] and/or [attachments].
        You can provide blocks and attachments as Python dicts or you can use the
        [convenience classes] that the underlying slack client provides.
        Any extra kwargs you provide, will be passed on directly to the [chat.postMessage] request.

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenience classes]:
            https://github.com/slackapi/python-slackclient/tree/master/slack/web/classes
        [chat.postMessage]: https://api.slack.com/methods/chat.postMessage

        Args:
            text: message text
            attachments: optional attachments (see [attachments](https://api.slack.com/docs/message-attachments))
            blocks: optional blocks (see [blocks](https://api.slack.com/reference/block-kit/blocks))

        Returns:
            Dictionary deserialized from [chat.postMessage](https://api.slack.com/methods/chat.postMessage) response.
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

        This is the scheduled version of [`reply_dm()`][machine.plugins.message.Message.reply_dm].
        It behaves the same, but will send the DM at the scheduled time.

        Args:
            when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
            text: message text
            attachments: optional attachments (see [attachments](https://api.slack.com/docs/message-attachments))
            blocks: optional blocks (see [blocks](https://api.slack.com/reference/block-kit/blocks))

        Returns:
            Dictionary deserialized from [chat.scheduleMessage](https://api.slack.com/methods/chat.scheduleMessage)
                response.
        """
        return await self._client.send_dm_scheduled(
            when, self.sender.id, text=text, attachments=attachments, blocks=blocks, **kwargs
        )

    async def react(self, emoji: str) -> AsyncSlackResponse:
        """React to the original message

        Add a reaction to the original message

        Args:
            emoji: what emoji to react with (should be a string, like 'angel', 'thumbsup', etc.)

        Returns:
            Dictionary deserialized from [reactions.add](https://api.slack.com/methods/reactions.add) response.
        """
        return await self._client.react(self.channel.id, self._msg_event["ts"], emoji)

    def _create_reply(self, text: str | None) -> str | None:
        if not self.is_dm and text is not None:
            return f"{self.at_sender}: {text}"
        else:
            return text

    async def pin_message(self) -> AsyncSlackResponse:
        """Pin message

        Pin the current message in the channel it was posted in

        Returns:
            Dictionary deserialized from [pins.add](https://api.slack.com/methods/pins.add) response.
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
