# Migrating plugins to async

As of v0.30.0 Slack Machine dropped support for the old backend based on the RTM API. As such, Slack Machine is now
fully based on [AsyncIO](https://docs.python.org/3/library/asyncio.html). This means plugins written before the
rewrite to asyncio aren't supported anymore. This is a migration guide to get your old plugins working with the
new version of Slack Machine.

## Await all Slack Machine plugin functions

Any function from [`MachineBasePlugin`][machine.plugins.base.MachineBasePlugin] and
[`Message`][machine.plugins.message.Message] needs to be awaited now. This is as easy as prefixing your the function
calls with the `await` keyword:

```python
await self.say("#general", "Hello there baby!")
```

## All of your plugin functions need to be async

Because you're awaiting methods from the Slack Machine plugin classes now, the functions you define in your own
plugins, need to be _async_. This is as easy as prefixing your function definitions with the `async` keyword:

```python
class MyPlugin(MachineBasePlugin):
    @listen_to(r"^hello")
    async def hello(self, msg):
        msg.say("world")
```
