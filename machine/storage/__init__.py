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
        return "{}:{}".format(self._fq_plugin_name, key)

    def _namespace_key(self, key, shared):
        return key if shared else self._gen_unique_key(key)

    def set(self, key, value, expires=None, shared=False):
        """Store or update a value by key

        :param key: the key under which to store the data
        :param value: the data to store
        :param expires: optional number of seconds after which the data is expired
        :param shared: ``True/False`` wether this data should be shared by other plugins.  Use with
            care, because it pollutes the global namespace of the storage.
        """
        namespaced_key = self._namespace_key(key, shared)
        pickled_value = dill.dumps(value)
        Storage.get_instance().set(namespaced_key, pickled_value, expires)

    def get(self, key, shared=False):
        """Retrieve data by key

        :param key: key for the data to retrieve
        :param shared: ``True/False`` wether to retrieve data from the shared (global) namespace.
        :return: the data, or ``None`` if the key cannot be found/has expired
        """
        namespaced_key = self._namespace_key(key, shared)
        value = Storage.get_instance().get(namespaced_key)
        if value:
            return dill.loads(value)
        else:
            return None

    def has(self, key, shared=False):
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
        return Storage.get_instance().has(namespaced_key)

    def delete(self, key, shared=False):
        """Remove a key and its data from storage

        :param key: key to remove
        :param shared: ``True/False`` wether the key to remove should be in the shared (global)
            namespace
        """
        namespaced_key = self._namespace_key(key, shared)
        Storage.get_instance().delete(namespaced_key)

    def get_storage_size(self):
        """Calculate the total size of the storage

        :return: the total size of the storage in bytes (integer)
        """
        return Storage.get_instance().size()

    def get_storage_size_human(self):
        """Calculate the total size of the storage in human readable format

        :return: the total size of the storage in a human readable string, rounded to the nearest
            applicable division. eg. B for Bytes, KiB for Kilobytes, MiB for Megabytes etc.
        """
        return sizeof_fmt(self.get_storage_size())

    def __contains__(self, key):
        return self.has(key, False)
