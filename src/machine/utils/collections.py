from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from typing import TypeVar, cast

KT = TypeVar("KT", bound=str)
VT = TypeVar("VT")


class CaseInsensitiveDict(MutableMapping[KT, VT]):
    """
    A case-insensitive ``dict``-like object.
    Implements all methods and operations of
    ``collections.MutableMapping`` as well as dict's ``copy``. Also
    provides ``lower_items``.
    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case insensitive:
        cid = CaseInsensitiveDict()
        cid['Accept'] = 'application/json'
        cid['aCCEPT'] == 'application/json'  # True
        list(cid) == ['Accept']  # True
    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header, regardless
    of how the header name was originally stored.
    If the constructor, ``.update``, or equality comparison
    operations are given keys that have equal ``.lower()``s, the
    behavior is undefined.

    This class was copied from the ``requests`` package and made type-safe
    The original can be found at:
    https://github.com/requests/requests/blob/v1.2.3/requests/structures.py#L37
    """

    def __init__(self, data: Mapping[KT, VT] | Iterable[tuple[KT, VT]] | None = None, **kwargs: VT):
        self._store: dict[KT, tuple[KT, VT]] = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    @staticmethod
    def _convert_key(key: KT) -> KT:
        lower_key = cast(KT, key.lower())
        return lower_key

    def __setitem__(self, key: KT, value: VT) -> None:
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[self._convert_key(key)] = (key, value)

    def __getitem__(self, key: KT) -> VT:
        return self._store[self._convert_key(key)][1]

    def __delitem__(self, key: KT) -> None:
        del self._store[self._convert_key(key)]

    def __iter__(self) -> Iterator[KT]:
        return (casedkey for casedkey, _ in self._store.values())

    def __len__(self) -> int:
        return len(self._store)

    def lower_items(self) -> Iterator[tuple[KT, VT]]:
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for (lowerkey, keyval) in self._store.items())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self) -> CaseInsensitiveDict[KT, VT]:
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict(self.items())!r})"
