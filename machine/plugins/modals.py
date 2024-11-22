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
    payload: ViewSubmissionPayload

    def __init__(self, client: SlackClient, payload: ViewSubmissionPayload):
        self._client = client
        self.payload = payload

    @property
    def user(self) -> User:
        """The user that submitted the modal

        :return: the user that submitted the modal
        """
        return self._client.users[self.payload.user.id]

    @property
    def view(self) -> View:
        """The view that was submitted including the state of all the elements in the view

        :return: the view that was submitted
        """
        return self.payload.view

    @property
    def trigger_id(self) -> str:
        """The trigger id associated with the submitted modal

        The trigger id can be user ot open another modal

        :return: the trigger id for the modal
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
        Any extra kwargs you provide, will be passed on directly to `AsyncWebClient.views_open()`

        Note: you have to call this method within 3 seconds of receiving the modal submission payload.

        :param view: the view to open
        :return: Dictionary deserialized from `AsyncWebClient.views_open()`
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
        Any extra kwargs you provide, will be passed on directly to `AsyncWebClient.views_push()`

        Note: you have to call this method within 3 seconds of receiving the modal submission payload.

        :param view: the view to push
        :return: Dictionary deserialized from `AsyncWebClient.views_push()`
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
        Any extra kwargs you provide, will be passed on directly to `AsyncWebClient.views_update()`

        Note: you have to call this method within 3 seconds of receiving the modal submission payload.

        :param view: the view to update
        :return: Dictionary deserialized from `AsyncWebClient.views_update()`
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
        and attachments as Python dicts or you can use the [convenient classes] that the
        underlying slack client provides.
        Any extra kwargs you provide, will be passed on directly to the `chat.postMessage` request.

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenient classes]: https://github.com/slackapi/python-slack-sdk/tree/main/slack/web/classes

        :param text: message text
        :param attachments: optional attachments (see [attachments])
        :param blocks: optional blocks (see [blocks])
        :return: Dictionary deserialized from [chat.postMessage] response.

        [chat.postMessage]: https://api.slack.com/methods/chat.postMessage
        """
        return await self._client.send_dm(self.user.id, text, attachments=attachments, blocks=blocks, **kwargs)


class ModalClosure:
    payload: ViewClosedPayload

    def __init__(self, client: SlackClient, payload: ViewClosedPayload):
        self._client = client
        self.payload = payload

    @property
    def user(self) -> User:
        """The user that closed the modal

        :return: the user that closed the modal
        """
        return self._client.users[self.payload.user.id]

    @property
    def view(self) -> View:
        """The view that was closed including the state of all the elements in the view when it was closed

        :return: the view that was closed
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
        and attachments as Python dicts or you can use the [convenient classes] that the
        underlying slack client provides.
        Any extra kwargs you provide, will be passed on directly to the `chat.postMessage` request.

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenient classes]: https://github.com/slackapi/python-slack-sdk/tree/main/slack/web/classes

        :param text: message text
        :param attachments: optional attachments (see [attachments])
        :param blocks: optional blocks (see [blocks])
        :return: Dictionary deserialized from [chat.postMessage] response.

        [chat.postMessage]: https://api.slack.com/methods/chat.postMessage
        """
        return await self._client.send_dm(self.user.id, text, attachments=attachments, blocks=blocks, **kwargs)
