import os
from machine.utils.collections import CaseInsensitiveDict

def import_settings():
    default_settings = {
        'PLUGINS': ['machine.plugins.builtin.general.DebugPlugin',
                    'machine.plugins.builtin.general.MessagePrintPlugin']
    }
    settings = CaseInsensitiveDict(default_settings)
    try:
        import local_settings
        print("local_settings found!")
    except ImportError:
        print("No local_settings found!")
    else:
        for k in dir(local_settings):
            if not k.startswith('_'):
                settings[k] = getattr(local_settings, k)

    for k,v in os.environ.items():
        if k[:8] == 'MACHINE_':
            k = k[8:]
            settings[k] = v

    return settings