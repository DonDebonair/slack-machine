import os
import pytest
import boto3
import time
from moto import mock_dynamodb2
from machine.storage.backends.dynamodb import DynamoDBStorage


@pytest.fixture
def dynamodb_storage():
    with mock_dynamodb2():
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'
        db = boto3.resource('dynamodb')
        settings = {
            'DYNAMODB_CREATE_TABLE': True,
            'DYNAMODB_ENDPOINT_URL': 'http://dummy',
            'DYNAMODB_CLIENT': db
        }
        yield DynamoDBStorage(settings)


def test_store_retrieve_values(dynamodb_storage):
    assert dynamodb_storage.get('key_invalid') is None
    dynamodb_storage.set('key1', 'value1')
    assert dynamodb_storage.get('key1') == 'value1'
    dynamodb_storage.set('key2', 'value2', 2)
    assert dynamodb_storage.get('key2') == 'value2'
    r = dynamodb_storage._table.get_item(Key={'sm-key': dynamodb_storage._prefix('key2')})
    assert r['Item']['sm-expire'] > 0


def test_has(dynamodb_storage):
    dynamodb_storage.set('key1', 'value1')
    assert dynamodb_storage.has('key1')
    assert dynamodb_storage.has('key2') == False


def test_delete(dynamodb_storage):
    dynamodb_storage.set('key1', 'value1')
    assert dynamodb_storage.has('key1')
    assert dynamodb_storage.get('key1') == 'value1'
    dynamodb_storage.delete('key1')
    assert dynamodb_storage.has('key1') == False


def test_size(dynamodb_storage):
    assert isinstance(dynamodb_storage.size(), int)
