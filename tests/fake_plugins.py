# -*- coding: utf-8 -*-
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to, listen_to, process


class FakePlugin(MachineBasePlugin):
    async def init(self, http_app):
        self.x = 42

    @respond_to(r"hello")
    async def respond_function(self, msg):
        pass

    @listen_to(r"hi")
    async def listen_function(self, msg):
        pass

    @process("some_event")
    async def process_function(self, event):
        pass
