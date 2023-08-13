import os
from importlib import import_module
from typing import Tuple

from structlog.stdlib import get_logger

from machine.utils.collections import CaseInsensitiveDict

logger = get_logger(__name__)


def import_settings(settings_module: str = "local_settings") -> Tuple[CaseInsensitiveDict, bool]:
    default_settings = {
        "PLUGINS": [
            "machine.plugins.builtin.general.PingPongPlugin",
            "machine.plugins.builtin.general.HelloPlugin",
            "machine.plugins.builtin.help.HelpPlugin",
            "machine.plugins.builtin.fun.memes.MemePlugin",
        ],
        "STORAGE_BACKEND": "machine.storage.backends.memory.MemoryStorage",
        "HTTP_PROXY": None,
        "TZ": "UTC",
        "LOG_HANDLED_MESSAGES": True,
    }
    settings = CaseInsensitiveDict(default_settings)
    try:
        local_settings = import_module(settings_module)
        found_local_settings = True
    except ImportError:
        found_local_settings = False
    else:
        for k in dir(local_settings):
            if not k.startswith("_"):
                settings[k] = getattr(local_settings, k)

    for k, v in os.environ.items():
        if k[:3] == "SM_":
            k = k[3:]
            settings[k] = v

    return settings, found_local_settings
