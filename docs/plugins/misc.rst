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
