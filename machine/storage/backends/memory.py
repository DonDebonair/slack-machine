import sys
from datetime import datetime, timedelta

from machine.storage.backends.base import MachineBaseStorage


class MemoryStorage(MachineBaseStorage):
    def __init__(self, settings):
        super().__init__(settings)
        self._storage = {}

    def get(self, key):
        stored = self._storage.get(key, None)
        if not stored:
            return None
        else:
            if stored[1] and stored[1] < datetime.utcnow():
                del self._storage[key]
                return None
            else:
                return stored[0]

    def set(self, key, value, expires=None):
        if expires:
            expires_at = datetime.utcnow() + timedelta(seconds=expires)
        else:
            expires_at = None
        self._storage[key] = (value, expires_at)

    def has(self, key):
        stored = self._storage.get(key, None)
        if not stored:
            return False
        else:
            if stored[1] and stored[1] < datetime.utcnow():
                del self._storage[key]
                return False
            else:
                return True

    def delete(self, key):
        del self._storage[key]

    def size(self):
        return sys.getsizeof(self._storage)  # pragma: no cover
