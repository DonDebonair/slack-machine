from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from slack_sdk.models.views import View as SlackSDKView
from slack_sdk.web.async_slack_response import AsyncSlackResponse

from machine.clients.slack import SlackClient
from machine.models import User
from machine.models.interactive import View, ViewClosedPayload, ViewSubmissionPayload


class ModalSubmission:
    """A Slack modal submission that was received by the bot

    This class represents a modal submission that was received by the bot and passed to a plugin.

    Attributes:
        payload: The payload that was received by the bot when the modal was submitted
    """

    payload: ViewSubmissionPayload

    def __init__(self, client: SlackClient, payload: ViewSubmissionPayload):
        self._client = client
        self.payload = payload

    @property
    def user(self) -> User:
        """The user that submitted the modal

        Returns:
            the user that submitted the modal
        """
        return self._client.users[self.payload.user.id]

    @property
    def view(self) -> View:
        """The view that was submitted including the state of all the elements in the view

        Returns:
            the view that was submitted
        """
        return self.payload.view

    @property
    def trigger_id(self) -> str:
        """The trigger id associated with the submitted modal

        The trigger id can be used to open another modal

        Note:
            The trigger id is only valid for 3 seconds after the modal was submitted.

            You can use [`open_modal()`][machine.plugins.modals.ModalSubmission.open_modal] to open a modal instead of
            using the `trigger_id` directly.

        Returns:
            the trigger id for the modal
        """
        return self.payload.trigger_id

    async def open_modal(
        self,
        view: dict | SlackSDKView,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Open another modal in response to the modal submission

        Open another modal in response to modal submission, using the trigger_id that was returned when the modal was
        submitted.
        Any extra kwargs you provide, will be passed on directly to
        [views.open](https://api.slack.com/methods/views.open)

        Note:
            You have to call this method within 3 seconds of receiving the modal submission payload.

        Args:
            view: the view to open

        Returns:
            Dictionary deserialized from [views.open](https://api.slack.com/methods/views.open)
        """
        return await self._client.open_modal(self.trigger_id, view, **kwargs)

    async def push_modal(
        self,
        view: dict | SlackSDKView,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Push a new modal view in response to the modal submission

        Push a new modal view on top of the view stack in response to modal submission, using the trigger_id that was
        returned when the modal was submitted.
        Any extra kwargs you provide, will be passed on directly to
        [views.push](https://api.slack.com/methods/views.push)

        Note:
            You have to call this method within 3 seconds of receiving the modal submission payload.

        Args:
            view: the view to push

        Returns:
            Dictionary deserialized from [views.push](https://api.slack.com/methods/views.push)
        """
        return await self._client.push_modal(self.trigger_id, view, **kwargs)

    async def update_modal(
        self,
        view: dict | SlackSDKView,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Update the modal view in response to the modal submission

        Update the modal view in response to modal submission, using the trigger_id that was returned when the modal was
        submitted.
        Any extra kwargs you provide, will be passed on directly to
        [views.update](https://api.slack.com/methods/views.update)

        Note:
            You have to call this method within 3 seconds of receiving the modal submission payload.

        Args:
            view: the view to update

        Returns:
            Dictionary deserialized from [views.update](https://api.slack.com/methods/views.update)
        """
        return await self._client.update_modal(view, self.payload.view.id, self.payload.view.external_id, **kwargs)

    async def send_dm(
        self,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Send a DM to the user that submitted the modal

        Send a Direct Message to the user that submitted the modal by opening a DM channel and
        sending a message to it.
        Allows for rich formatting using [blocks] and/or [attachments] . You can provide blocks
        and attachments as Python dicts or you can use the [convenience classes] that the
        underlying slack client provides.
        Any extra kwargs you provide, will be passed on directly to the
        [chat.postMessage](https://api.slack.com/methods/chat.postMessage) request.

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


class ModalClosure:
    """A Slack modal closure that was received by the bot

    This class represents the closure (cancellation) of a modal that was received by the bot and passed to a plugin.

    Attributes:
        payload: The payload that was received by the bot when the modal was closed
    """

    payload: ViewClosedPayload

    def __init__(self, client: SlackClient, payload: ViewClosedPayload):
        self._client = client
        self.payload = payload

    @property
    def user(self) -> User:
        """The user that closed the modal

        Returns:
            the user that closed the modal
        """
        return self._client.users[self.payload.user.id]

    @property
    def view(self) -> View:
        """The view that was closed including the state of all the elements in the view when it was closed

        Returns:
            the view that was closed
        """
        return self.payload.view

    async def send_dm(
        self,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Send a DM to the user that closed the modal

        Send a Direct Message to the user that closed the modal by opening a DM channel and
        sending a message to it.
        Allows for rich formatting using [blocks] and/or [attachments] . You can provide blocks
        and attachments as Python dicts or you can use the [convenience classes] that the
        underlying slack client provides.
        Any extra kwargs you provide, will be passed on directly to the
        [chat.postMessage](https://api.slack.com/methods/chat.postMessage) request.

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
