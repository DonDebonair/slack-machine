from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to, listen_to, process, command


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

    @command("/test")
    async def command_function(self, payload):
        pass

    @command("/test-generator")
    async def generator_command_function(self, payload):
        yield "hello"


class FakePlugin2(MachineBasePlugin):
    def init(self):
        self.x = 42

    @listen_to(r"doit")
    async def another_listen_function(self, msg):
        pass
