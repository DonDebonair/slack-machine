from unittest.mock import MagicMock

import pytest
from redis import StrictRedis

from machine.storage.backends.redis import RedisStorage

@pytest.fixture(scope='module')
def redis_client():
    return MagicMock(spec=StrictRedis)

@pytest.fixture
def redis_storage(mocker, redis_client):
    mocker.patch('machine.storage.backends.redis.StrictRedis', autospec=True)
    settings = {'REDIS_URL': 'redis://nohost:1234'}
    storage = RedisStorage(settings)
    storage._redis = redis_client
    return storage

def test_set(redis_storage, redis_client):
    redis_storage.set('key1', 'value1')
    redis_client.set.assert_called_with('SM:key1', 'value1', None)
    redis_storage.set('key2', 'value2', 42)
    redis_client.set.assert_called_with('SM:key2', 'value2', 42)

def test_get(redis_storage, redis_client):
    redis_storage.get('key1')
    redis_client.get.assert_called_with('SM:key1')

def test_has(redis_storage, redis_client):
    redis_storage.has('key1')
    redis_client.exists.assert_called_with('SM:key1')

def test_delete(redis_storage, redis_client):
    redis_storage.delete('key1')
    redis_client.delete.assert_called_with('SM:key1')

def test_size(redis_storage, redis_client):
    redis_storage.size()
    redis_client.info.assert_called_with('memory')
