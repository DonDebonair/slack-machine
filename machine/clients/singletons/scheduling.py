from apscheduler.schedulers.background import BackgroundScheduler

from machine.settings import import_settings
from machine.utils import Singleton
from machine.utils.redis import gen_config_dict


class Scheduler(metaclass=Singleton):
    def __init__(self):
        _settings, _ = import_settings()
        self._scheduler = BackgroundScheduler()
        if 'REDIS_URL' in _settings:
            redis_config = gen_config_dict(_settings)
            self._scheduler.add_jobstore('redis', **redis_config)

    def __getattr__(self, item):
        return getattr(self._scheduler, item)

    @staticmethod
    def get_instance():
        return Scheduler()
