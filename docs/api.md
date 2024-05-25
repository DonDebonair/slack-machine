# API Documentation

This is the API documentation of all the classes and functions relevant for Plugin development. The rest of the code
deals with the internal workings of Slack Machine and is very much an implementation detail and subject to change.
Therefore it is not documented.

## Plugin classes

The following classes form the basis for Plugin development.

### ::: machine.plugins.base.MachineBasePlugin

------------------------------------------------------------------------

### ::: machine.plugins.message.Message

### ::: machine.plugins.command.Command

### ::: machine.plugins.block_action.BlockAction


## Decorators

These are the decorators you can use to have Slack Machine respond to
specific things (events, messages, etc.)

### ::: machine.plugins.decorators

## Models

These classes represent base objects from the Slack API

### ::: machine.models.user.User

### ::: machine.models.channel.Channel

## Storage

Storage is exposed to plugins through the `self.storage` field. The following class implements the interface plugins
can use to interact with the storage backend.

### ::: machine.storage.PluginStorage

------------------------------------------------------------------------

New *Storage Backends* can be implemented by extending the following
class:

### ::: machine.storage.backends.base.MachineBaseStorage
