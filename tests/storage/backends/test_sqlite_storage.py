import pytest

from machine.storage.backends.sqlite import SQLiteStorage
import pytest_asyncio


@pytest_asyncio.fixture
async def sqlite_storage():
    storage = SQLiteStorage({"SQLITE_PATH": ":memory:"})
    await storage.init()
    yield storage
    await storage.close()


@pytest.mark.asyncio
async def test_set_and_get(sqlite_storage: SQLiteStorage):
    key = "test_key"
    value = b"test_value"
    await sqlite_storage.set(key, value)
    assert await sqlite_storage.get(key) == value


@pytest.mark.asyncio
async def test_has(sqlite_storage: SQLiteStorage):
    assert not await sqlite_storage.has("non_existant_key")
    await sqlite_storage.set("test_key", b"test_value")
    assert await sqlite_storage.has("test_key")


@pytest.mark.asyncio
async def test_delete(sqlite_storage: SQLiteStorage):
    await sqlite_storage.delete("test_key")
    assert not await sqlite_storage.has("test_key")


@pytest.mark.asyncio
async def test_expire_values(sqlite_storage: SQLiteStorage, mocker):
    mocked_time = mocker.patch("machine.storage.backends.sqlite.time", autospec=True)
    mocked_time.time.return_value = 44046732
    await sqlite_storage.set("key1", b"value1", expires=15)
    assert await sqlite_storage.get_expire("key1") == 44046732 + 15
    assert await sqlite_storage.get("key1") == b"value1"
    mocked_time.time.return_value = 44046732 + 20
    assert await sqlite_storage.get("key1") is None


@pytest.mark.asyncio
async def test_size(sqlite_storage: SQLiteStorage):
    assert await sqlite_storage.size() == 0
    await sqlite_storage.set("test_key_1", "test_value_1")
    await sqlite_storage.set("test_key_2", "test_value_2")
    assert await sqlite_storage.size() > 44  # number of characters in both columns for both rows
