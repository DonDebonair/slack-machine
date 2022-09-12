import pytest

from machine.storage import PluginStorage
from machine.storage.backends.memory import MemoryStorage


@pytest.fixture
def storage_backend():
    storage = MemoryStorage({})
    return storage


@pytest.fixture
def plugin_storage(storage_backend):
    storage_instance = PluginStorage("tests.fake_plugin.FakePlugin", storage_backend)
    return storage_instance


@pytest.mark.asyncio
async def test_namespacing(plugin_storage, storage_backend):
    await plugin_storage.set("key1", "value1")
    expected_key = "tests.fake_plugin.FakePlugin:key1"
    assert expected_key in storage_backend._storage


@pytest.mark.asyncio
async def test_inclusion(plugin_storage, storage_backend):
    await plugin_storage.set("key1", "value1")
    assert await plugin_storage.has("key1") is True


@pytest.mark.asyncio
async def test_retrieve(plugin_storage):
    await plugin_storage.set("key1", "value1")
    retrieved = await plugin_storage.get("key1")
    assert retrieved == "value1"


@pytest.mark.asyncio
async def test_shared(plugin_storage, storage_backend):
    await plugin_storage.set("key1", "value1", shared=True)
    assert await plugin_storage.has("key1") is False
    assert await plugin_storage.has("key1", shared=True) is True
    expected_key = "key1"
    assert expected_key in storage_backend._storage


@pytest.mark.asyncio
async def test_delete(plugin_storage, storage_backend):
    await plugin_storage.set("key1", "value1")
    assert await plugin_storage.has("key1") is True
    expected_key = "tests.fake_plugin.FakePlugin:key1"
    assert expected_key in storage_backend._storage
    await plugin_storage.delete("key1")
    assert await plugin_storage.has("key1") is False
    assert expected_key not in storage_backend._storage
