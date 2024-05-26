from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Union


@dataclass
class MatcherConfig:
    regex: re.Pattern[str]
    handle_changed_message: bool = False


@dataclass
class CommandConfig:
    command: str
    is_generator: bool = False


@dataclass
class ActionConfig:
    action_id: Union[re.Pattern[str], str, None] = None
    block_id: Union[re.Pattern[str], str, None] = None


@dataclass
class ModalConfig:
    callback_id: Union[re.Pattern[str], str]
    is_generator: bool = False


@dataclass
class PluginActions:
    process: list[str] = field(default_factory=list)
    listen_to: list[MatcherConfig] = field(default_factory=list)
    respond_to: list[MatcherConfig] = field(default_factory=list)
    schedule: dict[str, Any] | None = None
    commands: list[CommandConfig] = field(default_factory=list)
    actions: list[ActionConfig] = field(default_factory=list)
    modal_submissions: list[ModalConfig] = field(default_factory=list)
    modal_closures: list[ModalConfig] = field(default_factory=list)


@dataclass
class Metadata:
    plugin_actions: PluginActions = field(default_factory=PluginActions)
    required_settings: list[str] = field(default_factory=list)
