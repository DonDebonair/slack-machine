# Slack Machine

[![Join the chat at https://gitter.im/slack-machine/lobby](https://badges.gitter.im/slack-machine/lobby.svg)](https://gitter.im/slack-machine/lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![image](https://img.shields.io/pypi/v/slack-machine.svg)](https://pypi.python.org/pypi/slack-machine)
[![image](https://img.shields.io/pypi/l/slack-machine.svg)](https://pypi.python.org/pypi/slack-machine)
[![image](https://img.shields.io/pypi/pyversions/slack-machine.svg)](https://pypi.python.org/pypi/slack-machine)
[![CI Status](https://github.com/DonDebonair/slack-machine/actions/workflows/ci.yml/badge.svg)](https://github.com/DonDebonair/slack-machine/actions/workflows/ci.yml)
[![image](https://codecov.io/gh/DonDebonair/slack-machine/branch/main/graph/badge.svg)](https://codecov.io/gh/DonDebonair/slack-machine)

Slack Machine is a wonderful, simple, yet powerful and extendable Slack bot framework.
More than just a bot, Slack Machine is a framework that helps you
develop your Slack team into a ChatOps powerhouse.

![image](extra/logo.png)

## *Note*

As of v0.26.0 Slack Machine supports AsyncIO using the
[Slack Events API](https://api.slack.com/apis/connections/events-api) and
[Socket Mode](https://api.slack.com/apis/connections/socket). This is still experimental and should be thoroughly
tested. The goal is to eventually stop supporting the old version that uses the Slack RTM API, as the Events API is
recommended by Slack for must use cases and asyncio has the potential to be much more performant.

I encourage everyone to start testing the async mode and report any issues in this repository.

## Features

- Get started with mininal configuration
- Built on top of the [Slack RTM API](https://api.slack.com/rtm) for smooth, real-time
  interactions (or Slack Events API + Socket Mode for async mode)
- Support for rich interactions using the [Slack Web API](https://api.slack.com/web)
- High-level API for maximum convenience when building plugins
- Low-level API for maximum flexibility
- **(Experimental) Support for asyncio**

### Plugin API features:

- Listen and respond to any regular expression
- Capture parts of messages to use as variables in your functions
- Respond to messages in channels, groups and direct message conversations
- Respond with reactions
- Respond in threads
- Respond with ephemeral messages
- Send DMs to any user
- Support for [message attachments](https://api.slack.com/docs/message-attachments)
- Support for [blocks](https://api.slack.com/reference/block-kit/blocks)
- Listen and respond to any [Slack event](https://api.slack.com/events) supported by the RTM API (or the Events API
  with Socket Mode in the case of using async mode)
- Store and retrieve any kind of data in persistent storage (currently Redis and in-memory storage are supported)
- Schedule actions and messages (note: currently not supported in async mode)
- Emit and listen for events
- Help texts for Plugins
- Built in web server for webhooks (note: currently not supported in async mode)

### Coming Soon

- Support for Interactive Buttons
- ... and much more

## Installation

You can install Slack Machine using pip:

``` bash
$ pip install slack-machine
```

It is **strongly recommended** that you install `slack-machine` inside a
[virtual environment](https://docs.python.org/3/tutorial/venv.html)!

## Usage

1. Create a directory for your Slack Machine bot:
   `mkdir my-slack-bot && cd my-slack-bot`
2. Add a `local_settings.py` file to your bot directory:
   `touch local_settings.py`
3. Create a Bot User for your Slack team:
   https://my.slack.com/services/new/bot (take note of your API
   token)
4. Add the Slack API token to your `local_settings.py` like this:

``` python
SLACK_API_TOKEN = 'xox-my-slack-token'
```

5. Start the bot with `slack-machine`
6. ...
7. Profit!

## Documentation

You can find the documentation for Slack Machine here: https://dondebonair.github.io/slack-machine/

Go read it to learn how to properly configure Slack Machine, write plugins, and more!
