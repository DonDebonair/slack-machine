# -*- coding: utf-8 -*-
import dill

from machine.singletons import Storage
from machine.utils import sizeof_fmt


class PluginStorage:
    """Class providing access to persistent storage for plugins

    This class is the main access point for plugins to work with persistent storage. It is
    accessible from plugins using ``self.storage``. Data is serialized before sending it to
    the storage backend, and deserialized upon retrieval. Serialization is done by `dill`_, so
    pretty much any Python object can be stored and retrieved.

    .. _Dill: https://pypi.python.org/pypi/dill
    """

    def __init__(self, fq_plugin_name):
        self._fq_plugin_name = fq_plugin_name

    def _gen_unique_key(self, key):
        separator = ":"
        namespace = self._fq_plugin_name
        if isinstance(key, bytes):
            separator = separator.encode("utf-8")
            namespace = namespace.encode("utf-8")

        if key.startswith(namespace):
            return key

        return namespace + separator + key

    def _namespace_key(self, key, shared):
        return key if shared else self._gen_unique_key(key)

    async def set(self, key, value, expires=None, shared=False):
        """Store or update a value by key

        :param key: the key under which to store the data
        :param value: the data to store
        :param expires: optional number of seconds after which the data is expired
        :param shared: ``True/False`` whether this data should be shared by other plugins.  Use with
            care, because it pollutes the global namespace of the storage.
        """
        namespaced_key = self._namespace_key(key, shared)
        pickled_value = dill.dumps(value)
        await Storage.get_instance().set(namespaced_key, pickled_value, expires)

    async def get(self, key, shared=False):
        """Retrieve data by key

        :param key: key for the data to retrieve
        :param shared: ``True/False`` whether to retrieve data from the shared (global) namespace.
        :return: the data, or ``None`` if the key cannot be found/has expired
        """
        namespaced_key = self._namespace_key(key, shared)
        value = await Storage.get_instance().get(namespaced_key)
        if value:
            return dill.loads(value)
        else:
            return None

    async def has(self, key, shared=False):
        """Check if the key exists in storage

        Note: this class implements ``__contains__`` so instead of calling
        ``self.storage.has(...)``, you can also use: ``key in self.storage``. This will check the
        *namespaced* version of the key, so it's the same as:
        ``self.storage.has('key', shared=False)``

        :param key: key to check
        :param shared: ``True/False`` whether to check in the shared (global) namespace
        :return: ``True/False`` whether the key exists. Can only return ``True`` if the key has not
            expired.
        """
        namespaced_key = self._namespace_key(key, shared)
        return await Storage.get_instance().has(namespaced_key)

    async def delete(self, key, shared=False):
        """Remove a key and its data from storage

        :param key: key to remove
        :param shared: ``True/False`` whether the key to remove should be in the shared (global)
            namespace
        """
        namespaced_key = self._namespace_key(key, shared)
        await Storage.get_instance().delete(namespaced_key)

    async def find_keys(self, pattern, shared=False):
        """ Find all keys matching the pattern.

            :param pattern: pattern to search for
            :param shared: ``True/False`` whether the search should occur on the shared (global)
                namespace
            :return: iterable over matching keys
        """
        namespaced_ptn = self._namespace_key(pattern, shared)
        return await Storage.get_instance().find_keys(namespaced_ptn)

    async def get_storage_size(self):
        """Calculate the total size of the storage

        :return: the total size of the storage in bytes (integer)
        """
        return await Storage.get_instance().size()

    async def get_storage_size_human(self):
        """Calculate the total size of the storage in human readable format

        :return: the total size of the storage in a human readable string, rounded to the nearest
            applicable division. eg. B for Bytes, KiB for Kilobytes, MiB for Megabytes etc.
        """
        return sizeof_fmt(await self.get_storage_size())
