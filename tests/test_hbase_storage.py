import pytest
from happybase import Table

from machine.storage.backends.hbase import bytes_to_float, float_to_bytes, HBaseStorage

_VAL = b'values:value'
_EXP = b'values:expires_at'
_COLS = [_VAL, _EXP]


@pytest.fixture
def table(mocker):
    table = mocker.MagicMock(spec=Table)
    ConnectionCls = mocker.patch('machine.storage.backends.hbase.Connection', autospec=True)
    instance = ConnectionCls.return_value
    instance.table.return_value = table
    return table


@pytest.fixture
def hbase_storage(table):
    return HBaseStorage({'HBASE_HOST': 'foo', 'HBASE_TABLE': 'bar'})


def test_float_conversion():
    assert bytes_to_float(float_to_bytes(3.14159265359)) == 3.14159265359


def test_get(table, hbase_storage):
    hbase_storage.get('key1')
    table.row.assert_called_with('key1', _COLS)


def test_has(table, hbase_storage):
    hbase_storage.has('key1')
    table.row.assert_called_with('key1', _COLS)


def test_delete(table, hbase_storage):
    hbase_storage.delete('key1')
    table.delete.assert_called_with('key1')


def test_set(table, hbase_storage):
    hbase_storage.set('key1', 'val1')
    table.put.assert_called_with('key1', {b'values:value': 'val1'})
