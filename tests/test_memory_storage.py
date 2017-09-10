from datetime import datetime

import pytest

from machine.storage.backends.memory import MemoryStorage


@pytest.fixture
def memory_storage():
    return MemoryStorage({})


def test_store_retrieve_values(memory_storage):
    assert memory_storage._storage == {}
    memory_storage.set("key1", "value1")
    assert memory_storage._storage == {"key1": ("value1", None)}
    assert memory_storage.get("key1") == "value1"


def test_delete_values(memory_storage):
    assert memory_storage._storage == {}
    memory_storage.set("key1", "value1")
    memory_storage.set("key2", "value2")
    assert memory_storage._storage == {"key1": ("value1", None), "key2": ("value2", None)}
    memory_storage.delete("key2")
    assert memory_storage._storage == {"key1": ("value1", None)}

def test_expire_values(memory_storage, mocker):
    assert memory_storage._storage == {}
    mocked_dt = mocker.patch('machine.storage.backends.memory.datetime', autospec=True)
    mocked_dt.utcnow.return_value = datetime(2017, 1, 1, 12, 0, 0, 0)
    memory_storage.set("key1", "value1", expires=15)
    assert memory_storage._storage == {"key1": ("value1", datetime(2017, 1, 1, 12, 0, 15, 0))}
    assert memory_storage.get("key1") == "value1"
    mocked_dt.utcnow.return_value = datetime(2017, 1, 1, 12, 0, 20, 0)
    assert memory_storage.get("key1") == None

def test_inclusion(memory_storage):
    assert memory_storage._storage == {}
    memory_storage.set("key1", "value1")
    assert memory_storage.has("key1") == True
    memory_storage.delete("key1")
    assert memory_storage.has("key1") == False