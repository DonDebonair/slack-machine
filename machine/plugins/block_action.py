from __future__ import annotations

from typing import Any, Optional, Sequence, Union

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
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
    """

    payload: BlockActionsPayload
    triggered_action: Action

    def __init__(self, client: SlackClient, payload: BlockActionsPayload, triggered_action: Action):
        self._client = client
        self.payload = payload  #: blablab
        """The payload that was received by the bot when the action was triggered that this plugin method listens for"""
        self.triggered_action = triggered_action
        """The action that triggered this plugin method"""
        self._webhook_client = AsyncWebhookClient(self.payload.response_url) if self.payload.response_url else None

    @property
    def user(self) -> User:
        """The user that triggered the action

        :return: the user that triggered the action
        """
        return self._client.users[self.payload.user.id]

    @property
    def channel(self) -> Optional[Channel]:
        """The channel the action was triggered in

        :return: the channel the action was triggered in or None if the action was triggered in a modal
        """
        if self.payload.channel is None:
            return None
        return self._client.channels[self.payload.channel.id]

    @property
    def state(self) -> Optional[State]:
        """The state of the block when the action was triggered

        :return: the state of the block when the action was triggered
        """
        return self.payload.state

    @property
    def response_url(self) -> Optional[str]:
        """The response URL for the action

        :return: the response URL for the action or None if the action was triggered in a modal
        """
        return self.payload.response_url

    @property
    def trigger_id(self) -> str:
        """The trigger id associated with the action

        The trigger id can be user ot open a modal

        :return: the trigger id for the action
        """
        return self.payload.trigger_id

    async def say(
        self,
        text: Optional[str] = None,
        attachments: Union[Sequence[Attachment], Sequence[dict[str, Any]], None] = None,
        blocks: Union[Sequence[Block], Sequence[dict[str, Any]], None] = None,
        ephemeral: bool = True,
        replace_original: bool = False,
        delete_original: bool = False,
        **kwargs: Any,
    ) -> Optional[WebhookResponse]:
        """Send a new message to the channel the block action was triggered in

        Send a new message to the channel the block action was triggered in, using the response_url as a webhook.
        If the block action happened in a modal, the response_url will be None and this method will not send a message
        but instead log a warning.
        Allows for rich formatting using [blocks] and/or [attachments] . You can provide blocks
        and attachments as Python dicts or you can use the [convenient classes] that the
        underlying slack client provides.
        This will send an ephemeral message by default, only visible to the user that triggered the action.
        You can set `ephemeral` to `False` to make the message visible to everyone in the channel.
        By default, Slack replaces the original message in which the action was triggered. This method overrides this
        behavior. If you want your message to replace the original, set replace_original to True.
        Any extra kwargs you provide, will be passed on directly to `AsyncWebhookClient.send()`

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenient classes]: https://github.com/slackapi/python-slack-sdk/tree/main/slack/web/classes

        :param text: message text
        :param attachments: optional attachments (see [attachments])
        :param blocks: optional blocks (see [blocks])
        :param ephemeral: `True/False` wether to send the message as an ephemeral message, only
            visible to the user that initiated the action
        :param replace_original: `True/False` whether the message that contains the block from which the action was
            triggered should be replaced by this message
        :param delete_original: `True/False` whether the message that contains the block from which the action was
            triggered should be deleted. No other parameters should be provided.
        :return: Dictionary deserialized from `AsyncWebhookClient.send()`

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
