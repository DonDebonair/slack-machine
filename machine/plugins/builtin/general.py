from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import process

class DebugPlugin(MachineBasePlugin):

    def catch_all(self, event):
        print("Event received: {}".format(event))

class MessagePrintPlugin(MachineBasePlugin):

    @process(event_type='message')
    def print_message_event(self, event):
        print("Message received: {}".format(event))