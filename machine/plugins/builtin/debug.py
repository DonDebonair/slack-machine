import logging
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import process

logger = logging.getLogger(__name__)


class EchoPlugin(MachineBasePlugin):

    @process(slack_event_type='message')
    def echo_message(self, event):
        logger.debug("Message received: %s", event)
        self.say(event['channel'], event['text'])
