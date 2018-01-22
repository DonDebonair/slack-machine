import logging
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import listen_to, respond_to

logger = logging.getLogger(__name__)


class PingPongPlugin(MachineBasePlugin):
    """Playing Ping Pong"""

    @listen_to(r'^ping$')
    def listen_to_ping(self, msg):
        """ping: serving the ball"""
        logger.debug("Ping received with msg: %s", msg)
        msg.say("pong")

    @listen_to(r'^pong$')
    def listen_to_pong(self, msg):
        """pong: returning the ball"""
        logger.debug("Pong received with msg: %s", msg)
        msg.say("ping")


class HelloPlugin(MachineBasePlugin):
    """Greetings"""

    @respond_to(r'^(?P<greeting>hi|hello)')
    def greet(self, msg, greeting):
        """hi/hello: say hello to the little guy"""
        logger.debug("Greeting '%s' received", greeting)
        msg.say("{}, {}!".format(greeting.title(), msg.at_sender))
