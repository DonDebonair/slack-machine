# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slack import RTMClient, WebClient

from machine.utils import Singleton
from machine.utils.module_loading import import_string
from machine.utils.readonly_proxy import ReadonlyProxy
from machine.utils.redis import gen_config_dict


class Slack(metaclass=Singleton):
    __slots__ = "_login_data", "_rtm_client", "_web_client"

    def __init__(
        self, settings: dict = None, loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        if not loop:
            loop = asyncio.get_event_loop()

        if settings is None:
            raise ValueError("Expected a settings dictionary, got None")

        slack_api_token = settings.get("SLACK_API_TOKEN", None)
        http_proxy = settings.get("HTTP_PROXY", None)
        https_proxy = settings.get("HTTPS_PROXY", None)

        self._login_data = None
        self._rtm_client = RTMClient(
            token=slack_api_token,
            run_async=True,
            auto_reconnect=True,
            proxy=https_proxy or http_proxy or None,
            loop=loop,
        )
        self._web_client = WebClient(slack_api_token, run_async=True, loop=loop)

        @RTMClient.run_on(event="open")
        def _store_login_data(**payload):
            self._login_data = payload["data"]

    @property
    def login_data(self) -> ReadonlyProxy[dict]:
        return ReadonlyProxy(self._login_data or {})

    @property
    def rtm(self) -> ReadonlyProxy[RTMClient]:
        return ReadonlyProxy(self._rtm_client)

    @property
    def web(self) -> ReadonlyProxy[WebClient]:
        return ReadonlyProxy(self._web_client)

    @staticmethod
    def get_instance() -> Slack:
        return Slack()


class Scheduler(metaclass=Singleton):
    """ Configures an `asyncio`-compatible scheduler instance.
    """

    def __init__(
        self, settings: dict = None, loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        if not loop:
            loop = asyncio.get_event_loop()

        if settings is None:
            raise ValueError("Expected a settings dictionary, got None")

        self._scheduler = AsyncIOScheduler(event_loop=loop)
        if "REDIS_URL" in settings:
            redis_config = gen_config_dict(settings)
            self._scheduler.add_jobstore("redis", **redis_config)

    def __getattr__(self, item):
        return getattr(self._scheduler, item)

    @staticmethod
    def get_instance() -> Scheduler:
        return Scheduler()


class Storage(metaclass=Singleton):
    def __init__(self, settings: dict = None):
        if settings is None:
            raise ValueError("Expected a settings dictionary, got None")

        _, cls = import_string(settings["STORAGE_BACKEND"])[0]
        self._storage = cls(settings)

    def __getattr__(self, item):
        return getattr(self._storage, item)

    @staticmethod
    def get_instance():
        return Storage()
