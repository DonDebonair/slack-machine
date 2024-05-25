from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse

from machine.clients.slack import SlackClient
from machine.models import Channel, User
from machine.plugins import ee
from machine.storage import PluginStorage
from machine.utils.collections import CaseInsensitiveDict


# TODO: fix docstrings (return types are wrong, replace RST with Markdown)
class MachineBasePlugin:
    """Base class for all Slack Machine plugins

    The purpose of this class is two-fold:

    1. It acts as a marker-class so Slack Machine can recognize plugins as such
    2. It provides a lot of common functionality and convenience methods for plugins to
       interact with channels and users

    :var settings: Slack Machine settings object that contains all settings that
        were defined through ``local_settings.py`` Plugin developers can use any
        settings that are defined by the user, and ask users to add new settings
        specifically for their plugin.
    """

    _client: SlackClient
    storage: PluginStorage
    settings: CaseInsensitiveDict
    _fq_name: str

    def __init__(self, client: SlackClient, settings: CaseInsensitiveDict, storage: PluginStorage):
        self._client = client
        self.storage = storage
        self.settings = settings
        self._fq_name = f"{self.__module__}.{self.__class__.__name__}"

    async def init(self) -> None:
        """Initialize plugin

        This method can be implemented by concrete plugin classes. It will be called **once**
        for each plugin, when that plugin is first loaded. You can refer to settings via
        ``self.settings``, and access storage through ``self.storage``, but the Slack client has
        not been initialized yet, so you cannot send or process messages during initialization.

        :return: None
        """
        return None

    @property
    def users(self) -> dict[str, User]:
        """Dictionary of all users in the Slack workspace

        :return: a dictionary of all users in the Slack workspace, where the key is the user id and
            the value is a [`User`][machine.models.user.User] object
        """
        return self._client.users

    @property
    def users_by_email(self) -> dict[str, User]:
        """Dictionary of all users in the Slack workspace by email

        **Note**: not every user might have an email address in their profile, so this
        dictionary might not contain all users in the Slack workspace

        :return: a dictionary of all users in the Slack workspace, where the key is the email and
            the value is a [`User`][machine.models.user.User] object
        """
        return self._client.users

    @property
    def channels(self) -> dict[str, Channel]:
        """List of all channels in the Slack workspace

        This is a list of all channels in the Slack workspace that the bot is aware of. This
        includes all public channels, all private channels the bot is a member of and all DM
        channels the bot is a member of.

        :return: a list of all channels in the Slack workspace, where each channel is a
            :py:class:`~machine.models.channel.Channel` object
        """
        return self._client.channels

    @property
    def web_client(self) -> AsyncWebClient:
        """Slack SDK web client to access the [Slack Web API][slack-web-api]

        This property references an instance of [`AsyncWebClient`][async-web-client]

        [slack-web-api]: https://api.slack.com/web
        [async-web-client]: https://slack.dev/python-slack-sdk/api-docs/slack_sdk/web/async_client.html#slack_sdk.web.async_client.AsyncWebClient
        """  # noqa: E501
        return self._client.web_client

    def find_channel_by_name(self, channel_name: str) -> Channel | None:
        """Find a channel by its name, irrespective of a preceding pound symbol. This does not include DMs.

        :param channel_name: The name of the channel to retrieve.
        :return: The channel if found, None otherwise.
        """
        if channel_name.startswith("#"):
            channel_name = channel_name[1:]
        for c in self.channels.values():
            if c.name_normalized and channel_name.lower() == c.name_normalized.lower():
                return c
        return None

    def get_user_by_id(self, user_id: str) -> User | None:
        """Get a user by their ID.

        :param user_id: The ID of the user to retrieve.
        :return: The user if found, None otherwise.
        """
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        """Get a user by their email address.

        :param email: The email address of the user to retrieve.
        :return: The user if found, None otherwise.
        """
        return self._client.get_user_by_email(email)

    @property
    def bot_info(self) -> dict[str, Any]:
        """Information about the bot user in Slack

        This will return a dictionary with information about the bot user in Slack that represents
        Slack Machine

        :return: Bot user
        """
        return self._client.bot_info

    def at(self, user: User) -> str:
        """Create a mention of the provided user

        Create a mention of the provided user in the form of ``<@[user_id]>``. This method is
        convenient when you want to include mentions in your message. This method does not send
        a message, but should be used together with methods like
        :py:meth:`~machine.plugins.base.MachineBasePlugin.say`

        :param user: user your want to mention
        :return: user mention
        """
        return user.fmt_mention()

    async def say(
        self,
        channel: Channel | str,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        thread_ts: str | None = None,
        ephemeral_user: User | str | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Send a message to a channel

        Send a message to a channel using the WebAPI. Allows for rich formatting using
        `blocks`_ and/or `attachments`_. You can provide blocks and attachments as Python dicts or
        you can use the `convenient classes`_ that the underlying slack client provides.
        Can also reply in-thread and send ephemeral messages, visible to only one user.
        Ephemeral messages and threaded messages are mutually exclusive, and ``ephemeral_user``
        takes precedence over ``thread_ts``
        Any extra kwargs you provide, will be passed on directly to the `chat.postMessage`_ or
        `chat.postEphemeral`_ request.

        .. _attachments: https://api.slack.com/docs/message-attachments
        .. _blocks: https://api.slack.com/reference/block-kit/blocks
        .. _convenient classes:
            https://github.com/slackapi/python-slackclient/tree/master/slack/web/classes

        :param channel: :py:class:`~machine.models.channel.Channel` object or id of channel to send
            message to. Can be public or private (group) channel, or DM channel.
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param blocks: optional blocks (see `blocks`_)
        :param thread_ts: optional timestamp of thread, to send a message in that thread
        :param ephemeral_user: optional user name or id if the message needs to visible
            to a specific user only
        :return: Dictionary deserialized from `chat.postMessage`_ request, or `chat.postEphemeral`_
            if `ephemeral_user` is True.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        .. _chat.postEphemeral: https://api.slack.com/methods/chat.postEphemeral
        """
        return await self._client.send(
            channel,
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
        channel: Channel | str,
        text: str,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        thread_ts: str | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Schedule a message to a channel

        This is the scheduled version of :py:meth:`~machine.plugins.base.MachineBasePlugin.say`.
        It behaves the same, but will send the message at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param channel: :py:class:`~machine.models.channel.Channel` object or id of channel to send
            message to. Can be public or private (group) channel, or DM channel.
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
            channel,
            text=text,
            attachments=attachments,
            blocks=blocks,
            thread_ts=thread_ts,
            **kwargs,
        )

    async def update(
        self,
        channel: Channel | str,
        ts: str,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        ephemeral_user: User | str | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Update an existing message

        Update an existing message using the WebAPI. Allows for rich formatting using
        [blocks] and/or [attachments]. You can provide blocks and attachments as Python dicts or
        you can use the [convenient classes] that the underlying slack client provides.
        Can also update in-thread and ephemeral messages, visible to only one user.
        Any extra kwargs you provide, will be passed on directly to the [`chat.update`][chat_update] request.

        [attachments]: https://api.slack.com/docs/message-attachments
        [blocks]: https://api.slack.com/reference/block-kit/blocks
        [convenient classes]: https://github.com/slackapi/python-slack-sdk/tree/main/slack/web/classes
        [chat_update]: https://api.slack.com/methods/chat.update

        :param channel: [`Channel`][machine.models.channel.Channel] object or id of channel to send
            message to. Can be public or private (group) channel, or DM channel.
        :param ts: timestamp of the message to be updated.
        :param text: message text
        :param attachments: optional attachments (see [attachments])
        :param blocks: optional blocks (see [blocks])
        :param thread_ts: optional timestamp of thread, to send a message in that thread
        :param ephemeral_user: optional user name or id if the message needs to visible
            to a specific user only
        :return: Dictionary deserialized from [`chat.update`](https://api.slack.com/methods/chat.update) request


        """
        return await self._client.update(
            channel,
            ts=ts,
            text=text,
            attachments=attachments,
            blocks=blocks,
            ephemeral_user=ephemeral_user,
            **kwargs,
        )

    async def delete(
        self,
        channel: Channel | str,
        ts: str,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Delete an existing message

        Delete an existing message using the WebAPI.
        Any extra kwargs you provide, will be passed on directly to the [`chat.delete`][chat_delete] request.

        [chat_delete]: https://api.slack.com/methods/chat.delete

        :param channel: [`Channel`][machine.models.channel.Channel] object or id of channel to send
            message to. Can be public or private (group) channel, or DM channel.
        :param ts: timestamp of the message to be deleted.
        :return: Dictionary deserialized from [`chat.delete`](https://api.slack.com/methods/chat.delete) request


        """
        return await self._client.delete(
            channel,
            ts=ts,
            **kwargs,
        )

    async def react(self, channel: Channel | str, ts: str, emoji: str) -> AsyncSlackResponse:
        """React to a message in a channel

        Add a reaction to a message in a channel. What message to react to, is determined by the
        combination of the channel and the timestamp of the message.

        :param channel: :py:class:`~machine.models.channel.Channel` object or id of channel to send
            message to. Can be public or private (group) channel, or DM channel.
        :param ts: timestamp of the message to react to
        :param emoji: what emoji to react with (should be a string, like 'angel', 'thumbsup', etc.)
        :return: Dictionary deserialized from `reactions.add`_ request.

        .. _reactions.add: https://api.slack.com/methods/reactions.add
        """
        return await self._client.react(channel, ts, emoji)

    async def send_dm(
        self,
        user: User | str,
        text: str | None = None,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Send a Direct Message

        Send a Direct Message to a user by opening a DM channel and sending a message to it. Allows
        for rich formatting using `blocks`_ and/or `attachments`_. You can provide blocks and
        attachments as Python dicts or you can use the `convenient classes`_ that the underlying
        slack client provides.
        Any extra kwargs you provide, will be passed on directly to the `chat.postMessage`_ request.

        .. _attachments: https://api.slack.com/docs/message-attachments
        .. _blocks: https://api.slack.com/reference/block-kit/blocks
        .. _convenient classes:
            https://github.com/slackapi/python-slackclient/tree/master/slack/web/classes

        :param user: :py:class:`~machine.models.user.User` object or id of user to send DM to.
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param blocks: optional blocks (see `blocks`_)
        :return: Dictionary deserialized from `chat.postMessage`_ request.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        """
        return await self._client.send_dm(user, text, attachments=attachments, blocks=blocks, **kwargs)

    async def send_dm_scheduled(
        self,
        when: datetime,
        user: User | str,
        text: str,
        attachments: Sequence[Attachment] | Sequence[dict[str, Any]] | None = None,
        blocks: Sequence[Block] | Sequence[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncSlackResponse:
        """Schedule a Direct Message

        This is the scheduled version of
        :py:meth:`~machine.plugins.base.MachineBasePlugin.send_dm`. It behaves the same, but
        will send the DM at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param user: :py:class:`~machine.models.user.User` object or id of user to send DM to.
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param blocks: optional blocks (see `blocks`_)
        :return: None

        .. _attachments: https://api.slack.com/docs/message-attachments
        .. _blocks: https://api.slack.com/reference/block-kit/blocks
        """
        return await self._client.send_dm_scheduled(
            when, user, text=text, attachments=attachments, blocks=blocks, **kwargs
        )

    def emit(self, event: str, **kwargs: Any) -> None:
        """Emit an event

        Emit an event that plugins can listen for. You can include arbitrary data as keyword
        arguments.

        :param event: name of the event
        :param **kwargs: any data you want to emit with the event
        :return: None
        """
        ee.emit(event, self, **kwargs)

    async def pin_message(self, channel: Channel | str, ts: str) -> AsyncSlackResponse:
        """Pin message

        Pin a message in a channel

        :param channel: channel to pin the message in
        :param ts: timestamp of the message to pin
        :return: response from the Slack Web API
        """
        return await self._client.pin_message(channel, ts)

    async def unpin_message(self, channel: Channel | str, ts: str) -> AsyncSlackResponse:
        """Unpin message

        Unpin a message that was previously pinned in a channel

        :param channel: channel where the message is pinned that needs to be unpinned
        :param ts: timestamp of the message to unpin
        :return: response from the Slack Web API
        """
        return await self._client.unpin_message(channel, ts)

    async def set_topic(self, channel: Channel | str, topic: str, **kwargs: Any) -> AsyncSlackResponse:
        """Set channel topic

        Set or update topic for the channel

        :param channel: channel where topic needs to be set or updated
        :param topic: topic for the channel (slack does not support formatting for topics)
        :return: response from the Slack Web API
        """
        return await self._client.set_topic(channel, topic, **kwargs)
