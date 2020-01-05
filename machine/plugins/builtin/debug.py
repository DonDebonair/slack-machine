import logging
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import process

logger = logging.getLogger(__name__)


class EchoPlugin(MachineBasePlugin):

    @process(slack_event_type='message')
    def echo_message(self, event):
        logger.debug("Message received: %s", event)
        if 'subtype' not in event or (
                event['subtype'] != 'bot_message' and event['subtype'] != 'message_replied'):
            if 'thread_ts' in event:
                thread_ts = event['thread_ts']
            else:
                thread_ts = None
            self.say(event['channel'], event['text'], thread_ts=thread_ts)
