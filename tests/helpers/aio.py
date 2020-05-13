# -*- coding: utf-8 -*-

import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, NewType
from unittest.mock import MagicMock

CoroutineFunction = NewType("CoroutineFunction", Callable[..., Awaitable])


def make_awaitable_result(return_value: Any):
    fut = asyncio.Future()
    if isinstance(return_value, Exception):
        fut.set_exception(return_value)
    else:
        fut.set_result(return_value)

    return fut
