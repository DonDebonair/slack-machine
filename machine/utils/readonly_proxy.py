# -*- coding: utf-8 -*-

from typing import Any, Generic, T


class ReadonlyProxy(Generic[T]):
    __slots__ = "_target"

    def __init__(self, target: T):
        self._target = target

    def __getitem__(self, item: Any) -> Any:
        _target = getattr(self, "_target")
        return _target[item]

    def __getattr__(self, item: str) -> Any:
        return getattr(self._target, item)
