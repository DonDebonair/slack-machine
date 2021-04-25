import logging
from typing import Callable, Dict, List
import asyncio

from slack.web.client import WebClient
from slack.rtm.client import RTMClient

from machine.models import User
from machine.models import Channel
from machine.settings import import_settings
from machine.utils import Singleton

logger = logging.getLogger(__name__)


def call_paginated_endpoint(endpoint: Callable, field: str, **kwargs) -> List:
    collection = []
    response = endpoint(limit=500, **kwargs)
    collection.extend(response[field])
    next_cursor = response['response_metadata'].get('next_cursor')
    while next_cursor:
        response = endpoint(limit=500, cursor=next_cursor, **kwargs)
        collection.extend(response[field])
        next_cursor = response['response_metadata'].get('next_cursor')
    return collection


class LowLevelSlackClient(metaclass=Singleton):
    def __init__(self):
        _settings, _ = import_settings()
        slack_api_token = _settings.get('SLACK_API_TOKEN', None)
        http_proxy = _settings.get('HTTP_PROXY', None)
        self.rtm_client = RTMClient(token=slack_api_token, proxy=http_proxy)
        self.web_client = WebClient(token=slack_api_token, proxy=http_proxy)
        self._bot_info = {}
        self._users = {}
        self._channels = {}

    @staticmethod
    def get_instance() -> 'LowLevelSlackClient':
        return LowLevelSlackClient()

    def _register_user(self, user_response):
        user = User.from_api_response(user_response)
        self._users[user.id] = user
        return user

    def _register_channel(self, channel_response):
        channel = Channel.from_api_response(channel_response)
        self._channels[channel.id] = channel
        return channel

    def ping(self):
        # Ugly hack because some parts of slackclient > 2.0 are async-only (like the ping function)
        # and Slack Machine isn't async yet
        loop = asyncio.new_event_loop()
        result = self.rtm_client.ping()
        loop.run_until_complete(result)

    def _on_open(self, **payload):
        # Set bot info
        self._bot_info = payload['data']['self']
        # Build user cache
        all_users = call_paginated_endpoint(self.web_client.users_list, 'members')
        for u in all_users:
            self._register_user(u)
        logger.debug("Number of users found: %s" % len(self._users))
        logger.debug("Users: %s" % ", ".join([f"{u.profile.display_name}|{u.profile.real_name}"
                                              for u in self._users.values()]))
        # Build channel cache
        all_channels = call_paginated_endpoint(self.web_client.conversations_list, 'channels',
                                               types='public_channel,private_channel,mpim,im')
        for c in all_channels:
            self._register_channel(c)
        logger.debug("Number of channels found: %s" % len(self._channels))
        logger.debug("Channels: %s" % ", ".join([c.identifier for c in self._channels.values()]))

    def _on_team_join(self, **payload):
        user = self._register_user(payload['data']['user'])
        logger.debug("User joined team: %s" % user)

    def _on_user_change(self, **payload):
        user = self._register_user(payload['data']['user'])
        logger.debug("User changed: %s" % user)

    def _on_channel_created(self, **payload):
        channel_resp = self.web_client.conversations_info(channel=payload['data']['channel']['id'])
        channel = self._register_channel(channel_resp['channel'])
        logger.debug("Channel created: %s" % channel)

    def _on_channel_updated(self, **payload):
        data = payload['data']
        if isinstance(data['channel'], dict):
            channel_id = data['channel']['id']
        else:
            channel_id = data['channel']
        channel_resp = self.web_client.conversations_info(channel=channel_id)
        channel = self._register_channel(channel_resp['channel'])
        logger.debug("Channel updated: %s" % channel)

    def _on_channel_deleted(self, **payload):
        channel = self._channels[payload['data']['channel']]
        del self._channels[payload['data']['channel']]
        logger.debug("Channel %s deleted" % channel.name)

    @property
    def bot_info(self) -> Dict[str, str]:
        return self._bot_info

    def start(self):
        RTMClient.on(event='open', callback=self._on_open)
        RTMClient.on(event='team_join', callback=self._on_team_join)
        RTMClient.on(event='channel_created', callback=self._on_channel_created)
        RTMClient.on(event='group_joined', callback=self._on_channel_created)
        RTMClient.on(event='mpim_joined', callback=self._on_channel_created)
        RTMClient.on(event='im_created', callback=self._on_channel_created)
        RTMClient.on(event='channel_deleted', callback=self._on_channel_deleted)
        RTMClient.on(event='im_close', callback=self._on_channel_deleted)
        RTMClient.on(event='channel_rename', callback=self._on_channel_updated)
        RTMClient.on(event='channel_archive', callback=self._on_channel_updated)
        RTMClient.on(event='channel_unarchive', callback=self._on_channel_updated)
        RTMClient.on(event='user_change', callback=self._on_user_change)
        self.rtm_client.start()

    @property
    def users(self) -> Dict[str, User]:
        return self._users

    @property
    def channels(self) -> Dict[str, Channel]:
        return self._channels
