from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Callable, Any, Awaitable

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
    regex: re.Pattern[str]
    handle_message_changed: bool


@dataclass
class RegisteredActions:
    listen_to: dict[str, MessageHandler] = field(default_factory=dict)
    respond_to: dict[str, MessageHandler] = field(default_factory=dict)
    process: dict[str, dict[str, Callable[[dict[str, Any]], Awaitable[None]]]] = field(default_factory=dict)
