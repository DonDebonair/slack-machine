import re

from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import action, command, listen_to, process, respond_to


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

    @action(action_id=re.compile(r"my_action.*", re.IGNORECASE), block_id="my_block")
    async def block_action_function(self, payload):
        pass


class FakePlugin2(MachineBasePlugin):
    async def init(self):
        self.x = 42

    @listen_to(r"doit")
    async def another_listen_function(self, msg):
        pass
