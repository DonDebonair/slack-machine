.. _usage:

Using Slack Machine
===================

Once you have installed Slack Machine, configuring and starting your bot is easy:

1. Create a directory for your Slack Machine bot: ``mkdir my-slack-bot && cd my-slack-bot``
2. Add a ``local_settings.py`` file to your bot directory: ``touch local_settings.py``
3. Create a Bot User for your Slack team: https://my.slack.com/services/new/bot (take note of your API token)
4. Add the Slack API token to your ``local_settings.py`` like this:

.. code-block:: python
    
    SLACK_API_TOKEN = 'xox-my-slack-token'

5. Start the bot with ``slack-machine``
6. \...
7. Profit!

Configuring Slack Machine
-------------------------

All the configuration for your bot lives in the ``local_settings.py`` in the root of your bot 
directory. The core of Slack Machine, and the built-in plugins, only need a ``SLACK_API_TOKEN`` 
to function.

You can override the log level by setting ``LOGLEVEL``. By default this is set to ``"ERROR"``.

Enabling plugins
""""""""""""""""

Slack Machine comes with a few simple built-in plugins:

- **HelloPlugin**: responds in kind when users greet the bot with "hello" or "hi" (only when the bot is mentioned)
- **PingPongPlugin**: responds to "ping" with "pong" and vice versa (listens regardless of mention)
- **EventLoggerPlugin**: logs all events the bot receives to the console (only when ``LOGLEVEL`` is set to ``"DEBUG"``)
- **EchoPlugin**: replies to any message the bot hears, with exactly the same message. The bot will reply to the same 
  channel the original message was heard in

By default, **HelloPlugin** and **PingPonPlugin** are enabled.

You can specify which plugins Slack Machine should load, by setting the ``PLUGINS`` variable in ``local_settings.py`` 
to a list of fully qualified classes or modules that represent plugins. You can either point to a plugin class directly, 
or to a module containing one or more plugins.

For example, to enable all built-in Slack Machine plugins, your ``local_settings.py`` would look like this:

.. code-block:: python
    
    SLACK_API_TOKEN = 'xox-my-slack-token'
    PLUGINS = [
        'machine.plugins.builtin.general.PingPongPlugin',
        'machine.plugins.builtin.general.HelloPlugin',
        'machine.plugins.builtin.debug.EventLoggerPlugin',
        'machine.plugins.builtin.debug.EchoPlugin'
    ]

Or is you want import them by the modules they're in:

.. code-block:: python
    
    SLACK_API_TOKEN = 'xox-my-slack-token'
    PLUGINS = [
        'machine.plugins.builtin.general',
        'machine.plugins.builtin.debug'
    ]

Slack Machine can load any plugin that is on the Python path. This means you can load any plugin that is installed 
in the same virtual environment you installed Slack Machine in. And as a convenience, Slack Machine will also add the 
directory you start Slack Machine from, to your Python path.

That's all there is to it!
