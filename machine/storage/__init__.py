import dill

from machine.utils import sizeof_fmt


class PluginStorage:
    def __init__(self, fq_plugin_name, storage_backend):
        self._storage = storage_backend
        self._fq_plugin_name = fq_plugin_name

    def _gen_unique_key(self, key):
        return "{}:{}".format(self._fq_plugin_name, key)

    def _namespace_key(self, key, shared):
        return key if shared else self._gen_unique_key(key)

    def set(self, key, value, expires=None, shared=False):
        namespaced_key = self._namespace_key(key, shared)
        pickled_value = dill.dumps(value)
        self._storage.set(namespaced_key, pickled_value, expires)

    def get(self, key, shared=False):
        namespaced_key = self._namespace_key(key, shared)
        value = self._storage.get(namespaced_key)
        if value:
            return dill.loads(value)
        else:
            return None

    def has(self, key, shared=False):
        namespaced_key = self._namespace_key(key, shared)
        return self._storage.has(namespaced_key)

    def delete(self, key, shared=False):
        namespaced_key = self._namespace_key(key, shared)
        self._storage.delete(namespaced_key)

    def get_storage_size(self):
        return self._storage.size()

    def get_storage_size_human(self):
        return sizeof_fmt(self.get_storage_size())

    def __contains__(self, key):
        return self.has(key, False)
