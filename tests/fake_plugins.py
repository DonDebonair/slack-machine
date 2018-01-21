from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to, listen_to, process


class FakePlugin(MachineBasePlugin):

    @respond_to(r'hello')
    def respond_function(self, msg):
        pass

    @listen_to(r'hi')
    def listen_function(self, msg):
        pass

    @process('some_event')
    def process_function(self, event):
        pass

class FakePlugin2(MachineBasePlugin):

    def init(self):
        self.x = 42

    def catch_all(self, event):
        pass