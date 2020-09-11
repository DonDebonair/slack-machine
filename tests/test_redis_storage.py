# -*- coding: utf-8 -*-

from unittest import mock

import aioredis
import dill
import pytest

from machine.storage import PluginStorage
from machine.storage.backends.redis import RedisStorage

from tests.helpers.aio import make_awaitable_result
from tests.helpers.expect import AsyncExpectMock, expect


@pytest.fixture(scope="module")
def redis_client():
    return AsyncExpectMock()


@pytest.fixture
def redis_storage(expect, redis_client):
    create_redis_pool = mock.patch(
        "machine.storage.backends.redis.aioredis.create_redis_pool"
    )
    create_redis_pool.return_value = expect.AsyncExpectMock()
    settings = {"REDIS_URL": "redis://nohost:1234"}
    storage = RedisStorage(settings)
    storage._redis = redis_client
    return storage


@pytest.fixture
def plugin_storage(mocker, redis_storage):
    backend_get_instance = mocker.patch("machine.storage.Storage.get_instance")
    backend_get_instance.return_value = redis_storage
    return PluginStorage("FakePlugin")


@pytest.mark.asyncio
async def test_set(redis_storage, redis_client):
    redis_client.set.expect("SM:key1", "value1", expire=None).returns(None)
    redis_client.set.expect("SM:key2", "value2", expire=42).returns(None)

    await redis_storage.set("key1", "value1", expires=None)
    await redis_storage.set("key2", "value2", expires=42)


@pytest.mark.asyncio
async def test_get(redis_storage, redis_client):
    redis_client.get.expect("SM:key1").returns(None)

    await redis_storage.get("key1")


@pytest.mark.asyncio
async def test_has(redis_storage, redis_client):
    redis_client.exists.expect("SM:key1").returns(None)

    await redis_storage.has("key1")


@pytest.mark.asyncio
async def test_delete(redis_storage, redis_client):
    redis_client.delete.expect("SM:key1").returns(None)

    await redis_storage.delete("key1")


@pytest.mark.asyncio
async def test_size(redis_storage, redis_client):
    redis_client.info.expect("memory").returns(
        {"memory": {"used_memory": "haha all of it"}}
    )

    await redis_storage.size()


def test_prefix_bytes(redis_storage):
    assert redis_storage._prefix(b"my-data") == b"SM:my-data"


def test_prefix_str(redis_storage):
    assert redis_storage._prefix("my-data") == "SM:my-data"


@pytest.mark.asyncio
async def test_find_keys(redis_storage, redis_client):
    redis_client.set.expect("SM:ns:key1", "1", expire=None).returns(None)
    redis_client.set.expect("SM:ns:key2", "2", expire=None).returns(None)
    redis_client.set.expect("SM:ms:key3", "3", expire=None).returns(None)
    redis_client.scan.expect(cursor=b"0", match="SM:ns:*").returns(
        ("", ["SM:ns:key1", "SM:ns:key2"])
    )

    await redis_storage.set("ns:key1", "1")
    await redis_storage.set("ns:key2", "2")
    await redis_storage.set("ms:key3", "3")

    assert list(await redis_storage.find_keys("ns:*")) == ["SM:ns:key1", "SM:ns:key2"]


@pytest.mark.asyncio
async def test_plugin_storage_wrapping(plugin_storage, redis_client):
    redis_client.set.expect(
        "SM:FakePlugin:ns:key1", dill.dumps("1"), expire=None
    ).returns(None)
    redis_client.set.expect(
        "SM:FakePlugin:ns:key2", dill.dumps("2"), expire=None
    ).returns(None)
    redis_client.set.expect(
        "SM:FakePlugin:ms:key3", dill.dumps("3"), expire=None
    ).returns(None)
    redis_client.scan.expect(cursor=b"0", match="SM:FakePlugin:ns:*").returns(
        ("", ["SM:FakePlugin:ns:key1", "SM:FakePlugin:ns:key2"])
    )

    await plugin_storage.set("ns:key1", "1")
    await plugin_storage.set("ns:key2", "2")
    await plugin_storage.set("ms:key3", "3")

    keys = list(await plugin_storage.find_keys("ns:*"))
    assert keys == ["SM:FakePlugin:ns:key1", "SM:FakePlugin:ns:key2"]

    redis_client.get.expect("SM:FakePlugin:ns:key1").returns(dill.dumps("1"))
    redis_client.get.expect("SM:FakePlugin:ns:key2").returns(dill.dumps("2"))

    for key in keys:
        assert await plugin_storage.get(key, shared=True) is not None
