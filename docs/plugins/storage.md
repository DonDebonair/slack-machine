# Storage

Slack Machine provides persistent storage that can easily be accessed from plugins through `self.storage`. This field
contains an instance of [`PluginStorage`][machine.storage.PluginStorage], which lets you store, retrieve and remove
values by key, check for the existence of a key and get information about the current size of the underlying storage.

The [`PluginStorage`][machine.storage.PluginStorage] class interfaces with whatever storage backend Slack Machine is
configured with. You can read more about the available storage backends in the [user guide][choosing-storage].

Example:

```python
@respond_to(r"store (?P<text>.*) under (?P<key>\w+)")
async def store(self, msg, text, key):
    await self.storage.set(key, text)
    await msg.say(f"'{text}' stored under {key}!")

@respond_to(r"retrieve (?P<key>\w+)")
async def retrieve(self, msg, key):
    data = await self.storage.get(key)
    if data:
        await msg.say(f"'{data}' retrieved from <{key}>!")
    else:
        await msg.say("Key not found!")

@respond_to(r"delete (?P<key>\w+)")
async def delete(self, msg, key):
    await self.storage.delete(key)
    await msg.say(f"data in <{key}> deleted!")

@respond_to(r"does (?P<key>\w+) exist?")
async def exists(self, msg, key):
    if await self.storage.has(key):
        await msg.say(f"<{key}> exists.")
    else:
        await msg.say(f"<{key}> does not exist!")

@respond_to(r"size")
async def size(self, msg):
    human_size = await self.storage.get_storage_size_human()
    await msg.say("storage size: {human_size}")
```

## Shared vs non-shared

By default, when you store, retrieve and remove data by key, Slack Machine will automatically namespace the keys you use
with the fully qualified classname of the plugin the storage is used from. This is done to prevent plugins from changing
or even deleting each others data. So when you do this:

```python
# resides in module my.plugin.package
class MyPlugin:
    async def some_function():
        await self.storage.set("my-key", "my-data")
```

Slack Machine will send the key `my.plugin.package.MyPlugin:my-key` to the storage backend.

You can override this behaviour by setting the `shared` parameter to `True` when calling a storage related function
that requires a key as parameter. This keep the key global (ie. non-namespaced). This is useful when you want to share
data between plugins. Use this feature with care though, as you can destroy data that belongs to other plugins!

## Implementing your own storage backend

You can implement your own storage backend by subclassing [`MachineBaseStorage`][machine.storage.backends.base.
MachineBaseStorage]. You only have to implement a couple of methods, and you don't have to take care of namespacing of
keys, as Slack Machine will do that for you.
