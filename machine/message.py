# -*- coding: utf-8 -*-

from async_lru import alru_cache


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
    def user_id(self) -> str:
        return self._msg_event["user"]

    @property
    def channel_id(self) -> str:
        return self._msg_event["channel"]

    @property
    def thread_ts(self):
        """The timestamp of the original message

        :return: the timestamp of the original message
        """
        try:
            thread_ts = self._msg_event["thread_ts"]
        except KeyError:
            thread_ts = self._msg_event["ts"]

        return thread_ts

    @property
    def is_dm(self) -> bool:
        chan = self.channel_id
        return not (chan.startswith("C") or chan.startswith("G"))

    @property
    def at_sender(self):
        """The sender of the message formatted as mention

        :return: a string representation of the sender of the message, formatted as `mention`_,
            to be used in messages

        .. _mention: https://api.slack.com/docs/message-formatting#linking_to_channels_and_users
        """
        return self._client.fmt_mention({"id": self.user_id})

    @property
    def text(self):
        """The body of the actual message

        :return: the body (text) of the actual message
        """
        return self._msg_event["text"]

    @alru_cache(maxsize=8)
    async def get_sender(self) -> dict:
        """The sender of the message

        :return: dictionary describing the user the message was sent by
        """
        return await self._client.find_user_by_id(self.user_id)

    @alru_cache(maxsize=8)
    async def get_channel(self) -> dict:
        """The channel the message was sent to

        :return: dictionary describing the channel the message was sent to
        """
        return await self._client.find_channel_by_id(self.channel_id)

    async def say(self, text, **kwargs):
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
        :param ephemeral: ``True/False`` whether to send the message as an ephemeral message, only
            visible to the sender of the original message
        :return: Dictionary deserialized from `chat.postMessage`_ request, or `chat.postEphemeral`_
            if `ephemeral` is True.

        .. _chat.postMessage: https://api.slack.com/methods/chat.postMessage
        .. _chat.postEphemeral: https://api.slack.com/methods/chat.postEphemeral
        """

        return await self._client.send(
            self.channel_id, text, **self._handle_context_args(**kwargs)
        )

    def say_scheduled(self, when, text, **kwargs):
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

        self._client.send_scheduled(
            when, self.channel_id, text, **self._handle_context_args(**kwargs)
        )

    async def reply(self, text, **kwargs):
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
        in_thread = kwargs.get("in_thread", False)
        ephemeral = kwargs.get("ephemeral", False)
        if in_thread and not ephemeral:
            text = self._create_reply(text)

        return await self.say(text, **self._handle_context_args(**kwargs))

    def reply_scheduled(self, when, text, **kwargs):
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
        in_thread = kwargs.get("in_thread", False)
        ephemeral = kwargs.get("ephemeral", False)
        if in_thread and not ephemeral:
            text = self._create_reply(text)

        self.say_scheduled(when, text, **self._handle_context_args(**kwargs))

    async def reply_dm(self, text, **kwargs):
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
        return await self._client.send_dm(
            self.user_id, text, **self._handle_context_args(**kwargs)
        )

    def reply_dm_scheduled(self, when, text, **kwargs):
        """Schedule a DM reply and send it using the WebAPI

        This is the scheduled version of :py:meth:`~machine.plugins.base.Message.reply_dm_webapi`.
        It behaves the same, but will send the DM at the scheduled time.

        .. _attachments: https://api.slack.com/docs/message-attachments

        :param when: when you want the message to be sent, as :py:class:`datetime.datetime` instance
        :param text: message text
        :param attachments: optional attachments (see `attachments`_)
        :return: None
        """
        self._client.send_dm_scheduled(
            when, self.user_id, text, **self._handle_context_args(**kwargs)
        )

    async def react(self, emoji):
        """React to the original message

        Add a reaction to the original message

        :param emoji: what emoji to react with (should be a string, like 'angel', 'thumbsup', etc.)
        :return: Dictionary deserialized from `reactions.add`_ request.

        .. _reactions.add: https://api.slack.com/methods/reactions.add
        """
        return await self._client.react(self.channel_id, self.thread_ts, emoji)

    def _create_reply(self, text):
        if not self.is_dm:
            return "{}: {}".format(self.at_sender, text)
        else:
            return text

    def _handle_context_args(self, **kwargs):
        """ Given **kwargs from `say` and friends, turn certain contextual
            arguments (ie., `ephemeral`, `in_thread`) into context-free args
            to send to Slack.
        """

        next_kwargs = {}

        if kwargs.pop("ephemeral", False):
            next_kwargs["ephemeral_user"] = self.user_id

        if kwargs.pop("in_thread", False):
            next_kwargs["thread_ts"] = self.thread_ts

        if "ephemeral_user" in next_kwargs and "thread_ts" in next_kwargs:
            raise ValueError("Messages may be in-thread or ephemeral, not both")

        next_kwargs.update(kwargs)
        return next_kwargs

    def __str__(self):
        return "Message '{}', sent by user @{} in channel #{}".format(
            self.text, self.user_id, self.channel_id
        )

    def __repr__(self):
        return "Message(text={}, sender={}, channel={})".format(
            repr(self.text), repr(self.user_id), repr(self.channel_id)
        )
