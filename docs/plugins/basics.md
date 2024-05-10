# Plugin Basics

Writing plugins for Slack Machine is easy. To show you *how* easy, we'll build and run a simple plugin from start to
finish. To be able to follow this guide, you have to have [installed and configured][installation] Slack Machine first!

## The Base class for plugins

Plugins in Slack Machine are classes that subclass [`MachineBasePlugin`][machine.plugins.base.MachineBasePlugin].
Inheriting from this class tells Slack Machine that we're dealing with a plugin. But that's not even the most exciting
part! With this base class, your plugin immediately has a lot of functionality at its disposal that makes it super easy
to do anything from talking to channels, responding to messages, sending DMs, and much more!

## The decorators

Being able to talk in Slack is only half the story for plugins. The functions in your plugin have to be triggered
somehow. Slack Machine provides [decorators](../api.md#decorators) for that. You can decorate the functions in your
plugin class to tell them what they should react to.

As an example, let's create a cool plugin!

## Step 1: Creating the plugin

We're going to create a plugin that listens for [The Answer](http://hitchhikers.wikia.com/wiki/42), and responds in
kind.

In the root of your bot (where your `local_settings.py` lives), create a *plugins* folder. In it, create an
`__init__.py` (so your *plugins* folder becomes a package) and a file named `hitchhikers.py`.

Your folder structure should look like this:

``` bash
├── local_settings.py
└── plugins
    ├── __init__.py
    └── hitchhikers.py
```

## Step 2: Adding the code

First, we should import the [`MachineBasePlugin`][machine.plugins.base.MachineBasePlugin] in our code, and the
decorator to listen for specific messages. Then we can create our plugin class that includes a function
that listens for The Answer, and responds to it:

```python
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import listen_to
import re

class UltimateQuestionPlugin(MachineBasePlugin):

    @listen_to(regex=r"^42$")
    async def question(self, msg):
        await msg.say("You're telling me the Answer to the Ultimate Question of Life, the Universe and Everything, ",
                      "but I don't know the question :cry:")
```

!!! tip

    As Slack-Machine is fully built on top of Python's excellent
    [AsyncIO library](https://docs.python.org/3/library/asyncio.html), all of the functionality that Slack Machine
    offers (e.g. sending messages, adding reactions etc.) comes in the form of async functions, a.k.a.
    [_coroutines_](https://docs.python.org/3/library/asyncio-task.html#coroutines). This means that the plugin functions
    you define, have to be coroutines as well!

    This will take a while to get used to, but the reward is that Slack Machine is able to run your plugin functions
    concurrently.

## Step 3: Enabling our plugin

Now we can enable our plugin in our configuration file. Your
`local_settings.py` should look like this:

```python
SLACK_APP_TOKEN = "xapp-my-app-token"
SLACK_BOT_TOKEN = "xoxb-my-bot-token"

PLUGINS = ["machine.plugins.builtin.general.HelloPlugin",
           "machine.plugins.builtin.general.PingPongPlugin",
           "plugins.hitchhikers.UltimateQuestionPlugin"]
```

## Step 4: Run that bot!

To run your bot with the new plugin:

``` bash
$ slack-machine
```

That's all there is to it!
