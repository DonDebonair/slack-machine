import logging
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import process

logger = logging.getLogger(__name__)


class EventLoggerPlugin(MachineBasePlugin):

    def catch_all(self, event):
        logger.debug("Event received: %s", event)


class EchoPlugin(MachineBasePlugin):

    @process(slack_event_type='message')
    def echo_message(self, event):
        logger.debug("Message received: %s", event)
        self.say(event['channel'], event['text'])
