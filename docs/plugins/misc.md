# Miscellaneous stuff

This section contains some odds and ends that were not discussed in previous sections.

## Plugin initialization

Plugins are initialized when Slack Machine starts. Because the
[`MachineBasePlugin`][machine.plugins.base.MachineBasePlugin] already has a constructor that is used to pass various
things to the plugin instance at startup, it is advised not to provide a constructor for your plugin.

If your plugin needs to initialize its own things at startup, you can override the
[`init()`][machine.plugins.base.MachineBasePlugin.init] method. This method will be called once when the plugin is
initialized. It is no-op by default. If you choose to implement this method, make sure it is `async`. This allows
you to use the async plugin API of Slack Machine to interact with Slack and also lets you use the plugin storage.

When the `init()` methods of plugins are called, the underlying Slack client has already been initialized, so you
should have full access to all Slack-related information, incl. a populated list of
[`users`][machine.plugins.base.MachineBasePlugin.users] and
[`channels`][machine.plugins.base.MachineBasePlugin.channels]

## Logging

Slack Machine uses [structlog](https://www.structlog.org) for logging. In your plugins, you can instantiate and use a
logger as follows:

```python
from structlog.stdlib import get_logger

logger = get_logger(__name__)


async def my_function():
    logger.info("Running my function", foo=42, bar="hello")
```

### Logging message handler invocations

By default, Slack Machine will log anytime a Slack message triggers a handler in a plugin. This log statement will
include the message that triggered the handler and the user id & name of the user that posted the message.

You can disable these log message by setting `LOG_HANDLED_MESSAGES` to `False` in your `local_settings.py`

### Using loggers provided by Slack Machine in your handler functions

Structlog allows adding extra parameters as context. Slack Machine leverages this to bind the _id_ and _name_ of the
user who sent a message to a logger as context variables whenever a message triggers a handler function. You can opt-in
to using this logger, by adding a `logger` parameter to your handler function.

```python
async def my_handler(msg, logger):
    logger.info("my_handler invoked!")
```

Slack Machine will automatically inject a logger with the right context variables into your handler. The example
will produce a message like:

```bash
2022-10-21T14:29:05.639162Z [info] my_handler invoked! [example_plugin.my_plugin.MyPlugin.my_handler] filename=my_plugin.py func_name=my_handler lineno=5 user_id=U12345678 user_name=user1
```

This currently works for handler functions that are decorated with
[`respond_to`][machine.plugins.decorators.respond_to], [`listen_to`][machine.plugins.decorators.listen_to] or
[`command`][machine.plugins.decorators.command]

## Plugin help information

You can provide help text for your plugin and its commands by adding
[docstrings](https://www.python.org/dev/peps/pep-0257/) to your plugin class and its methods. The first line of the
docstring of a plugin class will be used for grouping help information of plugin methods. This even extends beyond one
class, ie. if multiple plugin classes have the same docstring (first line), the help information for the methods under
those classes will be grouped together.

The first line of the docstring of each plugin method can be used for specifying help information for that specific
function. It should be in the format `command: help text`.

The `machine.plugins.builtin.help.HelpPlugin` (enabled by default) will provide Slack users with the help information
described above.
