import pytest
import tempfile
import os

from machine.storage.backends.sqlite import SQLiteStorage


@pytest.fixture
def sqlite_storage():
    with tempfile.NamedTemporaryFile(delete=False) as temp_db:
        temp_path = temp_db.name
    settings = {"SQLITE_FILE": temp_path}
    storage = SQLiteStorage(settings)
    yield storage
    os.unlink(temp_path)


@pytest.mark.asyncio
async def test_set_and_get(sqlite_storage):
    await sqlite_storage.set("key1", b"value1")
    value = await sqlite_storage.get("key1")
    assert value == b"value1"


@pytest.mark.asyncio
async def test_has(sqlite_storage):
    assert not await sqlite_storage.has("non_existant_key")
    await sqlite_storage.set("test_key", b"test_value")
    assert await sqlite_storage.has("test_key")


@pytest.mark.asyncio
async def test_delete(sqlite_storage):
    await sqlite_storage.delete("test_key")
    assert not await sqlite_storage.has("test_key")


@pytest.mark.asyncio
async def test_size(sqlite_storage):
    assert await sqlite_storage.size() == 0
    await sqlite_storage.set("test_key_1", "test_value_1")
    await sqlite_storage.set("test_key_2", "test_value_2")
    assert await sqlite_storage.size() == 2
