import logging
from typing import Callable, Dict, List

from slack_sdk.web.client import WebClient
from slack_sdk.rtm_v2 import RTMClient

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
        self._channels: Dict[str, Channel] = {}

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
        self.rtm_client.current_session.ping()

    def _on_hello(self, client: RTMClient, payload, *rest):
        # Set bot info
        self._bot_info = self.web_client.bots_info(bot=self.rtm_client.bot_id)['bot']
        # Build user cache
        all_users = call_paginated_endpoint(self.web_client.users_list, 'members')
        for u in all_users:
            self._register_user(u)
        logger.debug("Number of users found: %s", len(self._users))
        logger.debug("Users: %s", ", ".join([f"{u.profile.display_name}|{u.profile.real_name}"
                                             for u in self._users.values()]))
        # Build channel cache
        all_channels = call_paginated_endpoint(self.web_client.conversations_list, 'channels',
                                               types='public_channel,private_channel,mpim,im')
        for c in all_channels:
            self._register_channel(c)
        logger.debug("Number of channels found: %s", len(self._channels))
        logger.debug("Channels: %s", ", ".join([c.identifier for c in self._channels.values()]))

    def _on_team_join(self, client, payload):
        logger.debug("team_join: %s", payload)
        user = self._register_user(payload['user'])
        logger.debug("User joined team: %s", user)

    def _on_user_change(self, client, payload):
        logger.debug("user_change: %s", payload)
        user = self._register_user(payload['user'])
        logger.debug("User changed: %s", user)

    def _on_channel_created(self, client, payload):
        logger.debug("channel_created/group_joined/im_created: %s", payload)
        channel_resp = self.web_client.conversations_info(channel=payload['channel']['id'])
        channel = self._register_channel(channel_resp['channel'])
        logger.debug("Channel created: %s", channel)

    def _on_channel_updated(self, client, payload):
        logger.debug("channel_rename/channel_archive/channel_unarchive/"
                     "group_rename/group_archive/group_unarchive: %s", payload)
        if isinstance(payload['channel'], dict):
            channel_id = payload['channel']['id']
        else:
            channel_id = payload['channel']
        channel_resp = self.web_client.conversations_info(channel=channel_id)
        channel = self._register_channel(channel_resp['channel'])
        logger.debug("Channel updated: %s", channel)

    def _on_channel_deleted(self, client, payload):
        logger.debug("channel_deleted/im_close: %s", payload)
        channel = self._channels[payload['channel']]
        del self._channels[payload['channel']]
        logger.debug("Channel %s deleted", channel.name)

    def _on_member_left_channel(self, client, payload):
        logger.debug("member_left_channel: %s", payload)
        channel = self._channels[payload['channel']]
        channel._members.remove(payload['user'])
        logger.debug('Member left channel %s', channel.name)

    def _on_member_joined_channel(self, client, payload):
        logger.debug("member_joined_channel: %s", payload)
        channel = self._channels[payload['channel']]
        # Since the member list is cached on first query, only update the cache if the list has been
        # retrieved at least once.
        if channel._members:
            channel._members.append(payload['user'])
        logger.debug('Member joined %s', channel.name)

    def _on_channel_id_changed(self, client, payload):
        logger.debug("channel_id_changed: %s", payload)
        channel = self._channels[payload['old_channel_id']]
        self._channels[payload['new_channel_id']] = channel
        del self._channels[payload['old_channel_id']]

    @property
    def bot_info(self) -> Dict[str, str]:
        return self._bot_info

    def start(self):
        self.rtm_client.on('hello')(lambda client, event: self._on_hello(client, event))
        self.rtm_client.on('team_join')(lambda client, event: self._on_team_join(client, event))
        self.rtm_client.on('channel_created')(
            lambda client, event: self._on_channel_created(client, event))
        self.rtm_client.on('group_joined')(
            lambda client, event: self._on_channel_created(client, event))
        self.rtm_client.on('im_created')(
            lambda client, event: self._on_channel_created(client, event))
        self.rtm_client.on('channel_deleted')(
            lambda client, event: self._on_channel_deleted(client, event))
        self.rtm_client.on('im_close')(
            lambda client, event: self._on_channel_deleted(client, event))
        self.rtm_client.on('group_deleted')(
            lambda client, event: self._on_channel_deleted(client, event))
        self.rtm_client.on('channel_rename')(
            lambda client, event: self._on_channel_updated(client, event))
        self.rtm_client.on('channel_archive')(
            lambda client, event: self._on_channel_updated(client, event))
        self.rtm_client.on('channel_unarchive')(
            lambda client, event: self._on_channel_updated(client, event))
        self.rtm_client.on('group_rename')(
            lambda client, event: self._on_channel_updated(client, event))
        self.rtm_client.on('group_archive')(
            lambda client, event: self._on_channel_updated(client, event))
        self.rtm_client.on('group_unarchive')(
            lambda client, event: self._on_channel_updated(client, event))
        self.rtm_client.on('member_joined_channel')(
            lambda client, event: self._on_member_joined_channel(client, event))
        self.rtm_client.on('member_left_channel')(
            lambda client, event: self._on_member_left_channel(client, event))
        self.rtm_client.on('user_change')(lambda client, event: self._on_user_change(client, event))
        self.rtm_client.on('channel_id_changed')(
            lambda client, event: self._on_channel_id_changed(client, event))
        self.rtm_client.start()

    @property
    def users(self) -> Dict[str, User]:
        return self._users

    @property
    def channels(self) -> Dict[str, Channel]:
        return self._channels
