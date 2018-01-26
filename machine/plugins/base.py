from blinker import signal


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

    def init(self):
        """Initialize plugin

        This method can be implemented by concrete plugin classes. It will be called **once**
        for each plugin, when that plugin is first loaded. You can refer to settings via
        ``self.settings``, and access storage through ``self.storage``, but the Slack client has
        not been initialized yet, so you cannot send or process messages during initialization.

        :return: None
        """
        pass

    @property
    def users(self):
        """Dictionary of all users in the Slack workspace

        :return: a dictionary of all users in the Slack workspace, where the key is the user id and
            the value is a User object (see the source code of `User`_ in the underlying Slack
            client library)

        .. _User: https://github.com/slackapi/python-slackclient/blob/master/slackclient/user.py
        """
        return self._client.users

    @property
    def channels(self):
        """List of all channels in the Slack workspace

        This is a list of all channels in the Slack workspace that the bot is aware of. This
        includes all public channels, all private channels the bot is a member of and all DM
        channels the bot is a member of.

        :return: a list of all channels in the Slack workspace, where each channel is a Channel
            object (see the source code of `Channel`_ in the underlying Slack client library)

        .. _Channel: https://github.com/slackapi/python-slackclient/blob/master/slackclient/channel.py # NOQA
        """
        return self._client.channels

    def retrieve_bot_info(self):
        """Information about the bot user in Slack

        This will return a dictionary with information about the bot user in Slack that represents
        Slack Machine

        :return: Bot user
        """
        return self._client.retrieve_bot_info()

    def at(self, user):
        """Create a mention of the provided user

        Create a mention of the provided user in the form of ``<@[user_id]>``. This method is
        convenient when you want to include mentions in your message. This method does not send
        a message, but should be used together with methods like
        :py:meth:`~machine.plugins.base.MachineBasePlugin.say`

        :param user: user your want to mention
        :return: user mention
        """
        return self._client.fmt_mention(user)

    def say(self, channel, text, thread_ts=None):
        """Send a message to a channel

        Send a message to a channel using the RTM API. Only `basic Slack formatting`_ allowed.
        For richer formatting using attachments, use
        :py:meth:`~machine.plugins.base.MachineBasePlugin.say_webapi`

        .. _basic Slack formatting: https://api.slack.com/docs/message-formatting

        :param channel: id or name of channel to send message to. Can be public or private (group)
            channel, or DM channel.
        :param text: message text
        :param thread_ts: optional timestamp of thread, to send a message in that thread
        :return: None
        """
        self._client.send(channel, text, thread_ts)

    def say_scheduled(self, when, channel, text):
        """Schedule a message to a channel

        This is the scheduled version of
        :py:meth:`~machine.plugins.base.MachineBasePlugin.say`.
        It behaves the same, but will send the message at the scheduled time.


        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param channel: id or name of channel to send message to. Can be public or private (group)
            channel, or DM channel.
        :param text: message text
        :return: None
        """
        self._client.send_scheduled(when, channel, text)

    def say_webapi(self, channel, text, attachments=None, thread_ts=None, ephemeral_user=None):
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
        return self._client.send_webapi(channel, text, attachments, thread_ts, ephemeral_user)

    def say_webapi_scheduled(self, when, channel, text, attachments, ephemeral_user):
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
        self._client.send_webapi_scheduled(when, channel, text, attachments, ephemeral_user)

    def react(self, channel, ts, emoji):
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
        return self._client.react(channel, ts, emoji)

    def send_dm(self, user, text):
        """Send a Direct Message

        Send a Direct Message to a user by opening a DM channel and sending a message to it.
        Only `basic Slack formatting`_ allowed. For richer formatting using attachments, use
        :py:meth:`~machine.plugins.base.MachineBasePlugin.send_dm_webapi`

        .. _basic Slack formatting: https://api.slack.com/docs/message-formatting

        :param user: id or name of the user to send direct message to
        :param text: message text
        :return: None
        """
        self._client.send_dm(user, text)

    def send_dm_scheduled(self, when, user, text):
        """Schedule a Direct Message

        This is the scheduled version of
        :py:meth:`~machine.plugins.base.MachineBasePlugin.send_dm`. It behaves the same, but will
        send the DM at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param user: id or name of the user to send direct message to
        :param text: message text
        :return: None
        """
        self._client.send_dm_scheduled(when, user, text)

    def send_dm_webapi(self, user, text, attachments=None):
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
        return self._client.send_dm_webapi(user, text, attachments)

    def send_dm_webapi_scheduled(self, when, user, text, attachments=None):
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
        self._client.send_dm_webapi_scheduled(when, user, text, attachments)

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


class Message:
    """A message that was received by the bot

    This class represents a message that was received by the bot and passed to one or more
    plugins. It contains the message (text) itself, and metadata about the message, such as the
    sender of the message, the channel the message was sent to.

    The ``Message`` class also contains convenience methods for replying to the message in the
    right channel, replying to the sender, etc.
    """

    def __init__(self, client, msg_event, plugin_class_name):
        self._client = client
        self._msg_event = msg_event
        self._fq_plugin_name = plugin_class_name

    @property
    def sender(self):
        """The sender of the message

        :return: the User the message was sent by
        """
        return self._client.users.find(self._msg_event['user'])

    @property
    def channel(self):
        """The channel the message was sent to

        :return: the Channel the message was sent to
        """
        return self._client.channels.find(self._msg_event['channel'])

    @property
    def is_dm(self):
        chan = self._msg_event['channel']
        return not (chan.startswith('C') or chan.startswith('G'))

    @property
    def text(self):
        """The body of the actual message

        :return: the body (text) of the actual message
        """
        return self._msg_event['text']

    @property
    def at_sender(self):
        """The sender of the message formatted as mention

        :return: a string representation of the sender of the message, formatted as `mention`_,
            to be used in messages

        .. _mention: https://api.slack.com/docs/message-formatting#linking_to_channels_and_users
        """
        return self._client.fmt_mention(self.sender)

    def say(self, text, thread_ts=None):
        """Send a new message to the channel the original message was received in

        Send a new message to the channel the original message was received in, using the RTM API.
        Only `basic Slack formatting`_ allowed. For richer formatting using attachments, use
        :py:meth:`~machine.plugins.base.Message.say_webapi`

        .. _basic Slack formatting: https://api.slack.com/docs/message-formatting

        :param text: message text
        :param thread_ts: optional timestamp of thread, to send a message in that thread
        :return: None
        """
        self._client.send(self.channel.id, text, thread_ts)

    def say_scheduled(self, when, text):
        """Schedule a message

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.say`.
        It behaves the same, but will send the message at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :return: None
        """
        self._client.send_scheduled(when, self.channel.id, text)

    def say_webapi(self, text, attachments=None, thread_ts=None, ephemeral=False):
        """Send a new message using the WebAPI to the channel the original message was received in

        Send a new message to the channel the original message was received in, using the WebAPI.
        Allows for rich formatting using `attachments`_. Can also reply to a thread and send an
        ephemeral message only visible to the sender of the original message.
        Ephemeral messages and threaded messages are mutually exclusive, and ``ephemeral``
        takes precedence over ``thread_ts``

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param thread_ts: optional timestamp of thread, to send a message in that thread
        :param ephemeral: ``True/False`` wether to send the message as an ephemeral message, only
            visible to the sender of the original message
        :return: Dictionary deserialized from `chat.postMessage`_ request, or `chat.postEphemeral`_
            if `ephemeral` is True.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        .. _chat.postEphemeral: https://api.slack.com/methods/chat.postEphemeral
        """
        if ephemeral:
            ephemeral_user = self.sender.id
        else:
            ephemeral_user = None

        return self._client.send_webapi(
            self.channel.id,
            text,
            attachments,
            thread_ts,
            ephemeral_user,
        )

    def say_webapi_scheduled(self, when, text, attachments=None, ephemeral=False):
        """Schedule a message and send it using the WebAPI

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.say_webapi`.
        It behaves the same, but will send the DM at the scheduled time.

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param ephemeral: ``True/False`` wether to send the message as an ephemeral message, only
            visible to the sender of the original message
        :return: None
        """
        if ephemeral:
            ephemeral_user = self.sender.id
        else:
            ephemeral_user = None

        self._client.send_webapi_scheduled(when, self.channel.id, text, attachments, ephemeral_user)

    def reply(self, text, in_thread=False):
        """Reply to the sender of the original message

        Reply to the sender of the original message with a new message, mentioning that user.

        :param text: message text
        :param in_thread: ``True/False`` wether to reply to the original message in-thread
        :return: None
        """
        if in_thread:
            self.say(text, thread_ts=self.thread_ts)
        else:
            text = self._create_reply(text)
            self.say(text)

    def reply_scheduled(self, when, text):
        """Schedule a reply

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.reply`.
        It behaves the same, but will send the reply at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :return: None
        """
        self.say_scheduled(when, self._create_reply(text))

    def reply_webapi(self, text, attachments=None, in_thread=False, ephemeral=False):
        """Reply to the sender of the original message using the WebAPI

        Reply to the sender of the original message with a new message, mentioning that user. Uses
        the WebAPI, so rich formatting using `attachments`_ is possible. Can also reply to a thread
        and send an ephemeral message only visible to the sender of the original message.
        Ephemeral messages and threaded messages are mutually exclusive, and ``ephemeral``
        takes precedence over ``thread_ts``

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :param in_thread: ``True/False`` wether to reply to the original message in-thread
        :param ephemeral: ``True/False`` wether to send the message as an ephemeral message, only
            visible to the sender of the original message
        :return: Dictionary deserialized from `chat.postMessage`_ request, or `chat.postEphemeral`_
            if `ephemeral` is True.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        .. _chat.postEphemeral: https://api.slack.com/methods/chat.postEphemeral
        """
        if in_thread and not ephemeral:
            return self.say_webapi(text, attachments=attachments, thread_ts=self.thread_ts)
        else:
            text = self._create_reply(text)
            return self.say_webapi(text, attachments=attachments, ephemeral=ephemeral)

    def reply_webapi_scheduled(self, when, text, attachments=None, ephemeral=False):
        """Schedule a reply and send it using the WebAPI

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.reply_webapi`.
        It behaves the same, but will send the reply at the scheduled time.

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param attachments: optional attachments (see `attachments`_)
        :param ephemeral: ``True/False`` wether to send the message as an ephemeral message, only
            visible to the sender of the original message
        :return: None
        """
        self.say_webapi_scheduled(when, self._create_reply(text), attachments, ephemeral)

    def reply_dm(self, text):
        """Reply to the sender of the original message with a DM

        Reply in a Direct Message to the sender of the original message by opening a DM channel and
        sending a message to it.

        :param text: message text
        :return: None
        """
        self._client.send_dm(self.sender.id, text)

    def reply_dm_scheduled(self, when, text):
        """Schedule a DM reply

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.reply_dm`. It
        behaves the same, but will send the DM at the scheduled time.

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :return: None
        """
        self._client.send_dm_scheduled(when, self.sender.id, text)

    def reply_dm_webapi(self, text, attachments=None):
        """Reply to the sender of the original message with a DM using the WebAPI

        Reply in a Direct Message to the sender of the original message by opening a DM channel and
        sending a message to it via the WebAPI. Allows for rich formatting using
        `attachments`_.

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :return: Dictionary deserialized from `chat.postMessage`_ request.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        """
        return self._client.send_dm_webapi(self.sender.id, text, attachments)

    def reply_dm_webapi_scheduled(self, when, text, attachments=None):
        """Schedule a DM reply and send it using the WebAPI

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.reply_dm_webapi`.
        It behaves the same, but will send the DM at the scheduled time.

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :return: None
        """
        self._client.send_dm_webapi_scheduled(when, self.sender.id, text, attachments)

    def react(self, emoji):
        """React to the original message

        Add a reaction to the original message

        :param emoji: what emoji to react with (should be a string, like 'angel', 'thumbsup', etc.)
        :return: Dictionary deserialized from `reactions.add`_ request.

        .. _reactions.add: https://api.slack.com/methods/reactions.add
        """
        return self._client.react(self.channel.id, self._msg_event['ts'], emoji)

    def _create_reply(self, text):
        if not self.is_dm:
            return "{}: {}".format(self.at_sender, text)
        else:
            return text

    @property
    def thread_ts(self):
        """The timestamp of the original message

        :return: the timestamp of the original message
        """
        try:
            thread_ts = self._msg_event['thread_ts']
        except KeyError:
            thread_ts = self._msg_event['ts']

        return thread_ts

    def __str__(self):
        return "Message '{}', sent by user @{} in channel #{}".format(
            self.text,
            self.sender.name,
            self.channel.name
        )

    def __repr__(self):
        return "Message(text={}, sender={}, channel={})".format(
            repr(self.text),
            repr(self.sender.name),
            repr(self.channel.name)
        )
