# -*- coding: utf-8 -*-

import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, NewType
from unittest.mock import Mock

CoroutineFunction = NewType("CoroutineFunction", Callable[..., Awaitable])


def async_test(fn: CoroutineFunction):
    """ Wrapper around test methods, to allow them to be run async """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(fn)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


def coroutine_mock():
    """ Usable as a mock callable for patching async functions.
        From https://stackoverflow.com/a/32505333
    """

    coro = Mock(name="CoroutineResult")
    corofunc = Mock(name="CoroutineFunction", side_effect=asyncio.coroutine(coro))
    corofunc.coro = coro
    return corofunc


def make_coroutine_mock(return_value: Any):
    """ Returns an coroutine mock with the given return_value.
        The returned item is ready to be `await`ed
    """

    mock = coroutine_mock()
    mock.coro.return_value = return_value
    return mock()
