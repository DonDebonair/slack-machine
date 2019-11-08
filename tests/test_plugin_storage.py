# -*- coding: utf-8 -*-
import pytest

from machine.storage import PluginStorage
from machine.storage.backends.memory import MemoryStorage

from tests.helpers import async_test


@pytest.fixture
def storage_backend(mocker):
    storage = MemoryStorage({})
    backend_get_instance = mocker.patch("machine.storage.Storage.get_instance")
    backend_get_instance.return_value = storage
    return storage


@pytest.fixture
def plugin_storage(storage_backend):
    storage_instance = PluginStorage("tests.fake_plugin.FakePlugin")
    return storage_instance


@async_test
async def test_namespacing(plugin_storage, storage_backend):
    await plugin_storage.set("key1", "value1")
    expected_key = "tests.fake_plugin.FakePlugin:key1"
    assert expected_key in storage_backend._storage


@async_test
async def test_inclusion(plugin_storage, storage_backend):
    await plugin_storage.set("key1", "value1")
    assert (await plugin_storage.has("key1")) == True
    assert await plugin_storage.has("key1")


@async_test
async def test_retrieve(plugin_storage):
    await plugin_storage.set("key1", "value1")
    retrieved = await plugin_storage.get("key1")
    assert retrieved == "value1"


@async_test
async def test_shared(plugin_storage, storage_backend):
    await plugin_storage.set("key1", "value1", shared=True)
    assert (await plugin_storage.has("key1")) == False
    assert (await plugin_storage.has("key1", shared=True)) == True
    expected_key = "key1"
    assert expected_key in storage_backend._storage


@async_test
async def test_delete(plugin_storage, storage_backend):
    await plugin_storage.set("key1", "value1")
    assert (await plugin_storage.has("key1")) == True
    expected_key = "tests.fake_plugin.FakePlugin:key1"
    assert expected_key in storage_backend._storage
    await plugin_storage.delete("key1")
    assert (await plugin_storage.has("key1")) == False
    assert expected_key not in storage_backend._storage
