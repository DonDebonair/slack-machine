import os
import pytest
import boto3
import time
import botocore
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


@pytest.fixture
def dynamodb_prebuilt_storage(dynamodb_storage):
    db = dynamodb_storage._db
    settings = {
        'DYNAMODB_CREATE_TABLE': True,
        'DYNAMODB_ENDPOINT_URL': 'http://dummy',
        'DYNAMODB_CLIENT': db
    }
    yield DynamoDBStorage(settings)


@pytest.fixture
def broken_storage():
    with mock_dynamodb2():
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'
        db = boto3.resource('dynamodb')
        settings = {
            'DYNAMODB_ENDPOINT_URL': 'http://dummy',
            'DYNAMODB_CLIENT': db
        }
        yield DynamoDBStorage(settings)


@pytest.fixture
def stock_storage():
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'
    settings = {
        'DYNAMODB_ENDPOINT_URL': 'http://dummy',
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


def test_client_error_has(broken_storage):
    with pytest.raises(botocore.exceptions.ClientError):
        broken_storage.has('key1')


def test_client_error_get(broken_storage):
    with pytest.raises(botocore.exceptions.ClientError):
        broken_storage.get('key1')


def test_client_error_set(broken_storage):
    with pytest.raises(botocore.exceptions.ClientError):
        broken_storage.set('key1', 'value1')


def test_client_error_delete(broken_storage):
    with pytest.raises(botocore.exceptions.ClientError):
        broken_storage.delete('key1')


def test_table_creation_exists(dynamodb_prebuilt_storage):
    assert dynamodb_prebuilt_storage.has('key1') == False


def test_invalid_table_name():
    with mock_dynamodb2():
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'
        db = boto3.resource('dynamodb')
        settings = {
            'DYNAMODB_CREATE_TABLE': True,
            'DYNAMODB_TABLE_NAME': 'aa',
            'DYNAMODB_ENDPOINT_URL': 'http://dummy',
            'DYNAMODB_CLIENT': db
        }
        with pytest.raises(botocore.exceptions.ParamValidationError):
            storage = DynamoDBStorage(settings)
