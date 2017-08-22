import logging
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import listen_to, respond_to

logger = logging.getLogger(__name__)

class PingPongPlugin(MachineBasePlugin):

    @listen_to(r'^ping$')
    def listen_to_ping(self, msg):
        logger.debug("Ping received with msg: %s", msg)
        msg.send("pong")

    @listen_to(r'^pong$')
    def listen_to_pong(self, msg):
        logger.debug("Pong received with msg: %s", msg)
        msg.send("ping")

class HelloPlugin(MachineBasePlugin):

    @respond_to(r'^(?P<greeting>hi|hello)')
    def greet(self, msg, greeting):
        logger.debug("Greeting '%s' received", greeting)
        msg.send("{}, {}!".format(greeting.title(), msg.mention))
