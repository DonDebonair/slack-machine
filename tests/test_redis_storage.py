# -*- coding: utf-8 -*-

from unittest import mock

import aioredis
import pytest

from machine.storage.backends.redis import RedisStorage

from tests.helpers import async_test, make_coroutine_mock
from tests.helpers.expect import ExpectMock, expect


@pytest.fixture(scope="module")
def redis_client():
    return ExpectMock(spec=aioredis.Redis)


@pytest.fixture
def redis_storage(expect, redis_client):
    create_redis_pool = mock.patch(
        "machine.storage.backends.redis.aioredis.create_redis_pool"
    )
    create_redis_pool.return_value = redis_client
    settings = {"REDIS_URL": "redis://nohost:1234"}
    storage = RedisStorage(settings)
    storage._redis = redis_client
    return storage


@async_test
async def test_set(redis_storage, redis_client):
    redis_client.set.expect("SM:key1", "value1", expire=None).returns(
        make_coroutine_mock(None)
    )
    redis_client.set.expect("SM:key2", "value2", expire=42).returns(
        make_coroutine_mock(None)
    )

    await redis_storage.set("key1", "value1", expires=None)
    await redis_storage.set("key2", "value2", expires=42)


@async_test
async def test_get(redis_storage, redis_client):
    redis_client.get.expect("SM:key1").returns(make_coroutine_mock(None))

    await redis_storage.get("key1")


@async_test
async def test_has(redis_storage, redis_client):
    redis_client.exists.expect("SM:key1").returns(make_coroutine_mock(None))

    await redis_storage.has("key1")


@async_test
async def test_delete(redis_storage, redis_client):
    redis_client.delete.expect("SM:key1").returns(make_coroutine_mock(None))

    await redis_storage.delete("key1")


@async_test
async def test_size(redis_storage, redis_client):
    redis_client.info.expect("memory").returns(
        make_coroutine_mock({"used_memory": "haha all of it"})
    )

    await redis_storage.size()
