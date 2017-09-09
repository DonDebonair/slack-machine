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
    def __init__(self, settings, client):
        self._client = client
        self.settings = settings

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

    def at(self, user):
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
        """
        self._client.send(channel, text, thread_ts)

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
        """
        self._client.send_webapi(channel, text, attachments, thread_ts, ephemeral_user)

    def react(self, channel, ts, emoji):
        """React to a message in a channel

        Add a reaction to a message in a channel. What message to react to, is determined by the
        combination of the channel and the timestamp of the message.

        :param: channel: id or name of channel to send message to. Can be public or private (group)
            channel, or DM channel.
        :param: ts: timestamp of the message to react to
        :param: emoji: what emoji to react with (should be a string, like 'angel', 'thumbsup', etc.)
        """
        self._client.react(channel, ts, emoji)

    def send_dm(self, user, text):
        """Send a Direct Message

        Send a Direct Message to a user by opening a DM channel and sending a message to it.
        Only `basic Slack formatting`_ allowed. For richer formatting using attachments, use
        :py:meth:`~machine.plugins.base.MachineBasePlugin.send_dm_webapi`

        .. _basic Slack formatting: https://api.slack.com/docs/message-formatting

        :param: user: id or name of the user to send direct message to
        :param: text: message text
        """
        self._client.send_dm(user, text)

    def send_dm_webapi(self, user, text, attachments=None):
        """Send a Direct Message through the WebAPI

        Send a Direct Message to a user by opening a DM channel and sending a message to it via
        the WebAPI. Allows for rich formatting using
        `attachments`_.

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param: user: id or name of the user to send direct message to
        :param: text: message text
        :param attachments: optional attachments (see `attachments`_)
        """
        self._client.send_dm_webapi(user, text, attachments)


class Message:
    """A message that was received by the bot

    This class represents a message that was received by the bot and passed to one or more
    plugins. It contains the message (text) itself, and metadata about the message, such as the
    sender of the message, the channel the message was sent to.

    The ``Message`` class also contains convenience methods for replying to the message in the
    right channel, replying to the sender, etc.
    """
    def __init__(self, client, msg_event):
        self._client = client
        self._msg_event = msg_event

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
        """
        self._client.send(self.channel.id, text, thread_ts)

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
        """
        if ephemeral:
            ephemeral_user = self.sender.id
        else:
            ephemeral_user = None
        self._client.send_webapi(self.channel.id, text, attachments, thread_ts, ephemeral_user)

    def reply(self, text, in_thread=False):
        """Reply to the sender of the original message

        Reply to the sender of the original message with a new message, mentioning that user.
        :param text: message text
        :param in_thread: ``True/False`` wether to reply to the original message in-thread
        """
        if in_thread:
            self.say(text, thread_ts=self.thread_ts)
        else:
            text = self._create_reply(text)
            self.say(text)

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
        """
        if in_thread and not ephemeral:
            self.say_webapi(text, attachments=attachments, thread_ts=self.thread_ts)
        else:
            text = self._create_reply(text)
            self.say_webapi(text, attachments=attachments, ephemeral=ephemeral)

    def reply_dm(self, text):
        """Reply to the sender of the original message in a DM

        Reply in a Direct Message to the sender of the original message by opening a DM channel and
        sending a message to it.

        :param text: message text
        """
        self._client.send_dm(self.sender.id, text)

    def reply_dm_webapi(self, text, attachments=None):
        """Reply to the sender of the original message in a DM using the WebAPI

        Reply in a Direct Message to the sender of the original message by opening a DM channel and
        sending a message to it via the WebAPI. Allows for rich formatting using
        `attachments`_.

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        """
        self._client.send_dm_webapi(self.sender.id, text, attachments)

    def react(self, emoji):
        """React to the original message

        Add a reaction to the original message

        :param emoji: what emoji to react with (should be a string, like 'angel', 'thumbsup', etc.)
        """
        self._client.react(self.channel.id, self._msg_event['ts'], emoji)

    def _create_reply(self, text):
        chan = self._msg_event['channel']
        if chan.startswith('C') or chan.startswith('G'):
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
