from machine.asyncio.plugins.base import MachineBasePlugin
from machine.asyncio.plugins.decorators import respond_to, listen_to, process


class FakePlugin(MachineBasePlugin):
    @respond_to(r"hello")
    async def respond_function(self, msg):
        pass

    @listen_to(r"hi")
    async def listen_function(self, msg):
        pass

    @process("some_event")
    async def process_function(self, event):
        pass


class FakePlugin2(MachineBasePlugin):
    def init(self):
        self.x = 42

    @listen_to(r"doit")
    async def another_listen_function(self, msg):
        pass
