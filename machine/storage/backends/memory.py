from __future__ import annotations

import sys
from datetime import datetime, timedelta
from typing import Any, Tuple, Mapping

from machine.storage.backends.base import MachineBaseStorage


class MemoryStorage(MachineBaseStorage):
    _storage: dict[str, Tuple[bytes, datetime | None]]

    def __init__(self, settings: Mapping[str, Any]):
        super().__init__(settings)
        self._storage = {}

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
        return sys.getsizeof(self._storage)  # pragma: no cover

    async def close(self) -> None:
        pass
