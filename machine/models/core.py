from __future__ import annotations

import re
from dataclasses import dataclass, field
from inspect import Signature
from typing import Any, AsyncGenerator, Awaitable, Callable, Union

from slack_sdk.models import JsonObject

from machine.plugins.base import MachineBasePlugin


@dataclass
class HumanHelp:
    command: str
    help: str


@dataclass
class Manual:
    human: dict[str, dict[str, HumanHelp]]
    robot: dict[str, list[str]]


@dataclass
class MessageHandler:
    class_: MachineBasePlugin
    class_name: str
    function: Callable[..., Awaitable[None]]
    function_signature: Signature
    regex: re.Pattern[str]
    handle_message_changed: bool


@dataclass
class CommandHandler:
    class_: MachineBasePlugin
    class_name: str
    function: Callable[..., Awaitable[None] | AsyncGenerator[dict | JsonObject | str, None]]
    function_signature: Signature
    command: str
    is_generator: bool


@dataclass
class BlockActionHandler:
    class_: MachineBasePlugin
    class_name: str
    function: Callable[..., Awaitable[None]]
    function_signature: Signature
    action_id_matcher: Union[re.Pattern[str], str, None]
    block_id_matcher: Union[re.Pattern[str], str, None]


@dataclass
class RegisteredActions:
    listen_to: dict[str, MessageHandler] = field(default_factory=dict)
    respond_to: dict[str, MessageHandler] = field(default_factory=dict)
    process: dict[str, dict[str, Callable[[dict[str, Any]], Awaitable[None]]]] = field(default_factory=dict)
    command: dict[str, CommandHandler] = field(default_factory=dict)
    block_actions: dict[str, BlockActionHandler] = field(default_factory=dict)


def action_block_id_to_str(id_: Union[str, re.Pattern[str], None]) -> str:
    if id_ is None:
        return "*"
    elif isinstance(id_, str):
        return id_
    else:
        return id_.pattern
