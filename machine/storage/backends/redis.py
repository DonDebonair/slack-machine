from urllib.parse import urlparse
from redis import StrictRedis

from machine.storage.backends.base import MachineBaseStorage


class RedisStorage(MachineBaseStorage):
    def __init__(self, settings):
        super().__init__(settings)
        self._key_prefix = settings.get('REDIS_KEY_PREFIX', 'SM')
        url = urlparse(settings['REDIS_URL'])
        if hasattr(url, "path"):
            db = url.path[1:]
        else:
            db = 0
        max_connections = settings.get('REDIS_MAX_CONNECTIONS', None)
        self._redis = StrictRedis(host=url.hostname, port=url.port, db=db,
                                  password=url.password, max_connections=max_connections)

    def _prefix(self, key):
        return "{}:{}".format(self._key_prefix, key)

    def has(self, key):
        return self._redis.exists(self._prefix(key))

    def get(self, key):
        return self._redis.get(self._prefix(key))

    def set(self, key, value, expires=None):
        self._redis.set(self._prefix(key), value, expires)

    def delete(self, key):
        self._redis.delete(self._prefix(key))

    def size(self):
        info = self._redis.info('memory')
        return info['used_memory']
