from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Union

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from slack_sdk.models.views import View
from slack_sdk.web.async_slack_response import AsyncSlackResponse
from slack_sdk.webhook import WebhookResponse
from slack_sdk.webhook.async_client import AsyncWebhookClient
from structlog.stdlib import get_logger

from machine.clients.slack import SlackClient
from machine.models import Channel, User
from machine.models.interactive import Action, BlockActionsPayload, State

logger = get_logger(__name__)


class BlockAction:
    """A Slack block action that was received by the bot

    This class represents a block action that was received by the bot and passed to a plugin.
    Block actions are actions that are triggered by interactions with blocks in Slack messages and modals.
    This class contains metadata about the block action, such as the action that happened that triggered this handler,
    the user that triggered the action, the state of the block when the action was triggered, the payload that was
    received when the action was triggered.

    Attributes:
        payload: The payload that was received by the bot when the action was triggered that this
            plugin method listens for
        triggered_action: The action that triggered this plugin method
    """

    payload: BlockActionsPayload
    triggered_action: Action

    def __init__(self, client: SlackClient, payload: BlockActionsPayload, triggered_action: Action):
        self._client = client
        self.payload = payload
        """The payload that was received by the bot when the action was triggered that this plugin method listens for"""
        self.triggered_action = triggered_action
        """The action that triggered this plugin method"""
        self._webhook_client = AsyncWebhookClient(self.payload.response_url) if self.payload.response_url else None

    @property
    def user(self) -> User:
        """The user that triggered the action

        Returns:
            the user that triggered the action
        """
        return self._client.users[self.payload.user.id]

    @property
    def channel(self) -> Channel | None:
        """The channel the action was triggered in

        Returns:
            the channel the action was triggered in or None if the action was triggered in a modal
        """
        if self.payload.channel is None:
            return None
        return self._client.channels[self.payload.channel.id]

    @property
    def state(self) -> State | None:
        """The state of the block when the action was triggered

        Returns:
            the state of the block when the action was triggered
        """
        return self.payload.state

    @property
    def response_url(self) -> str | None:
        """The response URL for the action

        Returns:
            the response URL for the action or `None` if the action was triggered in a modal
        """
        return self.payload.response_url

    @property
    def trigger_id(self) -> str:
        """The trigger id associated with the action

        The trigger id can be used to open a modal

        Note:
            The `trigger_id` is only valid for 3 seconds after the modal was submitted.

            You can use [`open_modal`][machine.plugins.block_action.BlockAction.open_modal] to open a modal instead of
            using the `trigger_id` directly.

        Returns:
            the trigger id for the action
        """
        return self.payload.trigger_id

    async def say(
        self,
        text: str | None = None,
        attachments: Union[Sequence[Attachment], Sequence[dict[str, Any]], None] = None,
        blocks: Union[Sequence[Block], Sequence[dict[str, Any]], None] = None,
        ephemeral: bool = True,
        replace_original: bool = False,
        delete_original: bool = False,
        **kwargs: Any,
    ) -> WebhookResponse | None:
        """Send a new message to the channel the block action was triggered in

        Send a new message to the channel the block action was triggered in, using the response_url as a webhook.
        If the block action happened in a modal, the response_url will be None and this method will not send a message
        but instead log a warning.
        Allows for rich formatting using [blocks] and/or [attachments]. You can provide blocks
        and attachments as Python dicts or you can use the [convenience classes] that the
        underlying slack client provides.
        This will send an ephemeral message by default, only visible to the user that triggered the action.
        You can set `ephemeral` to `False` to make the message visible to everyone in the channel.
        By default, Slack replaces the original message in which the action was triggered. This method overrides this
        behavior. If you want your message to replace the original, set replace_original to True.
        Any extra kwargs you provide, will be passed on directly to `AsyncWebhookClient.send()`

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenience classes]: https://github.com/slackapi/python-slack-sdk/tree/main/slack/web/classes

        Args:
            text: message text
            attachments: optional attachments (see [attachments](https://api.slack.com/docs/message-attachments))
            blocks: optional blocks (see [blocks](https://api.slack.com/docs/message-attachments))
            ephemeral: `True/False` wether to send the message as an ephemeral message, only
                visible to the user that initiated the action
            replace_original: `True/False` whether the message that contains the block from which the action was
                triggered should be replaced by this message
            delete_original: `True/False` whether the message that contains the block from which the action was
                triggered should be deleted. No other parameters should be provided.

        Returns:
            Dictionary deserialized from `AsyncWebhookClient.send()`

        """
        if self._webhook_client is None:
            logger.warning(
                "response_url is None, cannot send message. This likely means the action was triggered in a modal."
            )
            return None

        response_type = "ephemeral" if ephemeral else "in_channel"
        return await self._webhook_client.send(
            text=text,
            attachments=attachments,
            blocks=blocks,
            response_type=response_type,
            replace_original=replace_original,
            delete_original=delete_original,
            **kwargs,
        )

    async def send_dm(
        self,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Send a DM to the user that triggered the block action

        Send a Direct Message to the user that triggered the block action by opening a DM channel and
        sending a message to it.
        Allows for rich formatting using [blocks] and/or [attachments]. You can provide blocks
        and attachments as Python dicts or you can use the [convenience classes] that the
        underlying slack client provides.
        Any extra kwargs you provide, will be passed on directly to the `chat.postMessage` request.

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenience classes]: https://github.com/slackapi/python-slack-sdk/tree/main/slack/web/classes

        Args:
            text: message text
            attachments: optional attachments (see [attachments](https://api.slack.com/docs/message-attachments))
            blocks: optional blocks (see [blocks](https://api.slack.com/reference/block-kit/blocks))

        Returns:
            Dictionary deserialized from [chat.postMessage](https://api.slack.com/methods/chat.postMessage) response.
        """
        return await self._client.send_dm(self.user.id, text, attachments=attachments, blocks=blocks, **kwargs)

    async def open_modal(
        self,
        view: dict | View,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Open a modal in response to the block action

        Open a modal in response to the block action, using the trigger_id that was returned when the block action was
        triggered.
        Any extra kwargs you provide, will be passed on directly to
        [views.open](https://api.slack.com/methods/views.open)

        Note:
            You have to call this method within 3 seconds of receiving the block action payload.

        Args:
            view: the view to open

        Returns:
            Dictionary deserialized from [views.open](https://api.slack.com/methods/views.open)
        """
        return await self._client.open_modal(self.trigger_id, view, **kwargs)
