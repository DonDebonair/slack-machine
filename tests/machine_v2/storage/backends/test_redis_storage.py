import pytest

from machine_v2.storage.backends.redis import RedisStorage


@pytest.fixture()
def redis_client(mocker):
    redis_client = mocker.async_stub(name="Redis")
    redis_client.set = mocker.async_stub(name="set")
    redis_client.get = mocker.async_stub(name="get")
    redis_client.has = mocker.async_stub(name="has")
    redis_client.exists = mocker.async_stub(name="exists")
    redis_client.delete = mocker.async_stub(name="delete")
    redis_client.info = mocker.async_stub(name="info")
    return redis_client


@pytest.fixture
def redis_storage(mocker, redis_client):
    settings = {'REDIS_URL': 'redis://nohost:1234'}
    storage = RedisStorage(settings)
    storage._redis = redis_client
    return storage


@pytest.mark.asyncio
async def test_set(redis_storage, redis_client):
    await redis_storage.set('key1', 'value1')
    redis_client.set.assert_called_with('SM:key1', 'value1', None)
    await redis_storage.set('key2', 'value2', 42)
    redis_client.set.assert_called_with('SM:key2', 'value2', 42)


@pytest.mark.asyncio
async def test_get(redis_storage, redis_client):
    await redis_storage.get('key1')
    redis_client.get.assert_called_with('SM:key1')


@pytest.mark.asyncio
async def test_has(redis_storage, redis_client):
    await redis_storage.has('key1')
    redis_client.exists.assert_called_with('SM:key1')


@pytest.mark.asyncio
async def test_delete(redis_storage, redis_client):
    await redis_storage.delete('key1')
    redis_client.delete.assert_called_with('SM:key1')


@pytest.mark.asyncio
async def test_size(redis_storage, redis_client):
    await redis_storage.size()
    redis_client.info.assert_called_with('memory')
