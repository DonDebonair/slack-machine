.. _plugin settings:

Plugin Settings
===============

All settings that are defined, either from the Slack Machine defaults or in ``local_settings.py`` 
are available to plugins through the ``self.settings`` field. This is a dictionary with all 
settings indexed by their name. Next to ``local_settings.py``, users can also specify settings 
with environment variables. Slack Machine will automatically translate any environment variable 
with the format ``SM_<SETTINGNAME>`` to a setting with name ``SETTINGNAME``, overriding a setting 
with the same name from ``local_settings.py`` or the default settings.

So an environment variable ``SM_SLACK_API_TOKEN`` will result in a setting ``SLACK_API_TOKEN``.

Setting names are **case insensitive**.

Example of using settings
-------------------------

When the ``local_settings.py`` looks like this:

.. code-block:: python

    SLACK_API_TOKEN = 'xoxo-abc123'
    GREETING_PLUGIN_MY_GREETING = 'Bonjour'

This can be used in a plugin, like this:

.. code-block:: python

    @respond_to(r"Hello!")
    def greeting(self, msg):
        msg.reply("{}, {}!".format(
            self.settings['GREETING_PLUGIN_MY_GREETING'],
            msg.at_sender
        ))

The respond to a message *@superbot Hello!"* from **@john**, in this case would be: *Bonjour, @john!*
