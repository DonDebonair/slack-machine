from datetime import datetime, timedelta

from happybase import Connection
from machine.storage.backends.base import MachineBaseStorage


def bytes_to_float(byte_arr):
    s = byte_arr.decode('utf-8')
    return float(s)


def float_to_bytes(i):
    return bytes(str(i), 'utf-8')


class HBaseStorage(MachineBaseStorage):

    _VAL = b'values:value'
    _EXP = b'values:expires_at'
    _COLS = [_VAL, _EXP]

    def __init__(self, settings):
        super().__init__(settings)
        hbase_host = settings['HBASE_HOST']
        hbase_table = settings['HBASE_TABLE']
        self._connection = Connection(hbase_host)
        self._table = self._connection.table(hbase_table)

    def _get_value(self, key):
        row = self._table.row(key, self._COLS)
        val = row.get(self._VAL)
        if val:
            exp = row.get(self._EXP)
            if not exp:
                return val
            elif datetime.fromtimestamp(bytes_to_float(exp)) > datetime.utcnow():
                return val
            else:
                self.delete(key)
                return None
        return None

    def has(self, key):
        val = self._get_value(key)
        return bool(val)

    def get(self, key):
        return self._get_value(key)

    def set(self, key, value, expires=None):
        data = {self._VAL: value}
        if expires:
            expires_at = datetime.utcnow() + timedelta(seconds=expires)
            data[self._EXP] = float_to_bytes(expires_at.timestamp())
        self._table.put(key, data)

    def delete(self, key):
        self._table.delete(key)

    def size(self):
        return 0
