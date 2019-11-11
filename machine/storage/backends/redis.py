# -*- coding: utf-8 -*-

import aioredis

from machine.storage.backends.base import MachineBaseStorage


class RedisStorage(MachineBaseStorage):
    def __init__(self, settings):
        super().__init__(settings)
        self._redis_url = settings.get("REDIS_URL", "redis://localhost:6379")
        self._max_connections = settings.get("REDIS_MAX_CONNECTIONS", 10)
        self._key_prefix = settings.get("REDIS_KEY_PREFIX", "SM")
        self._redis = None

    async def connect(self):
        self._redis = await aioredis.create_redis_pool(
            self._redis_url, maxsize=self._max_connections
        )

    def _ensure_connected(self):
        if self._redis is None:
            raise NotConnectedError()

    def _prefix(self, key):
        return "{}:{}".format(self._key_prefix, key)

    async def has(self, key):
        self._ensure_connected()
        return await self._redis.exists(self._prefix(key))

    async def get(self, key):
        self._ensure_connected()
        return await self._redis.get(self._prefix(key))

    async def set(self, key, value, expires=None):
        self._ensure_connected()
        await self._redis.set(self._prefix(key), value, expire=expires)

    async def delete(self, key):
        self._ensure_connected()
        await self._redis.delete(self._prefix(key))

    async def size(self):
        self._ensure_connected()
        info = await self._redis.info("memory")
        return info["used_memory"]


class NotConnectedError(Exception):
    def __init__(self):
        super().__init__()
        self.message = "RedisStorage backend must be `connect()`ed before using"

    def __repr__(self):
        return self.message

    __str__ = __repr__
