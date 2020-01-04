from machine.utils.collections import CaseInsensitiveDict
from machine.utils import sizeof_fmt
from tests.singletons import FakeSingleton


def test_Singleton():
    c = FakeSingleton()
    c2 = FakeSingleton()
    assert c == c2


def test_CaseInsensitiveDict():
    d = CaseInsensitiveDict({'foo': 'bar'})
    assert 'foo' in d
    assert 'FoO' in d


def test_size_fmt():
    byte_size = 500
    assert sizeof_fmt(byte_size) == '500.0B'
    kb_size = 1124
    assert sizeof_fmt(kb_size) == '1.1KB'
    gb_size = 168963795964
    assert sizeof_fmt(gb_size) == '157.4GB'
