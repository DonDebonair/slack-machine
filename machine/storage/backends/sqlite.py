import aiosqlite
from machine.storage.backends.base import MachineBaseStorage
from typing import Any, Mapping


class SQLiteStorage(MachineBaseStorage):
    def __init__(self, settings: Mapping[str, Any]):
        self._file = settings.get("SQLITE_FILE")

    async def _connect(self):
        self.conn = await aiosqlite.connect(self._file)
        self.cursor = await self.conn.cursor()
        await self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires INTEGER
            )
        """
        )
        await self.conn.commit()

    async def set(self, key: str, value: str, expires: int = None):
        await self._connect()
        await self.cursor.execute(
            """
            INSERT OR REPLACE INTO storage (key, value, expires)
            VALUES (?, ?, ?)
        """,
            (key, value, expires),
        )
        await self.conn.commit()
        await self.conn.close()

    async def get(self, key: str):
        await self._connect()
        await self.cursor.execute("SELECT value FROM storage WHERE key=?", (key,))
        row = await self.cursor.fetchone()
        await self.conn.close()
        return row[0] if row else None

    async def delete(self, key: str):
        await self._connect()
        await self.cursor.execute("DELETE FROM storage WHERE key=?", (key,))
        await self.conn.commit()
        await self.conn.close()

    async def close(self):
        pass

    async def has(self, key: str):
        await self._connect()
        await self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM storage WHERE key=?)", (key,)
        )
        result = await self.cursor.fetchone()
        await self.conn.close()
        return bool(result[0])

    async def size(self):
        await self._connect()
        await self.cursor.execute("SELECT COUNT(*) FROM storage")
        result = await self.cursor.fetchone()
        await self.conn.close()
        return result[0]
