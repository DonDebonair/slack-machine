# API Documentation (Async)

This is the API documentation of **async versions** of all the classes and functions relevant for Plugin development.
The rest of the code deals with the internal workings of Slack Machine and is very much an implementation detail and
subject to change. Therefore it is not documented.

## Plugin classes

The following 2 classes form the basis for Plugin development.

### ::: machine.asyncio.plugins.base.MachineBasePlugin

------------------------------------------------------------------------

### ::: machine.asyncio.plugins.base.Message


## Decorators

These are the decorators you can use to have Slack Machine respond to
specific things (events, messages, etc.)

### ::: machine.asyncio.plugins.decorators

## Models

These classes represent base objects from the Slack API

### ::: machine.asyncio.models.user.User

### ::: machine.asyncio.models.channel.Channel

## Storage

Storage is exposed to plugins through the `self.storage` field. The
following class implements the interface plugins can use to interact
with the storage backend.

### ::: machine.asyncio.storage.PluginStorage

------------------------------------------------------------------------

New *Storage Backends* can be implemented by extending the following
class:

### ::: machine.asyncio.storage.backends.base.MachineBaseStorage
