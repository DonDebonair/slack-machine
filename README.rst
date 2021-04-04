Slack Machine
=============

.. image:: https://badges.gitter.im/slack-machine/lobby.svg
   :alt: Join the chat at https://gitter.im/slack-machine/lobby
   :target: https://gitter.im/slack-machine/lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

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
Slack Machine is a framework that helps you develop your Slack team into a ChatOps powerhouse.

.. image:: extra/logo.png

*Warning*
---------

As of v0.19 there are some breaking changes! If you're using v0.18.2 or older, you might have to
make some changes to your slack bot built with Slack Machine and/or Slack Machine plugins. The
following changes are non-backwards compatible:

- The ``catch_all`` method has been removed from the base plugin class. You can still respond to specific event types
  using the ``@process`` decorator
- The ``*_webapi`` methods to send messages do not exist anymore, use the regular counterparts instead. All messages
  are now sent using the Slack WebAPI. The RTM API is still used for listening to messages and events.
- ``self.users`` and ``self.channels`` now return different objects than before. See API documentation for more details.
  These properties should behave more consistently however, even in workspaces with many users.

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
    - Respond with ephemeral messages
    - Send DMs to any user
    - Support for `message attachments`_
    - Support for `blocks`_
    - Listen and respond to any `Slack event`_ supported by the RTM API
    - Store and retrieve any kind of data in persistent storage (currently Redis and in-memory storage are supported)
    - Schedule actions and messages
    - Emit and listen for events
    - Help texts for Plugins
    - Built in web server for webhooks

.. _Slack RTM API: https://api.slack.com/rtm
.. _Slack Web API: https://api.slack.com/web
.. _message attachments: https://api.slack.com/docs/message-attachments
.. _blocks: https://api.slack.com/reference/block-kit/blocks
.. _Slack event: https://api.slack.com/events

Coming Soon
"""""""""""

- Support for Interactive Buttons
- ... and much more

Installation
------------

You can install Slack Machine using pip:

.. code-block:: bash

    $ pip install slack-machine

It is **strongly recommended** that you install ``slack-machine`` inside a `virtual environment`_!

.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/

Usage
-----

1. Create a directory for your Slack Machine bot: ``mkdir my-slack-bot && cd my-slack-bot``
2. Add a ``local_settings.py`` file to your bot directory: ``touch local_settings.py``
3. Create a Bot User for your Slack team: https://my.slack.com/services/new/bot (take note of your API token)
4. Add the Slack API token to your ``local_settings.py`` like this:

.. code-block:: python

    SLACK_API_TOKEN = 'xox-my-slack-token'

5. Start the bot with ``slack-machine``
6. \...
7. Profit!

Documentation
-------------

You can find the documentation for Slack Machine here: http://slack-machine.readthedocs.io/en/latest/

Go read it to learn how to properly configure Slack Machine, write plugins, and more!
