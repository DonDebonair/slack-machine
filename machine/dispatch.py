import logging
import re
from typing import Any, Dict, Optional, List

from machine.clients.singletons.slack import LowLevelSlackClient
from machine.clients.slack import SlackClient
from machine.plugins.base import Message

logger = logging.getLogger(__name__)


class EventDispatcher:

    def __init__(self, plugin_actions, settings=None):
        self._client = LowLevelSlackClient()
        self._plugin_actions = plugin_actions
        alias_regex = ''
        if settings and "ALIASES" in settings:
            logger.info("Setting aliases to %s", settings['ALIASES'])
            alias_regex = '|(?P<alias>{})'.format(
                '|'.join([re.escape(s) for s in settings['ALIASES'].split(',')]))
        self.RESPOND_MATCHER = re.compile(
            r"^(?:<@(?P<atuser>\w+)>:?|(?P<username>\w+):{}) ?(?P<text>.*)$".format(
                alias_regex
            ),
            re.DOTALL,
        )

    def start(self):
        self._client.rtm_client.on('pong')(self.pong)
        self._client.rtm_client.on('message')(
            lambda client, event: self.handle_message(client, event))
        self._client.start()

    @staticmethod
    def pong(client, event):
        logger.debug("Server Pong!")

    def handle_message(self, client, event):
        # Handle message listeners
        # Handle message subtype 'message_changed' to allow the bot to respond to edits
        if 'subtype' in event and event['subtype'] == 'message_changed':
            event = event['message']
            event['channel'] = event.get('channel', '')
        if 'user' in event and not event['user'] == self._get_bot_id():
            listeners = self._find_listeners('listen_to')
            respond_to_msg = self._check_bot_mention(event)
            if respond_to_msg:
                listeners += self._find_listeners('respond_to')
                self._dispatch_listeners(listeners, respond_to_msg)
            else:
                self._dispatch_listeners(listeners, event)

    def _find_listeners(self, _type):
        return list(self._plugin_actions[_type].values())

    @staticmethod
    def _gen_message(event, plugin_class_name):
        return Message(SlackClient(), event, plugin_class_name)

    def _get_bot_id(self) -> str:
        return self._client.bot_info['user_id']

    def _get_bot_name(self) -> str:
        return self._client.bot_info['name']

    def _check_bot_mention(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        full_text = event.get('text', '')
        channel = event['channel']
        bot_name = self._get_bot_name()
        bot_id = self._get_bot_id()
        m = self.RESPOND_MATCHER.match(full_text)

        if channel[0] == 'C' or channel[0] == 'G':
            if not m:
                return None

            matches = m.groupdict()

            atuser = matches.get('atuser')
            username = matches.get('username')
            text = matches.get('text')
            alias = matches.get('alias')

            if alias:
                atuser = bot_id

            if atuser != bot_id and username != bot_name:
                # a channel message at other user
                return None

            event['text'] = text
        else:
            if m:
                event['text'] = m.groupdict().get('text', None)
        return event

    def _dispatch_listeners(self, listeners: List[Dict[str, Any]], event: Dict[str, Any]):
        for listener in listeners:
            matcher = listener['regex']
            match = matcher.search(event.get('text', ''))
            if match:
                message = self._gen_message(event, listener['class_name'])
                listener['function'](message, **match.groupdict())
