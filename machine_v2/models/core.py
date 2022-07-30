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
    listen_to: list[MessageHandler] = field(default_factory=list)
    respond_to: list[MessageHandler] = field(default_factory=list)
    process: dict[str, list[Callable[[str], None]]] = field(default_factory=dict)
