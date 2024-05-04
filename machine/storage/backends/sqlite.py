from __future__ import annotations

import time
from typing import Any, Mapping

import aiosqlite

from machine.storage.backends.base import MachineBaseStorage


class SQLiteStorage(MachineBaseStorage):
    def __init__(self, settings: Mapping[str, Any]):
        super().__init__(settings)
        self._file = settings.get("SQLITE_PATH", "slack-machine-state.db")

    async def close(self) -> None:
        await self.conn.close()

    async def init(self) -> None:
        self.conn = await aiosqlite.connect(self._file)
        self.conn.text_factory = bytes
        self.cursor = await self.conn.cursor()
        await self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sm_storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at INTEGER
            )
        """)
        await self.conn.commit()

    async def set(self, key: str, value: bytes, expires: int | None = None) -> None:
        current_ts = int(time.time())
        expires_at = current_ts + expires if expires is not None else None

        await self.cursor.execute(
            """
            INSERT OR REPLACE INTO sm_storage (key, value, expires_at)
            VALUES (?, ?, ?)
        """,
            (key, value, expires_at),
        )
        await self.conn.commit()

    async def get(self, key: str) -> bytes | None:
        current_ts = int(time.time())
        await self.cursor.execute(
            "SELECT value FROM sm_storage WHERE key=? AND (expires_at > ? OR expires_at IS NULL)", (key, current_ts)
        )
        row = await self.cursor.fetchone()
        return row[0] if row else None

    async def get_expire(self, key: str) -> bytes | None:
        current_ts = int(time.time())
        await self.cursor.execute(
            "SELECT expires_at FROM sm_storage WHERE key = ? AND (expires_at > ? OR expires_at IS NULL)",
            (key, current_ts),
        )
        row = await self.cursor.fetchone()
        return row[0] if row else None

    async def delete(self, key: str) -> None:
        await self.cursor.execute("DELETE FROM sm_storage WHERE key = ?", (key,))
        await self.conn.commit()

    async def has(self, key: str) -> bool:
        current_ts = int(time.time())
        await self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM sm_storage WHERE key = ? AND (expires_at > ? OR expires_at IS NULL))",
            (key, current_ts),
        )
        result = await self.cursor.fetchone()
        if result is not None:
            return result[0]
        return False

    async def size(self) -> int:
        await self.cursor.execute("SELECT payload FROM dbstat WHERE name = 'sm_storage' AND aggregate = TRUE")
        result = await self.cursor.fetchone()
        if result is not None:
            return result[0]
        return 0
