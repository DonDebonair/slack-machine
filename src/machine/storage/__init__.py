from __future__ import annotations

from datetime import timedelta
from typing import Any

import dill

from machine.storage.backends.base import MachineBaseStorage
from machine.utils import sizeof_fmt


class PluginStorage:
    """Class providing access to persistent storage for plugins

    This class is the main access point for plugins to work with persistent storage. It is
    accessible from plugins using ``self.storage``. Data is serialized before sending it to
    the storage backend, and deserialized upon retrieval. Serialization is done by `dill`_, so
    pretty much any Python object can be stored and retrieved.

    .. _Dill: https://pypi.python.org/pypi/dill
    """

    def __init__(self, fq_plugin_name: str, storage_backend: MachineBaseStorage):
        self._fq_plugin_name = fq_plugin_name
        self._storage = storage_backend

    def _gen_unique_key(self, key: str) -> str:
        return f"{self._fq_plugin_name}:{key}"

    def _namespace_key(self, key: str, shared: bool = False) -> str:
        return key if shared else self._gen_unique_key(key)

    async def set(self, key: str, value: Any, expires: int | timedelta | None = None, shared: bool = False) -> None:
        """Store or update a value by key

        :param key: the key under which to store the data
        :param value: the data to store
        :param expires: optional number of seconds after which the data is expired
        :param shared: ``True/False`` wether this data should be shared by other plugins.  Use with
            care, because it pollutes the global namespace of the storage.
        """
        expires = int(expires.total_seconds()) if isinstance(expires, timedelta) else expires
        namespaced_key = self._namespace_key(key, shared)
        pickled_value = dill.dumps(value)
        await self._storage.set(namespaced_key, pickled_value, expires)

    async def get(self, key: str, shared: bool = False) -> Any | None:
        """Retrieve data by key

        :param key: key for the data to retrieve
        :param shared: ``True/False`` wether to retrieve data from the shared (global) namespace.
        :return: the data, or ``None`` if the key cannot be found/has expired
        """
        namespaced_key = self._namespace_key(key, shared)
        value = await self._storage.get(namespaced_key)
        if value:
            return dill.loads(value)
        else:
            return None

    async def has(self, key: str, shared: bool = False) -> bool:
        """Check if the key exists in storage

        Note: this class implements ``__contains__`` so instead of calling
        ``self.storage.has(...)``, you can also use: ``key in self.storage``. This will check the
        *namespaced* version of the key, so it's the same as:
        ``self.storage.has('key', shared=False)``

        :param key: key to check
        :param shared: ``True/False`` wether to check in the shared (global) namespace
        :return: ``True/False`` wether the key exists. Can only return ``True`` if the key has not
            expired.
        """
        namespaced_key = self._namespace_key(key, shared)
        return await self._storage.has(namespaced_key)

    async def delete(self, key: str, shared: bool = False) -> None:
        """Remove a key and its data from storage

        :param key: key to remove
        :param shared: ``True/False`` wether the key to remove should be in the shared (global)
            namespace
        """
        namespaced_key = self._namespace_key(key, shared)
        await self._storage.delete(namespaced_key)

    async def get_storage_size(self) -> int:
        """Calculate the total size of the storage

        :return: the total size of the storage in bytes (integer)
        """
        return await self._storage.size()

    async def get_storage_size_human(self) -> str:
        """Calculate the total size of the storage in human readable format

        :return: the total size of the storage in a human readable string, rounded to the nearest
            applicable division. eg. B for Bytes, KiB for Kilobytes, MiB for Megabytes etc.
        """
        size = await self.get_storage_size()
        return sizeof_fmt(size)
