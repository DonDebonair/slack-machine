from __future__ import annotations

from typing import Any, Mapping

from redis.asyncio import Redis

from machine.utils.redis import gen_config_dict
from machine.storage.backends.base import MachineBaseStorage


class RedisStorage(MachineBaseStorage):
    _redis: Redis

    def __init__(self, settings: Mapping[str, Any]):
        super().__init__(settings)
        self._key_prefix = settings.get("REDIS_KEY_PREFIX", "SM")
        redis_config = gen_config_dict(settings)
        self._redis = Redis(**redis_config)

    def _prefix(self, key: str) -> str:
        return f"{self._key_prefix}:{key}"

    async def has(self, key: str) -> bool:
        return await self._redis.exists(self._prefix(key)) > 0

    async def get(self, key: str) -> bytes | None:
        return await self._redis.get(self._prefix(key))

    async def set(self, key: str, value: bytes, expires: int | None = None) -> None:
        await self._redis.set(self._prefix(key), value, expires)

    async def delete(self, key: str) -> None:
        await self._redis.delete(self._prefix(key))

    async def size(self) -> int:
        info = await self._redis.info("memory")
        return info["used_memory"]

    async def close(self) -> None:
        await self._redis.close()
