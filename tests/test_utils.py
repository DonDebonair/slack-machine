from machine.utils.collections import CaseInsensitiveDict
from tests.singletons import FakeSingleton


def test_Singleton():
    c = FakeSingleton()
    c2 = FakeSingleton()
    assert c == c2

def test_CaseInsensitiveDict():
    d = CaseInsensitiveDict({'foo': 'bar'})
    assert 'foo' in d
    assert 'FoO' in d