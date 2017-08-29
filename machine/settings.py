import os
import logging
from machine.utils.collections import CaseInsensitiveDict

logger = logging.getLogger(__name__)


def import_settings():
    default_settings = {
        'PLUGINS': ['machine.plugins.builtin.general.PingPongPlugin',
                    'machine.plugins.builtin.general.HelloPlugin']
    }
    settings = CaseInsensitiveDict(default_settings)
    try:
        import local_settings
        found_local_settings = True
    except ImportError as e:
        found_local_settings = False
    else:
        for k in dir(local_settings):
            if not k.startswith('_'):
                settings[k] = getattr(local_settings, k)

    for k, v in os.environ.items():
        if k[:8] == 'MACHINE_':
            k = k[8:]
            settings[k] = v

    return (settings, found_local_settings)
