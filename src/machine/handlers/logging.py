from typing import Any

from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from structlog.stdlib import BoundLogger, get_logger

logger = get_logger(__name__)


async def log_request(_: AsyncBaseSocketModeClient, request: SocketModeRequest) -> None:
    logger.debug(
        "Request received",
        type=request.type,
        request=request.to_dict(),
        accepts_response_payload=request.accepts_response_payload,
    )


def create_scoped_logger(class_name: str, function_name: str, **kwargs: Any) -> BoundLogger:
    """
    Create a scope logger for a plugin handler
    :param class_name: The name of the class that contains the handler
    :param function_name: The name of the handler function
    :param kwargs: Additional context to bind to the logger
    """
    fq_fn_name = f"{class_name}.{function_name}"
    handler_logger = get_logger(fq_fn_name)
    handler_logger = handler_logger.bind(**kwargs)
    return handler_logger
