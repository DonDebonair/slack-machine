from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Callable

from machine_v2.plugins.base import MachineBasePlugin


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
    function: Callable[..., None]
    regex: re.Pattern[str]


@dataclass
class RegisteredActions:
    listen_to: dict[str, MessageHandler] = field(default_factory=dict)
    respond_to: dict[str, MessageHandler] = field(default_factory=dict)
    process: dict[str, dict[str, Callable[[str], None]]] = field(default_factory=dict)
