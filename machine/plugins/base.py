# -*- coding: utf-8 -*-

from aiohttp.web import Application
from asyncblink import signal


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

    def __init__(self, settings, client, storage):
        self._client = client
        self.storage = storage
        self.settings = settings
        self._fq_name = "{}.{}".format(self.__module__, self.__class__.__name__)

    def init(self, http_app: Application):
        """Initialize plugin

        This method can be implemented by concrete plugin classes. It will be called **once**
        for each plugin, when that plugin is first loaded. You can refer to settings via
        ``self.settings``, and access storage through ``self.storage``, but the Slack client has
        not been initialized yet, so you cannot send or process messages during initialization.

        This method can be specified as either synchronous or asynchronous, depending on the needs
        of the plugin.

        :return: None
        """
        pass

    async def get_users(self):
        """Dictionary of all users in the Slack workspace

        :return: a dictionary of all users in the Slack workspace, where the key is the user id and
            the value is a User object (see the source code of `User`_ in the underlying Slack
            client library)

        .. _User: https://github.com/slackapi/python-slackclient/blob/master/slackclient/user.py
        """
        return await self._client.get_users()

    async def get_channels(self):
        """List of all channels in the Slack workspace

        This is a list of all channels in the Slack workspace that the bot is aware of. This
        includes all public channels, all private channels the bot is a member of and all DM
        channels the bot is a member of.

        :return: a list of all channels in the Slack workspace, where each channel is a Channel
            object (see the source code of `Channel`_ in the underlying Slack client library)

        .. _Channel: https://github.com/slackapi/python-slackclient/blob/master/slackclient/channel.py # NOQA
        """
        return await self._client.get_channels()

    def retrieve_bot_info(self):
        """Information about the bot user in Slack

        This will return a dictionary with information about the bot user in Slack that represents
        Slack Machine

        :return: Bot user
        """
        return self._client.retrieve_bot_info()

    def at(self, user: dict):
        """Create a mention of the provided user

        Create a mention of the provided user in the form of ``<@[user_id]>``. This method is
        convenient when you want to include mentions in your message. This method does not send
        a message, but should be used together with methods like
        :py:meth:`~machine.plugins.base.MachineBasePlugin.say`

        :param user: user your want to mention
        :return: user mention
        """
        return self._client.fmt_mention(user["id"])

    async def say(
        self, channel, text, attachments=None, thread_ts=None, ephemeral_user=None
    ):
        """Send a message to a channel using the WebAPI

        Send a message to a channel using the WebAPI. Allows for rich formatting using
        `attachments`_. Can also reply in-thread and send ephemeral messages, visible to only one
        user.
        Ephemeral messages and threaded messages are mutually exclusive, and ``ephemeral_user``
        takes precedence over ``thread_ts``

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param channel: id or name of channel to send message to. Can be public or private (group)
            channel, or DM channel.
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param thread_ts: optional timestamp of thread, to send a message in that thread
        :param ephemeral_user: optional user name or id if the message needs to visible
            to a specific user only
        :return: Dictionary deserialized from `chat.postMessage`_ request, or `chat.postEphemeral`_
            if `ephemeral_user` is True.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        .. _chat.postEphemeral: https://api.slack.com/methods/chat.postEphemeral
        """
        return await self._client.send_webapi(
            channel, text, attachments, thread_ts, ephemeral_user
        )

    def say_scheduled(self, when, channel, text, attachments, ephemeral_user):
        """Schedule a message to a channel and send it using the WebAPI

        This is the scheduled version of
        :py:meth:`~machine.plugins.base.MachineBasePlugin.say_webapi`.
        It behaves the same, but will send the message at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param ephemeral_user: optional user name or id if the message needs to visible
            to a specific user only
        :return: None
        """
        self._client.send_scheduled(when, channel, text, attachments, ephemeral_user)

    async def react(self, channel, ts, emoji):
        """React to a message in a channel

        Add a reaction to a message in a channel. What message to react to, is determined by the
        combination of the channel and the timestamp of the message.

        :param channel: id or name of channel to send message to. Can be public or private (group)
            channel, or DM channel.
        :param ts: timestamp of the message to react to
        :param emoji: what emoji to react with (should be a string, like 'angel', 'thumbsup', etc.)
        :return: Dictionary deserialized from `reactions.add`_ request.

        .. _reactions.add: https://api.slack.com/methods/reactions.add
        """
        return await self._client.react(channel, ts, emoji)

    async def send_dm(self, user, text, attachments=None):
        """Send a Direct Message through the WebAPI

        Send a Direct Message to a user by opening a DM channel and sending a message to it via
        the WebAPI. Allows for rich formatting using
        `attachments`_.

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param user: id or name of the user to send direct message to
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :return: Dictionary deserialized from `chat.postMessage`_ request.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        """
        return self._client.send_dm(user, text, attachments)

    def send_dm_scheduled(self, when, user, text, attachments=None):
        """Schedule a Direct Message and send it using the WebAPI

        This is the scheduled version of
        :py:meth:`~machine.plugins.base.MachineBasePlugin.send_dm_webapi`. It behaves the same, but
        will send the DM at the scheduled time.

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :return: None
        """
        self._client.send_dm_scheduled(when, user, text, attachments)

    def emit(self, event, **kwargs):
        """Emit an event

        Emit an event that plugins can listen for. You can include arbitrary data as keyword
        arguments.

        :param event: name of the event
        :param kwargs: any data you want to emit with the event
        :return: None
        """
        e = signal(event)
        e.send(self, **kwargs)
