from typing import Any, Mapping

import shelve
import atexit
from datetime import datetime, timedelta

from machine.storage.backends.base import MachineBaseStorage
from machine.plugins.decorators import required_settings


@required_settings(['STORAGE_FILE'])
class ShelfStorage(MachineBaseStorage):
    """ Shelve is module of the Python standard library that provides a
    persistent, dictionary-like object that is stored in a file.  It
    serves as a very simple way to provide cross-session persistent storage
    for the slack-machine.

    Objects in a shelf are pickled, so the usual warnings apply about
    pickling.

    To use this module, include in your setting file:
    STORAGE_BACKEND = 'machine.storage.backends.shelve.ShelfStorage'
    STORAGE_FILE = 'path/to/file'  # Do not provide an extension.

    The storage will be created in a set of files
    path/to/file.dat
    path/to/file.dir
    path/to/file.bak
    """
    settings: Mapping[str, Any]
    _storage: shelve.Shelf

    def __init__(self, settings: Mapping[str, Any]):
        super().__init__(settings)
        storage_file = settings['STORAGE_FILE']
        self._storage = shelve.open(storage_file, 'c')
        atexit.register(self._cleanup)

    def _cleanup(self):
        self._storage.close()

    async def get(self, key: str) -> bytes | None:
        stored = self._storage.get(key, None)
        if stored is None:
            return None
        else:
            if stored[1] and stored[1] < datetime.utcnow():
                del self._storage[key]
                return None
            else:
                return stored[0]

    async def set(self, key: str, value: bytes, expires: int | None = None) -> None:
        if expires:
            expires_at = datetime.utcnow() + timedelta(seconds=expires)
        else:
            expires_at = None
        self._storage[key] = (value, expires_at)

    async def has(self, key: str) -> bool:
        stored = self._storage.get(key, None)
        if stored is None:
            return False
        else:
            if stored[1] and stored[1] < datetime.utcnow():
                del self._storage[key]
                return False
            else:
                return True

    async def delete(self, key: str) -> None:
        del self._storage[key]

    async def size(self) -> int:
        return 0

    async def close(self) -> None:
        self._cleanup()
