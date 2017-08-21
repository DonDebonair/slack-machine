class MachineBasePlugin:

    def __init__(self, settings, client):
        self.settings = settings
        self._client = client

    @property
    def users(self):
        return self._client.server.users

    @property
    def channels(self):
        return self._client.server.channels

    def send(self, channel, message, thread=None, reply_broadcast=None):
        self._client.rtm_send_message(channel, message, thread, reply_broadcast)

class Message:

    def __init__(self, client, msg_event):
        self._client = client
        self._msg_event = msg_event

    @property
    def sender(self):
        return self._client.server.users.find(self._msg_event['user'])

    @property
    def channel(self):
        return self._client.server.channels.find(self._msg_event['channel'])

    @property
    def text(self):
        return self._msg_event['text']

    def send(self, text):
        self._client.rtm_send_message(self.channel.id, text)

    def __str__(self):
        return "Message '{}', sent by user @{} in channel #{}".format(self.text, self.sender.name, self.channel.name)

