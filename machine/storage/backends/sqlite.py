from __future__ import annotations

import aiosqlite
import time
from machine.storage.backends.base import MachineBaseStorage
from typing import Any, Mapping
from contextlib import AsyncExitStack


class SQLiteStorage(MachineBaseStorage):
    _context_stack: AsyncExitStack

    def __init__(self, settings: Mapping[str, Any]):
        self._file = settings.get("SQLITE_FILE", "slack-machine-state.db")

    async def close(self) -> None:
        await self.conn.close()

    async def init(self) -> None:
        self.conn = await aiosqlite.connect(self._file)
        self.conn.text_factory = bytes
        self.cursor = await self.conn.cursor()
        await self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires INTEGER
            )
        """)
        await self.conn.commit()

    async def set(self, key: str, value: bytes, expires: int | None = None) -> None:
        await self.cursor.execute(
            """
            INSERT OR REPLACE INTO storage (key, value, expires)
            VALUES (?, ?, ?)
        """,
            (key, value, expires),
        )
        await self.conn.commit()

    async def get(self, key: str) -> bytes | None:
        current_GMT = int(time.time())
        await self.cursor.execute(
            "SELECT value FROM storage WHERE key=? and (expires > ? OR expires IS NULL)", (key, current_GMT)
        )
        row = await self.cursor.fetchone()
        return row[0] if row else None

    async def delete(self, key: str) -> None:
        await self.cursor.execute("DELETE FROM storage WHERE key=?", (key,))
        await self.conn.commit()

    async def has(self, key: str) -> bool:
        current_GMT = int(time.time())
        await self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM storage WHERE key=? and (expires > ? OR expires IS NULL))", (key, current_GMT)
        )
        result = await self.cursor.fetchone()
        if result is not None:
            return result[0]
        return False

    async def size(self) -> int:
        await self.cursor.execute("SELECT COUNT(*) FROM storage")
        result = await self.cursor.fetchone()
        if result is not None:
            return result[0]
        return 0
