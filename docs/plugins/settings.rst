.. _plugin settings:

Plugin Settings
===============

All settings that are defined, either from the Slack Machine defaults or in ``local_settings.py``
are available to plugins through the ``self.settings`` field. This is a dictionary with all
settings indexed by their name. Next to ``local_settings.py``, users can also specify settings
with environment variables. Slack Machine will automatically translate any environment variable
with the format ``SM_<SETTING-NAME>`` to a setting with name ``SETTING-NAME``, overriding a setting
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

Required settings
-----------------

If your plugin requires one or more settings to be defined in order to work, you can mark them as
*required* with the :py:meth:`~machine.plugins.decorators.required_settings` decorator. This
decorator takes a string or a list of strings as argument which can be one or more settings that
are required by your plugin. Upon startup, Slack Machine will check if any of the settings that
are marked as *required* by a plugin, have not been defined by the user. If it finds one or more
missing settings, it will not load that particular plugin, and notify the user which settings are
missing.

The :py:meth:`~machine.plugins.decorators.required_settings` decorator can be applied to a plugin
class and/or its methods. Note that if **any** of the required settings are missing, the plugin
will not load as a whole, so none of the methods will be registered.

Example:

.. code-block:: python

    @required_settings(['TODO_SERVICE_USERNAME', 'TODO_SERVICE_PASSWORD'])
    class TodoPlugin(MachineBasePlugin):
        ...
