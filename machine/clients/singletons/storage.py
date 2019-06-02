from machine.settings import import_settings
from machine.utils import Singleton
from machine.utils.module_loading import import_string


class Storage(metaclass=Singleton):
    def __init__(self):
        _settings, _ = import_settings()
        _, cls = import_string(_settings['STORAGE_BACKEND'])[0]
        self._storage = cls(_settings)

    def __getattr__(self, item):
        return getattr(self._storage, item)

    @staticmethod
    def get_instance():
        return Storage()
