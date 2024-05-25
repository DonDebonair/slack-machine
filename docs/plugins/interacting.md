# How to interact

Slack Machine provides several convenient ways to interact with channels and users in your Slack workspace. To this end,
two very similar sets of functions are exposed through two classes:

### MachineBasePlugin

:   The [`MachineBasePlugin`][machine.plugins.base.MachineBasePlugin] class every plugin extends, provides methods
to send messages to channels (public, private and DM), using the WebAPI, with support for rich
messages/blocks/attachment. It also supports adding reactions to messages, pinning and unpinning messages, replying
in-thread, sending ephemeral messages to a channel (only visible to 1 user), updating and deleting messages and much
more.

### Message

:   An instance of the [`Message`][machine.plugins.message.Message] class is automatically supplied to your plugin
functions when using the [`@respond_to`][machine.plugins.decorators.respond_to] or
[`@respond_to`][machine.plugins.decorators.listen_to] decorators. It has a similar set of methods as the
[`MachineBasePlugin`][machine.plugins.base.MachineBasePlugin] class, but without the need to manually specify the
channel you want to talk to. It lets you send messages and reply to messages in the same channel the original message
was received in.

It is recommended to use the passed-in [`Message`][machine.plugins.message.Message] object to interact with channels
and users, whenever you use the [`@respond_to`][machine.plugins.decorators.respond_to] or
[`@respond_to`][machine.plugins.decorators.listen_to] decorators, as this takes away the pain of having to manually
target the right channels.

For a detailed description of all the methods available to you, please read the [api documentation](../api.md). What
follows are some examples of how you would respond in common scenarios.

## Responding to a message

If your plugin receives a message through the [`@respond_to`][machine.plugins.decorators.respond_to]
or [`@listen_to`][machine.plugins.decorators.listen_to] decorators,
the simplest way to reply is using [`msg.reply()`][machine.plugins.message.Message.reply]. It takes 2 parameters:

:   **text**: the message you want to send

:   **in_thread**: if Slack Machine should reply to the original message in-thread

[`msg.reply()`][machine.plugins.message.Message.reply] will start the reply with a mention of the sender of the
original message.

Example:

```python
@respond_to(r"^I love you")
async def spread_love(self, msg):
    await msg.reply("I love you too!")
```

If this function is triggered by a message *@superbot I love you*, sent by **@john**, the response will be: *@john: I
love you too!*

[`msg.reply()`][machine.plugins.message.Message.reply] will use the [Slack WebAPI](https://api.slack.com/web) to send
messages, which means you can send richly formatted messages
using [blocks](https://api.slack.com/reference/block-kit/blocks) and/or
[attachments](https://api.slack.com/docs/message-attachments).

The underlying Python slack-sdk that Slack Machine uses, provides some
[convenience classes](https://github.com/slackapi/python-slack-sdk/tree/master/slack/web/classes)
that can help with creating blocks or attachments. All Slack Machine methods that can be used to send messages, accept
lists of `Block` objects and/or `Attachment` objects from the aforementioned convience classes.

This method has 2 extra parameters that unlock 2 extra features:

:   **ephemeral**: if `True`, the message will be visible only to the
sender of the original message.

:   **in_thread**: this will send the message in a thread instead of to
the main channel

There is 1 more method to respond to a message in the same channel: [`msg.say()`][machine.plugins.message.Message.say]
is very similar to its `reply` counterpart, with the exception that it won't mention the sender of the original message.

If you want to reply to the sender of the original message in a DM instead of in the original channel, you can use the
[`msg.reply_dm()`][machine.plugins.message.Message.reply_dm] methods. This will open a DM convo between the sender of
the original message and the bot (if it doesn't exist already) and send a message there. If the original message was
already received in a DM channel, this is no different from using `reply()`.

## Message properties

The [`Message`][machine.plugins.message.Message] object your plugin function receives, has some convenient properties
about the message that triggered the function:

:   **sender**: a [`User`][machine.models.user.User] object with information about the sender, such as their `id`
and `name`

:   **channel**: a Channel object with information about the channel the message was received in

:   **text**: the contents of the original message

## Plugin properties

The [`MachineBasePlugin`][machine.plugins.base.MachineBasePlugin] class every plugin extends, exposes some properties
about your Slack workspace. These properties are not filled when your plugin is instantiated, but reflect the current
status of the Slack client:

:   **users**: a dict of user ids and the associated [`User`][machine.models.user.User] objects for all users that Slack
Machine knows about. This is usually all the active users in your Slack workspace. This data structure is filled
when Slack Machine starts and is automatically updated whenever a new user joins or the properties of a user change.

:   **channels**: a dict of channel ids and the associated [`User`][machine.models.channel.Channel] objects for
channels that Slack Machine knows about. This contains all the public channels in your Slack workspace, plus all private
channels that your Slack Machine instance was invited to.

## Sending messages without a msg object

There are situations in which you want to send messages to users/channels, but there is no original message to respond
to. For example when implementing your own event listener using the [`@process`][machine.plugins.decorators.process]
decorator. In this case you can call functions similar as those described before, but from your plugin itself:
[`self.say()`][machine.plugins.base.MachineBasePlugin.say] and
[`self.send_dm()`][machine.plugins.base.MachineBasePlugin.send_dm].

These behave similar to their [`Message`][machine.plugins.message.Message] counterparts, except that they require a
channel id or object, or user id or object (in case of DM) to be passed in. You can use
[`find_channel_by_name()`][machine.plugins.base.MachineBasePlugin.find_channel_by_name] to find the channel you want
to send a message to.

## Scheduling messages

Sometimes you want to reply to a message, send a message to some channel, send a DM etc. but you don't want to do it
*now*. You want to do it in **the future**. Slack Machine provides **scheduled** versions of many methods, both in the
[`MachineBasePlugin`][machine.plugins.base.MachineBasePlugin] all plugins extend from and in the
[`Message`][machine.plugins.message.Message] object [`@respond_to`][machine.plugins.decorators.respond_to] and
[`@respond_to`][machine.plugins.decorators.listen_to] functions receive. These methods can be recognized by their
**_scheduled** prefix. They work almost the same as their regular counterparts, except that they receive 1 extra
argument: a [`datetime`][datetime.datetime] object that tells Slack Machine *when* to send the message.

Example:

```python
@respond_to(r"greet me in the future")
async def future(self, msg):
    await msg.say("command received!")
    in_10_sec = datetime.now() + timedelta(seconds=10)
    await msg.reply_dm_scheduled(in_10_sec, "A Delayed Hello!")
```

This function will send a greeting 10 seconds after it has received a
message: *@superbot greet me in the future*.

!!! important "Caveat"

    You cannot schedule a reaction to a message. It doesn't make sense to react to a message in the future.

For more information about scheduling message, have a look at the [api documentation](../api.md).

## Protecting commands

Sometimes you may want to restrict certain commands in your bot, so they can only be invoked by certain users.

To use these restrictions you must appoint one user to be the *root user*. For security reasons there can be only one
*root user*, and it must be configured through `local_settings.py` or environment variables. That way you will never
lose control over your bot.

To enable all the role based features, your `local_settings.py` would look something like this:

```python
SLACK_APP_TOKEN = "xapp-my-app-token"
SLACK_BOT_TOKEN = "xoxb-my-bot-token"
ROOT_USER = "0000007"
PLUGINS = [
    'machine.plugins.builtin.admin.RBACPlugin',
]
```

You can get the *member ID* from a user by going to their Slack profile, clicking *more* and selecting *Copy member ID*.

If you wish to share the powers of root you can enable the RBAC admin
plugin `machine.plugins.builtin.admin.RBACPlugin` and grant the *admin* role to users you trust.

The RBAC plugin provides you with three new commands that lets you lookup, grant and revoke roles to users:

- *@superbot who has role admin*
- *@superbot grant role admin to @trusted-user*
- *@superbot revoke role admin from @trusted-user*.

Now you can decorate certain functions in your plugin with the
[`@require_any_role`][machine.plugins.decorators.require_any_role] or
[`@require_all_roles`][machine.plugins.decorators.require_all_roles] decorators to make them only usable by users with
certain roles.

Here is an example of a command that requires either the *admin* or *channel* role:

```python
@respond_to(
    r"^say in"
    r"\s+<#\w+\|(?P<channel_name>[^>]+)>"
    r"\s+(?P<message>.+)"
)
@require_any_role(["admin", "channel"])
async def say_in_channel(self, msg, channel_name, message):
    logging.info(channel_name)
    await self.say(channel_name, message)
```

You can define as many roles as you want, any string without spaces is acceptable.

## Emitting events

Your plugin can emit arbitrary events that other plugins (or your own) can listen for. Events are a convenient
mechanism for exchanging data between plugins and/or for a plugin to expose an api that other plugins
can hook into. Emitting an event is done with [`self.emit()`][machine.plugins.base.MachineBasePlugin.emit].
You have to provide a name for the event you want to emit, so others can listen for an event by that name. You can
optionally provide extra data as keyword arguments.

Example:

```python
@respond_to(r"I have used the bathroom")
async def broadcast_bathroom_usage(self, msg):
    self.emit('bathroom_used', toilet_flushed=True)
```

You can read [the events section][slack-machine-events] to see how your plugin can listen for events.


## Using the Slack Web API in other ways

Sometimes you want to use [Slack Web API](https://api.slack.com/web) in ways that are not directly exposed by
[`MachineBaserPlugin`][machine.plugins.base.MachineBasePlugin]. In these cases you can use
[`self.web_client`][machine.plugins.base.MachineBasePlugin.web_client]. `self.web_client` references the
[`AsyncWebClient`](https://slack.dev/python-slack-sdk/api-docs/slack_sdk/web/async_client.html#slack_sdk.web.async_client.AsyncWebClient)
object of the underlying Slack Python SDK. You should be able to call any
[Web API method](https://api.slack.com/methods) with that client.
