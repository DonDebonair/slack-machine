# -*- coding: utf-8 -*-

import asyncio
import signal
import sys
import os
from functools import partial

from loguru import logger

from machine import Machine


def main():
    # When running this function as console entry point, the current working dir is not in the
    # Python path, so we have to add it
    sys.path.insert(0, os.getcwd())

    loop = asyncio.new_event_loop()

    # Handle INT and TERM by gracefully halting the event loop
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, partial(prepare_to_stop, loop))

    bot = Machine(loop=loop)
    loop.run_until_complete(bot.run())

    # Once `prepare_to_stop` returns, `loop` is guaranteed
    # to be stopped.
    prepare_to_stop(loop)

    loop.close()
    sys.exit(0)


def prepare_to_stop(loop: asyncio.AbstractEventLoop):
    # Calling `cancel` on each task in the active loop causes
    # a `CancelledError` to be thrown into each wrapped coroutine during
    # the next iteration, which _should_ halt execution of the coroutine
    # if the coroutine does not explicitly suppress the `CancelledError`.
    for task in asyncio.Task.all_tasks(loop=loop):
        task.cancel()

    # Using `ensure_future` on the `stop` coroutine here ensures that
    # the `stop` coroutine is the last thing to run after each cancelled
    # task has its `CancelledError` emitted.
    asyncio.ensure_future(stop(), loop=loop)
    loop.run_forever()


# @asyncio.coroutine
async def stop():
    loop = asyncio.get_event_loop()
    logger.info("Thanks for playing!")

    loop.stop()
