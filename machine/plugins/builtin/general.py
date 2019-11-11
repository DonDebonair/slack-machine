# -*- coding: utf-8 -*-

from loguru import logger

from machine.message import Message
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import listen_to, respond_to


class PingPongPlugin(MachineBasePlugin):
    """Playing Ping Pong"""

    @listen_to(r"^ping$")
    async def listen_to_ping(self, msg: Message):
        """ping: serving the ball"""
        logger.debug("Ping received with msg: {}", msg)
        await msg.say("pong")

    @listen_to(r"^pong$")
    async def listen_to_pong(self, msg: Message):
        """pong: returning the ball"""
        logger.debug("Pong received with msg: {}", msg)
        await msg.say("ping")


class HelloPlugin(MachineBasePlugin):
    """Greetings"""

    @respond_to(r"^(?P<greeting>hi|hello)")
    async def greet(self, msg, greeting):
        """hi/hello: say hello to the little guy"""
        logger.debug("Greeting '{}' received", greeting)
        await msg.say("{}, {}!".format(greeting.title(), msg.at_sender))
