# Slack Machine

[![Join the chat at Slack](https://img.shields.io/badge/chat-slack-green?logo=slack&logoColor=white)](https://join.slack.com/t/slack-machine-chat/shared_invite/zt-1g87tzvlf-8bV_WnY3JZyaYNnRFwRd~w)
[![image](https://img.shields.io/pypi/v/slack-machine.svg)](https://pypi.python.org/pypi/slack-machine)
[![image](https://img.shields.io/pypi/l/slack-machine.svg)](https://pypi.python.org/pypi/slack-machine)
[![image](https://img.shields.io/pypi/pyversions/slack-machine.svg)](https://pypi.python.org/pypi/slack-machine)
[![CI Status](https://github.com/DonDebonair/slack-machine/actions/workflows/ci.yml/badge.svg)](https://github.com/DonDebonair/slack-machine/actions/workflows/ci.yml)
[![image](https://codecov.io/gh/DonDebonair/slack-machine/branch/main/graph/badge.svg)](https://codecov.io/gh/DonDebonair/slack-machine)

Slack Machine is a simple, yet powerful and extendable Slack bot framework. More than just a bot, Slack
Machine is a framework that helps you develop your Slack workspace into a ChatOps powerhouse. Slack Machine is built
with an intuitive plugin system that lets you build bots quickly, but also allows for easy code organization. A
plugin can look as simple as this:

```python
from machine.plugins.base import MachineBasePlugin
from machine.plugins.message import Message
from machine.plugins.decorators import respond_to


class DeploymentPlugin(MachineBasePlugin):
    """Deployments"""

    @respond_to(r"deploy (?P<application>\w+) to (?P<environment>\w+)")
    async def deploy(self, msg: Message, application, environment):
        """deploy <application> <environment>: deploy application to target environment"""
        await msg.say(f"Deploying {application} to {environment}")
```

## _Breaking Changes_

**Plugin initialization is now async** (v0.35.0)

The optional initialization method
[plugins can implement](https://dondebonair.github.io/slack-machine/plugins/misc/#plugin-initialization), which is
run once when the plugin is loaded, should be an **async** method starting the upcoming
[v0.35.0](https://github.com/DonDebonair/slack-machine/releases/tag/v0.35.0). The reason for this is that this
allows plugins to interact with Slack through the Slack Machine's plugin API - most of which methods are async.

Simply prefix your `init()` methods with `async`.

**Dropped support for Python 3.7** (v0.34.0)

As of [v0.34.0](https://github.com/DonDebonair/slack-machine/releases/tag/v0.34.0), support for Python 3.7 has been
dropped. Python 3.7 has reached end-of-life on 2023-06-27.

**AsyncIO** (v0.30.0)

As of [v0.30.0](https://github.com/DonDebonair/slack-machine/releases/tag/v0.30.0) Slack Machine dropped support for
the old backend based on the RTM API. As such, Slack Machine is now fully based on
[AsyncIO](https://docs.python.org/3/library/asyncio.html). This means plugins written before the rewrite to asyncio
aren't supported anymore. See [here](https://dondebonair.github.io/slack-machine/migrating/) for a migration guide to
get your old plugins working with the new version of Slack Machine.

It's really easy!

## Features

- Get started with mininal configuration
- Built on top of the [Slack Events API](https://api.slack.com/apis/connections/events-api) for smoothly responding
  to events in semi real-time. Uses [Socket Mode](https://api.slack.com/apis/connections/socket) so your bot doesn't
  need to be exposed to the internet!
- Support for rich interactions using the [Slack Web API](https://api.slack.com/web)
- High-level API for maximum convenience when building plugins
- Low-level API for maximum flexibility
- Built on top of [AsyncIO](https://docs.python.org/3/library/asyncio.html) to ensure good performance by handling
  communication with Slack concurrently

### Plugin API features:

- Listen and respond to any regular expression
- Respond to Slash Commands
- Capture parts of messages to use as variables in your functions
- Respond to messages in channels, groups and direct message conversations
- Respond with reactions
- Respond in threads
- Respond with ephemeral messages
- Send DMs to any user
- Support for [blocks](https://api.slack.com/reference/block-kit/blocks)
- Support for [message attachments](https://api.slack.com/docs/message-attachments) [Legacy 🏚]
- Support for [interactive elements](https://api.slack.com/block-kit)
- Listen and respond to any [Slack event](https://api.slack.com/events) supported by the Events API
- Store and retrieve any kind of data in persistent storage (currently Redis, DynamoDB, SQLite, and in-memory storage
  are supported)
- Schedule actions and messages
- Emit and listen for events
- Help texts for Plugins

### Coming Soon

- Support for modals
- Support for shortcuts
- ... and much more
