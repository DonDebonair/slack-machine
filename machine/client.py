class MessagingClient:
    def __init__(self, slack_client):
        self._slack_client = slack_client

    @property
    def users(self):
        return self._slack_client.server.users

    @property
    def channels(self):
        return self._slack_client.server.channels

    def send(self, channel, text, thread_ts=None):
        self._slack_client.rtm_send_message(channel, text, thread_ts)

    def send_webapi(self, channel, text, attachments=None, thread_ts=None, ephemeral_user=None):
        method = 'chat.postMessage'
        # This is the only way to conditionally add thread_ts
        kwargs = {
            'channel': channel,
            'text': text,
            'attachments': attachments,
            'as_user': True
        }
        if ephemeral_user:
            method = 'chat.postEphemeral'
            kwargs['user'] = ephemeral_user
        else:
            if thread_ts:
                kwargs['thread_ts'] = thread_ts
        self._slack_client.api_call(
            method,
            **kwargs
        )

    def react(self, channel, ts, emoji):
        self._slack_client.api_call(
            'reactions.add',
            name=emoji,
            channel=channel,
            timestamp=ts
        )

    def open_im(self, user):
        response = self._slack_client.api_call(
            'im.open',
            user=user
        )
        return response['channel']['id']

    def send_dm(self, user, text):
        dm_channel = self.open_im(user)
        self.send(dm_channel, text)

    def send_dm_webapi(self, user, text, attachments=None):
        dm_channel = self.open_im(user)
        self._slack_client.api_call(
            'chat.postMessage',
            channel=dm_channel,
            text=text,
            attachments=attachments,
            as_user=True
        )
