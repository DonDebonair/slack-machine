class MachineBasePlugin:
    is_machine_plugin = True

    def __init__(self, settings, client):
        self.settings = settings
        self._client = client

    @property
    def users(self):
        return self._client.server.users

    @property
    def channels(self):
        return self._client.server.channels