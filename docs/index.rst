.. Slack Machine documentation master file, created by
   sphinx-quickstart on Fri Sep  1 17:18:52 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Slack Machine
=============

.. image:: https://img.shields.io/pypi/v/slack-machine.svg
    :target: https://pypi.python.org/pypi/slack-machine

.. image:: https://img.shields.io/pypi/l/slack-machine.svg
    :target: https://pypi.python.org/pypi/slack-machine

.. image:: https://img.shields.io/pypi/pyversions/slack-machine.svg
    :target: https://pypi.python.org/pypi/slack-machine

.. image:: https://travis-ci.org/DandyDev/slack-machine.svg?branch=master
    :target: https://travis-ci.org/DandyDev/slack-machine

.. image:: https://codecov.io/gh/DandyDev/slack-machine/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/DandyDev/slack-machine

Slack Machine is a sexy, simple, yet powerful and extendable Slack bot. More than just a bot, 
Slack Machine is a framework that helps you develop your Slack workspace into a ChatOps powerhouse.

Features
--------

- Get started with mininal configuration
- Built on top of the `Slack RTM API`_ for smooth, real-time interactions
- Support for rich interactions using the `Slack Web API`_
- High-level API for maximum convenience when building plugins
- Low-level API for maximum flexibility
- Plugin API features:
    - Listen and respond to any regular expression
    - Capture parts of messages to use as variables in your functions
    - Respond to messages in channels, groups and direct message conversations
    - Respond with Emoji
    - Respond in threads
    - Send DMs to any user
    - Support for `message attachments`_
    - Listen and respond to any `Slack event`_ supported by the RTM API
    - Store and retrieve any kind of data in persistent storage (currently Redis and in-memory storage are supported)
    - Schedule actions and messages
    - Emit and listen for events

.. _Slack RTM API: https://api.slack.com/rtm
.. _Slack Web API: https://api.slack.com/web
.. _message attachments: https://api.slack.com/docs/message-attachments
.. _Slack event: https://api.slack.com/events

Coming Soon
"""""""""""

- Help texts for Plugins
- Support for Interactive Buttons
- ... and much more

User Guide
----------

.. toctree::
   :maxdepth: 2

   user/intro
   user/install
   user/usage

Writing Plugins
---------------

.. toctree::
   :maxdepth: 2

   plugins/basics
   plugins/listening
   plugins/interacting
   plugins/settings
   plugins/storage

API Docs
--------

.. toctree::
   :maxdepth: 2

   api
