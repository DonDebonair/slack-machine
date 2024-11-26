from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from slack_sdk.models.views import View
from slack_sdk.web.async_slack_response import AsyncSlackResponse
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
        """The user that invoked the command

        Returns:
            the User that invoked the command
        """
        return self._client.users[self._cmd_payload["user_id"]]

    @property
    def channel(self) -> Channel:
        """The channel the command was invoked in

        Returns:
            the Channel the command was invoked in
        """
        return self._client.channels[self._cmd_payload["channel_id"]]

    @property
    def is_dm(self) -> bool:
        """Whether the command was invoked in a DM

        Returns:
            `True` if the message was _not_ invoked in a channel or group, `False` otherwise
        """
        channel_id = self._cmd_payload["channel_id"]
        return not (channel_id.startswith("C") or channel_id.startswith("G"))

    @property
    def text(self) -> str:
        """The body of the command (i.e. anything after the command itself)

        Returns:
            the body (text) of the command
        """
        return self._cmd_payload["text"]

    @property
    def command(self) -> str:
        """The command that was invoked

        Returns:
            the command that was invoked
        """
        return self._cmd_payload["command"]

    @property
    def response_url(self) -> str:
        """The response url associated with the command

        This is a unique url for this specific command invocation.
        It can be used for sending messages in response to the command.
        This can only be used 5 times within 30 minutes of receiving the payload.

        Returns:
            the response url associated with the command
        """
        return self._cmd_payload["response_url"]

    @property
    def trigger_id(self) -> str:
        """The trigger id associated with the command

        The trigger id can be used to trigger modals

        Note:
            The `trigger_id` is only valid for 3 seconds after the modal was submitted.

            You can use [`open_modal`][machine.plugins.command.Command.open_modal] to open a modal instead of using
            the `trigger_id` directly.

        Returns:
            the trigger id associated with the command
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
        and attachments as Python dicts or you can use the [convenience classes] that the
        underlying slack client provides.
        This will send an ephemeral message by default, only visible to the user that invoked the command.
        You can set `ephemeral` to `False` to make the message visible to everyone in the channel
        Any extra kwargs you provide, will be passed on directly to `AsyncWebhookClient.send()`

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenience classes]: https://github.com/slackapi/python-slack-sdk/tree/main/slack/web/classes

        Args:
            text: message text
            attachments: optional attachments (see [attachments](https://api.slack.com/docs/message-attachments))
            blocks: optional blocks (see [blocks](https://api.slack.com/reference/block-kit/blocks))
            ephemeral: `True/False` wether to send the message as an ephemeral message, only
                visible to the sender of the original message

        Returns:
            Dictionary deserialized from `AsyncWebhookClient.send()`
        """
        response_type = "ephemeral" if ephemeral else "in_channel"

        return await self._webhook_client.send(
            text=text, attachments=attachments, blocks=blocks, response_type=response_type, **kwargs
        )

    async def open_modal(
        self,
        view: dict | View,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Open a modal in response to the command

        Open a modal in response to the command, using the trigger_id that was returned when the command was invoked.
        Any extra kwargs you provide, will be passed on directly to `AsyncWebClient.views_open()`

        Note:
            You have to call this method within 3 seconds of receiving the command payload.

        Args:
            view: the view to open

        Returns:
            Dictionary deserialized from `AsyncWebClient.views_open()`
        """
        return await self._client.open_modal(self.trigger_id, view, **kwargs)
