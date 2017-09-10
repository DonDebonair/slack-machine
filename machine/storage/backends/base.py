class MachineBaseStorage:
    def __init__(self, settings):
        self.settings = settings

    def get(self, key):
        raise NotImplementedError

    def set(self, key, value, expires=None):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def has(self, key):
        raise NotImplementedError

    def size(self):
        raise NotImplementedError
