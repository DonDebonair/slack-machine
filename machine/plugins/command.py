from __future__ import annotations

from typing import Any, Sequence

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from slack_sdk.webhook import WebhookResponse
from slack_sdk.webhook.async_client import AsyncWebhookClient

from machine.clients.slack import SlackClient
from machine.models import Channel, User


class Command:
    """A Slack command that was received by the bot

    This class represents a Slack command that was received by the bot and passed to a plugin.
    It contains the text that was included when the command was invoked, and metadata about
    the command, such as the user that invoked the command, the channel the command was invoked
    in.

    The `Command` class also contains convenience methods for sending messages in the right
    channel, opening modals etc.
    """

    # TODO: create proper class for cmd_event
    def __init__(self, client: SlackClient, cmd_payload: dict[str, Any]):
        self._client = client
        self._cmd_payload = cmd_payload
        self._webhook_client = AsyncWebhookClient(self._cmd_payload["response_url"])

    @property
    def sender(self) -> User:
        """The sender of the message

        :return: the User the message was sent by
        """
        return self._client.users[self._cmd_payload["user_id"]]

    @property
    def channel(self) -> Channel:
        """The channel the message was sent to

        :return: the Channel the message was sent to
        """
        return self._client.channels[self._cmd_payload["channel_id"]]

    @property
    def is_dm(self) -> bool:
        channel_id = self._cmd_payload["channel_id"]
        return not (channel_id.startswith("C") or channel_id.startswith("G"))

    @property
    def text(self) -> str:
        """The body of the actual message

        :return: the body (text) of the actual message
        """
        return self._cmd_payload["text"]

    @property
    def command(self) -> str:
        """The command that was invoked

        :return: the command that was invoked
        """
        return self._cmd_payload["command"]

    @property
    def response_url(self) -> str:
        """The response url associated with the command

        This is a unique url for this specific command invocation.
        It can be used for sending messages in response to the command.
        This can only be used 5 times within 30 minutes of receiving the payload.

        :return: the response url associated with the command
        """
        return self._cmd_payload["response_url"]

    @property
    def trigger_id(self) -> str:
        """The trigger id associated with the command

        The trigger id can be used to trigger modals

        :return: the trigger id associated with the command
        """
        return self._cmd_payload["trigger_id"]

    async def say(
        self,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        ephemeral: bool = True,
        **kwargs: Any,
    ) -> WebhookResponse:
        """Send a new message to the channel the command was invoked in

        Send a new message to the channel the command was invoked in, using the response_url as a webhook.
        Allows for rich formatting using [blocks] and/or [attachments] . You can provide blocks
        and attachments as Python dicts or you can use the [convenient classes] that the
        underlying slack client provides.
        This will send an ephemeral message by default, only visible to the user that invoked the command.
        You can set `ephemeral` to `False` to make the message visible to everyone in the channel
        Any extra kwargs you provide, will be passed on directly to `AsyncWebhookClient.send()`

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenient classes]: https://github.com/slackapi/python-slack-sdk/tree/main/slack/web/classes

        :param text: message text
        :param attachments: optional attachments (see [attachments])
        :param blocks: optional blocks (see [blocks])
        :param ephemeral: `True/False` wether to send the message as an ephemeral message, only
            visible to the sender of the original message
        :return: Dictionary deserialized from `AsyncWebhookClient.send()`

        """
        response_type = "ephemeral" if ephemeral else "in_channel"

        return await self._webhook_client.send(
            text=text, attachments=attachments, blocks=blocks, response_type=response_type, **kwargs
        )
