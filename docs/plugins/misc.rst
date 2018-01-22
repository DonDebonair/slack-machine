.. _misc:

Miscellaneous stuff
===================

This section contains some odds and ends that were not discussed in previous sections.

Plugin initialization
---------------------

Plugins are initialized when Slack Machine starts. Because the :py:class:`~machine.plugins.base.MachineBasePlugin`
already has a constructor that is used to pass various things to the plugin instance at startup,
it is advised not to provide a constructor for your plugin.

If your plugin needs to initialize its own things at startup, you can override the
:py:meth:`~machine.plugins.base.MachineBasePlugin.init` method. This method will be called once
when the plugin is initialized. It is no-op by default.

Plugin help information
-----------------------

You can provide help text for your plugin and its commands by adding `docstrings`_ to your plugin
class and its methods. The first line of the docstring of a plugin class will be used for grouping
help information of plugin methods. This even extends beyond one class, ie. if multiple plugin
classes have the same docstring (first line), the help information for the methods under those
classes will be grouped together.

The first line of the docstring of each plugin method can be used for specifying help information
for that specific function. It should be in the format ``command: help text``.

The ``machine.plugins.builtin.help.HelpPlugin`` (enabled by default) will provide Slack users with
the help information described above.

.. _docstrings: https://www.python.org/dev/peps/pep-0257/