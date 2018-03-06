import os
import logging
from importlib import import_module
from machine.utils.collections import CaseInsensitiveDict

logger = logging.getLogger(__name__)


def import_settings(settings_module='local_settings'):
    default_settings = {
        'PLUGINS': ['machine.plugins.builtin.general.PingPongPlugin',
                    'machine.plugins.builtin.general.HelloPlugin',
                    'machine.plugins.builtin.help.HelpPlugin',
                    'machine.plugins.builtin.fun.memes.MemePlugin'],
        'STORAGE_BACKEND': 'machine.storage.backends.memory.MemoryStorage',
        'DISABLE_HTTP': False,
        'HTTP_SERVER_BACKEND': 'wsgiref'
    }
    settings = CaseInsensitiveDict(default_settings)
    try:
        local_settings = import_module(settings_module)
        found_local_settings = True
    except ImportError:
        found_local_settings = False
    else:
        for k in dir(local_settings):
            if not k.startswith('_'):
                settings[k] = getattr(local_settings, k)

    for k, v in os.environ.items():
        if k[:3] == 'SM_':
            k = k[3:]
            settings[k] = v

    return (settings, found_local_settings)


globals().update(import_settings()[0])
