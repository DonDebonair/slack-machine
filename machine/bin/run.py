import asyncio
import os
import sys

from structlog.stdlib import get_logger

from machine import Machine

logger = get_logger(__name__)


def main() -> None:
    # When running this function as console entry point, the current working dir is not in the
    # Python path, so we have to add it
    sys.path.insert(0, os.getcwd())
    bot = Machine()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        loop.run_until_complete(bot.close())
        loop.close()
        logger.info("Thanks for playing!")
        sys.exit(0)
