class MachineBasePlugin:
    """Base class for all Slack Machine plugins

    :var settings: Slack Machine settings object that contains all settings that
        were defined through ``local_settings.py``

    The purpose of this class is two-fold:

    1. It acts as a marker-class so Slack Machine can recognize plugins as such
    2. It provides a lot of common functionality and convenience methods for plugins to
       interact with channels and users
    """
    def __init__(self, settings, client):
        self._client = client
        self.settings = settings

    @property
    def users(self):
        return self._client.users

    @property
    def channels(self):
        return self._client.channels

    def say(self, channel, text, thread_ts=None):
        """Send a message to a channel

        Sends a message to a channel using the RTM API. Only basic Slack formatting allowed.
        For richer formatting using attachments, use :py:meth:`say_webapi`

        :param channel: id or name of channel to send message to
        :param text: message text
        :param thread_ts: optional timestamp of thread, to reply in thread
        """
        self._client.send(channel, text, thread_ts)

    def say_webapi(self, channel, text, attachments=None, thread_ts=None, ephemeral_user=None):
        """Send a message to a channel using the WebAPI

        :param channel: id or name of channel to send message to
        :param text: message text
        :param attachments: optional attachments
        :param thread_ts: optional timestamp of thread, to reply in thread
        :param ephemeral_user: optional user name or id if the message needs to visible
            to a specific user only
        """
        self._client.send_webapi(channel, text, attachments, thread_ts, ephemeral_user)

    def react(self, channel, ts, emoji):
        self._client.react(channel, ts, emoji)

    def send_dm(self, user, text):
        self._client.send_dm(user, text)

    def send_dm_webapi(self, user, text, attachments=None):
        self._client.send_dm_webapi(user, text, attachments)


class Message:
    def __init__(self, client, msg_event):
        self._client = client
        self._msg_event = msg_event

    @property
    def sender(self):
        return self._client.users.find(self._msg_event['user'])

    @property
    def channel(self):
        return self._client.channels.find(self._msg_event['channel'])

    @property
    def text(self):
        return self._msg_event['text']

    @property
    def sender_mention(self):
        return "<@{}>".format(self.sender.id)

    def say(self, text, thread_ts=None, **kwargs):
        self._client.send(self.channel.id, text, thread_ts)

    def say_webapi(self, text, attachments=None, thread_ts=None, ephemeral=False, **kwargs):
        if ephemeral:
            ephemeral_user = self.sender.id
        else:
            ephemeral_user = None
        self._client.send_webapi(self.channel.id, text, attachments, thread_ts, ephemeral_user)

    def reply(self, text, in_thread=False):
        if in_thread:
            self.say(text, thread_ts=self.thread_ts)
        else:
            text = self._create_reply(text)
            self.say(text)

    def reply_dm(self, text):
        self._client.send_dm(self.sender.id, text)

    def reply_webapi(self, text, attachments=None, in_thread=False, ephemeral=False):
        if in_thread and not ephemeral:
            self.say_webapi(text, attachments=attachments, thread_ts=self.thread_ts)
        else:
            text = self._create_reply(text)
            self.say_webapi(text, attachments=attachments, ephemeral=ephemeral)

    def reply_dm_webapi(self, text, attachments=None):
        self._client.send_dm_webapi(self.sender.id, text, attachments)

    def react(self, emoji, **kwargs):
        self._client.react(self.channel.id, self._msg_event['ts'], emoji)

    def _create_reply(self, text):
        chan = self._msg_event['channel']
        if chan.startswith('C') or chan.startswith('G'):
            return "{}: {}".format(self.sender_mention, text)
        else:
            return text

    @property
    def thread_ts(self):
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
