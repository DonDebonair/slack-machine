from apscheduler.schedulers.background import BackgroundScheduler
from slackclient import SlackClient
from machine.settings import import_settings
from machine.utils import Singleton
from machine.utils.module_loading import import_string
from machine.utils.redis import gen_config_dict


class Slack(metaclass=Singleton):
    def __init__(self):
        _settings, _ = import_settings()
        slack_api_token = _settings.get('SLACK_API_TOKEN', None)
        http_proxy = _settings.get('HTTP_PROXY', None)
        https_proxy = _settings.get('HTTPS_PROXY', None)
        proxies = {'http': http_proxy, 'https': https_proxy}

        self._client = SlackClient(slack_api_token, proxies=proxies) if slack_api_token else None

    def __getattr__(self, item):
        return getattr(self._client, item)

    @staticmethod
    def get_instance():
        return Slack()


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
