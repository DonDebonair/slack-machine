# Slack Machine

![image](img/logo.png)

[![Join the chat at https://gitter.im/slack-machine/lobby](https://badges.gitter.im/slack-machine/lobby.svg)](https://gitter.im/slack-machine/lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![image](https://img.shields.io/pypi/v/slack-machine.svg)](https://pypi.python.org/pypi/slack-machine)
[![image](https://img.shields.io/pypi/l/slack-machine.svg)](https://pypi.python.org/pypi/slack-machine)
[![image](https://img.shields.io/pypi/pyversions/slack-machine.svg)](https://pypi.python.org/pypi/slack-machine)
[![CI Status](https://github.com/DonDebonair/slack-machine/actions/workflows/ci.yml/badge.svg)](https://github.com/DonDebonair/slack-machine/actions/workflows/ci.yml)
[![image](https://codecov.io/gh/DonDebonair/slack-machine/branch/main/graph/badge.svg)](https://codecov.io/gh/DonDebonair/slack-machine)

Slack Machine is a wonderful, simple, yet powerful and extendable Slack bot framework. More than just a bot, Slack
Machine is a framework that helps you develop your Slack workspace into a ChatOps powerhouse.

## *Note*

As of v0.30.0 Slack Machine dropped support for the old backend based on the RTM API. As such, Slack Machine is now
fully based on [AsyncIO](https://docs.python.org/3/library/asyncio.html). This means plugins written before the
rewrite to asyncio aren't supported anymore. See [here](migrating.md) for a migration guide to get your old plugins
working with the new version of Slack Machine.

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
- Capture parts of messages to use as variables in your functions
- Respond to messages in channels, groups and direct message conversations
- Respond with reactions
- Respond in threads
- Respond with ephemeral messages
- Send DMs to any user
- Support for [blocks](https://api.slack.com/reference/block-kit/blocks)
- Support for [message attachments](https://api.slack.com/docs/message-attachments) [Legacy 🏚]
- Listen and respond to any [Slack event](https://api.slack.com/events) supported by the Events API
- Store and retrieve any kind of data in persistent storage (currently Redis, DynamoDB and in-memory storage are
  supported)
- Schedule actions and messages
- Emit and listen for events
- Help texts for Plugins

### Coming Soon

- Support for Interactive Buttons
- ... and much more
