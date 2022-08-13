from datetime import datetime

import pytest

from machine.asyncio.storage.backends.memory import MemoryStorage


@pytest.fixture
def memory_storage():
    return MemoryStorage({})


@pytest.mark.asyncio
async def test_store_retrieve_values(memory_storage):
    assert memory_storage._storage == {}
    await memory_storage.set("key1", "value1")
    assert memory_storage._storage == {"key1": ("value1", None)}
    assert await memory_storage.get("key1") == "value1"


@pytest.mark.asyncio
async def test_delete_values(memory_storage):
    assert memory_storage._storage == {}
    await memory_storage.set("key1", "value1")
    await memory_storage.set("key2", "value2")
    assert memory_storage._storage == {"key1": ("value1", None), "key2": ("value2", None)}
    await memory_storage.delete("key2")
    assert memory_storage._storage == {"key1": ("value1", None)}


@pytest.mark.asyncio
async def test_expire_values(memory_storage, mocker):
    assert memory_storage._storage == {}
    mocked_dt = mocker.patch("machine.asyncio.storage.backends.memory.datetime", autospec=True)
    mocked_dt.utcnow.return_value = datetime(2017, 1, 1, 12, 0, 0, 0)
    await memory_storage.set("key1", "value1", expires=15)
    assert memory_storage._storage == {"key1": ("value1", datetime(2017, 1, 1, 12, 0, 15, 0))}
    assert await memory_storage.get("key1") == "value1"
    mocked_dt.utcnow.return_value = datetime(2017, 1, 1, 12, 0, 20, 0)
    assert await memory_storage.get("key1") is None


@pytest.mark.asyncio
async def test_inclusion(memory_storage):
    assert memory_storage._storage == {}
    await memory_storage.set("key1", "value1")
    assert await memory_storage.has("key1") is True
    await memory_storage.delete("key1")
    assert await memory_storage.has("key1") is False
