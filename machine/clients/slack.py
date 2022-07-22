import logging
from datetime import datetime
from typing import Dict, Union

from machine.clients.singletons.scheduling import Scheduler
from machine.models import User
from machine.models.channel import Channel
from machine.clients.singletons.slack import LowLevelSlackClient

from slack_sdk.models import extract_json

logger = logging.getLogger(__name__)


def id_for_user(user: Union[User, str]) -> str:
    if isinstance(user, User):
        return user.id
    else:
        return user


def id_for_channel(channel: Union[Channel, str]) -> str:
    if isinstance(channel, Channel):
        return channel.id
    else:
        return channel


class SlackClient:
    @property
    def bot_info(self) -> Dict[str, str]:
        return LowLevelSlackClient.get_instance().bot_info

    @property
    def users(self) -> Dict[str, User]:
        return LowLevelSlackClient.get_instance().users

    @property
    def channels(self) -> Dict[str, Channel]:
        return LowLevelSlackClient.get_instance().channels

    def send(self, channel: Union[Channel, str], text: str, **kwargs):
        channel_id = id_for_channel(channel)
        if 'attachments' in kwargs and kwargs['attachments'] is not None:
            kwargs['attachments'] = extract_json(kwargs['attachments'])
        if 'blocks' in kwargs and kwargs['blocks'] is not None:
            kwargs['blocks'] = extract_json(kwargs['blocks'])
        if 'ephemeral_user' in kwargs and kwargs['ephemeral_user'] is not None:
            ephemeral_user_id = id_for_user(kwargs['ephemeral_user'])
            del kwargs['ephemeral_user']
            return LowLevelSlackClient.get_instance().web_client.chat_postEphemeral(
                channel=channel_id,
                user=ephemeral_user_id,
                text=text,
                **kwargs
            )
        else:
            return LowLevelSlackClient.get_instance().web_client.chat_postMessage(
                channel=channel_id,
                text=text,
                **kwargs
            )

    def send_scheduled(self, when: datetime, channel: Union[Channel, str], text: str, **kwargs):
        args = [self, channel, text]

        Scheduler.get_instance().add_job(SlackClient.send, trigger='date', args=args,
                                         kwargs=kwargs, run_date=when)

    def react(self, channel: Union[Channel, str], ts: str, emoji: str):
        channel_id = id_for_channel(channel)
        return LowLevelSlackClient.get_instance().web_client.reactions_add(name=emoji,
                                                                           channel=channel_id,
                                                                           timestamp=ts)

    def open_im(self, user: Union[User, str]) -> str:
        user_id = id_for_user(user)
        response = LowLevelSlackClient.get_instance().web_client.conversations_open(users=user_id)
        return response['channel']['id']

    def send_dm(self, user: Union[User, str], text: str, **kwargs):
        user_id = id_for_user(user)
        dm_channel_id = self.open_im(user_id)

        return LowLevelSlackClient.get_instance().web_client.chat_postMessage(
            channel=dm_channel_id,
            text=text,
            as_user=True,
            **kwargs
        )

    def send_dm_scheduled(self, when: datetime, user, text: str, **kwargs):
        args = [self, user, text]

        Scheduler.get_instance().add_job(SlackClient.send_dm, trigger='date', args=args,
                                         kwargs=kwargs, run_date=when)
