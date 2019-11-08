# -*- coding: utf-8 -*-

import asyncio
import concurrent
from functools import partial
from typing import Any, Callable, Coroutine, List, Optional, Sequence, Tuple, Type


async def join(tasks: Sequence[Coroutine]) -> List[Any]:
    """ Execute all of the coroutines, returning a list of responses
        or exceptions.
    """

    async def wrapper(future, idx):
        try:
            output = await future
            return idx, output
        except Exception as err:
            return idx, err

    output = [None] * len(tasks)
    tasks = [wrapper(future, idx) for idx, future in enumerate(tasks, start=0)]

    for future in asyncio.as_completed(tasks):
        idx, result = await future
        output[idx] = result

    return output


async def split(tasks: Sequence[Coroutine]) -> Tuple[List[Any], List[Type[Exception]]]:
    """ Execute all of the coroutines, returning a list of responses
        and a list of exceptions.
    """

    results = await join(tasks)

    return_values = []
    exceptions = []

    for res in results:
        if isinstance(res, Exception):
            exceptions.append(res)
        else:
            return_values.append(res)

    return return_values, exceptions


def run_coro_until_complete(
    coro: Coroutine, loop: Optional[asyncio.AbstractEventLoop] = None
) -> Any:
    if loop is None:
        loop = asyncio.get_event_loop()

    task = loop.create_task(coro)
    loop.run_until_complete(task)

    return task.result()


def run_in_threadpool(func: Callable[..., Any]) -> Callable[..., Any]:
    """ Makes any calls to a synchronous function happen in a
        `concurrent.futures.ThreadPoolExecutor` so that synchronous calls
        are not blocking the event loop.

        The wrapper function will await the `asyncio.Future` provided by
        `submit_to_threadpool`, which returns the wrapped return value directly
        to the caller.
    """

    async def inner(*args, **kw) -> Any:
        fn = partial(func, *args, **kw)
        fut = await submit_to_threadpool(fn)
        return await fut

    return inner


async def submit_to_threadpool(
    fn: Callable[..., Any],
    loop: Optional[asyncio.AbstractEventLoop] = None,
    executor: Optional[concurrent.futures.Executor] = None,
) -> asyncio.Future:
    """ Given a curried function, run it inside the given `loop` with `executor`, or,
        get the current event loop, create a new `concurrent.futures.ThreadPoolExecutor`
        with `max_workers=2`, and run the function there.

        Will not accept any function arguments or keyword arguments. Use `functools.partial`
        to curry the input function.

        Returns an `asyncio.Future` object which can be awaited.
    """

    if loop is None:
        loop = asyncio.get_event_loop()

    if executor is None:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    return loop.run_in_executor(executor, fn)


def build_executor(*args, **kw) -> concurrent.futures.ThreadPoolExecutor:
    return concurrent.futures.ThreadPoolExecutor(*args, **kw)
