import logging
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import process, listen_to

logger = logging.getLogger(__name__)

class DebugPlugin(MachineBasePlugin):

    def catch_all(self, event):
        logger.debug("Event received: {}".format(event))

class EchoPlugin(MachineBasePlugin):

    @process(event_type='message')
    def echo_message(self, event):
        logger.debug("Message received: {}".format(event))
        self.send(event['channel'], event['text'])

class PingPongPlugin(MachineBasePlugin):

    @listen_to(r'^ping')
    def listen_to_ping(self, msg):
        logger.debug("Ping received with msg: %s", msg)
        msg.send("pong")

    @listen_to(r'^pong')
    def listen_to_pong(self, msg):
        logger.debug("Pong received with msg: %s", msg)
        msg.send("ping")