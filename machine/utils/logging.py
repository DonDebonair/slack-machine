from __future__ import annotations

import logging
import sys
from typing import Any, Mapping

import structlog
from structlog.processors import CallsiteParameter
from structlog.types import Processor


def configure_logging(settings: Mapping[str, Any]) -> None:
    """
    Configure logging with structlog. This function will configure structlog to use the right processors to add
    revelant metadata to the logs, such as timestamp, source file, line number, and function name.
    Next to that, it will configure all standard logging handlers to use structlog for formatting.
    :return: None
    """

    # These processors are used both by the logs generated through structlog as well as the logs generated through
    # the stdlib logging module (incl. logs from third-party packages)
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder([
            CallsiteParameter.FILENAME,
            CallsiteParameter.FUNC_NAME,
            CallsiteParameter.LINENO,
        ]),
    ]
    # Configure structlog itself
    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        context_class=dict,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    # Create a formatter. Use Console renderer in terminal and JSON renderer when running in container
    renderer: Processor
    if sys.stdout.isatty():  # noqa: SIM108 (doesn't work with mypy)
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    # All logging is going to be rendered by the stdlib logging module
    handler = logging.StreamHandler()
    # Use OUR `ProcessorFormatter` to format all `logging` entries.
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    # We want to get rid of their pre-configured log handlers
    for h in root_logger.handlers:
        root_logger.removeHandler(h)
    root_logger.addHandler(handler)
    level_str = settings.get("LOGLEVEL", "ERROR")
    # Get level as int so we can compare it
    level = logging.getLevelName(level_str)
    root_logger.setLevel(level)
    if level < logging.INFO:
        logging.getLogger("slack_sdk.socket_mode.aiohttp").setLevel(logging.INFO)
        logging.getLogger("slack_sdk.web.async_base_client").setLevel(logging.INFO)
