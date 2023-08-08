from datetime import datetime
import asyncio

import pytest

from machine.storage.backends.shelve import ShelfStorage


@pytest.fixture
def shelf_storage():
    return ShelfStorage({'STORAGE_FILE': 'shelve_test'})


@pytest.mark.asyncio
async def test_store_retrieve_values(shelf_storage):
    await shelf_storage.set("key1", "value1")
    assert shelf_storage._storage == {"key1": ("value1", None)}
    assert await shelf_storage.get("key1") == "value1"


@pytest.mark.asyncio
async def test_delete_values(shelf_storage):
    await shelf_storage.set("key1", "value1")
    await shelf_storage.set("key2", "value2")
    assert shelf_storage._storage == {"key1": ("value1", None), "key2": ("value2", None)}
    await shelf_storage.delete("key2")
    assert shelf_storage._storage == {"key1": ("value1", None)}


@pytest.mark.asyncio
async def test_expire_values(shelf_storage, mocker):
    mocked_dt = mocker.patch("machine.storage.backends.shelve.datetime", autospec=True)
    mocked_dt.utcnow.return_value = datetime(2017, 1, 1, 12, 0, 0, 0)
    await shelf_storage.set("key1", "value1", expires=15)
    assert shelf_storage._storage['key1'] == ("value1", datetime(2017, 1, 1, 12, 0, 15, 0))
    assert await shelf_storage.get("key1") == "value1"
    mocked_dt.utcnow.return_value = datetime(2017, 1, 1, 12, 0, 20, 0)
    assert await shelf_storage.get("key1") is None


@pytest.mark.asyncio
async def test_inclusion(shelf_storage):
    await shelf_storage.set("key1", "value1")
    assert await shelf_storage.has("key1") is True
    await shelf_storage.delete("key1")
    assert await shelf_storage.has("key1") is False
