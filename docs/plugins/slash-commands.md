# Slash Commands

Next to triggering Slack Machine by [listening to](listening.md) messages that match a specific regular expression,
you can also use [Slash Commands](https://api.slack.com/interactivity/slash-commands) in Slack Machine.

## Creating a Slash Command

To configure a Slash Command for your Slack App, you can follow the
[instructions](https://api.slack.com/interactivity/slash-commands#creating_commands) in the official Slack
documentation. As you will have likely followed the [guide to using Slack Machine](../user/usage.md), you propbably
have already defined a Slack App. This is what you need to do next:

1. Go to your [app's management dashboard](https://api.slack.com/apps)
2. Click your Slack App
3. Go to _Slash Commands_ in the navigation menu
4. Click the _Create New Command_ button and follow the instructions

### Using the App manifest

If you used the example _App manifest_ when creating your Slack App, you can also adjust that to include the Slash
Commands you want to define. You can add it under `features` as follows:

```yaml
features:
  bot_user:
    display_name: My Bot
    always_online: false
  slash_commands:
    - command: /hello
      description: Say hello
      usage_hint: "[whatever else you want to say]"
      should_escape: false
```

## Defining your Slash Command in code

The next step is to use the [`@command`][machine.plugins.decorators.command] decorator on the function that should be
triggered when the user uses the Slash Command you defined. The decorator takes only 1 parameter: the slash command
that should trigger the decorated function. It should be the same as the Slash Command you just defined in the App
dashboard.

This is what a decorated command handler typically looks like:

```python
@command("/hello")
async def hello(self, command):
    print(f"I just received the following command: {command.command} with text {command.text}")
    await command.say("I like greetings!")
```

### Parameters of your command handler

Your command handler will be called with a [`Command`][machine.plugins.command.Command] object that contains useful
information about the slash command invocation. The most important property is probably
[`text`][machine.plugins.command.Command.text], which contains any additional text that was passed when the slash
command was used.

You can optionally add the `logger` argument to your handler get a
[logger that was enriched by Slack Machine](misc.md#using-loggers-provided-by-slack-machine-in-your-handler-functions)

### Responding to a command

Responding to Slash Commands is a timely business. As explained
[in the official documentation](https://api.slack.com/interactivity/slash-commands#responding_to_commands), the
receipt of the slash command payload has to be acknowledged. This has to happen within 3 seconds, or Slack will
return an error to the user. To make your life easy, Slack Machine will handle all of this.

If you want to send a message to the user after a slash command was invoked, you can do so by calling the
[`say()`][machine.plugins.command.Command.say] method on the _command_ object your handler received from Slack Machine.
This works just like any other way Slack provides for sending messages. You can include just text, but also rich
content using [_Block Kit_](https://api.slack.com/block-kit)

!!! info

    The [`response_url`][machine.plugins.command.Command.response_url] property is used by the
    [`say()`][machine.plugins.command.Command.say] method to send messages to a channel after receiving a command.
    It does so by invoking a _Webhook_ using this `response_url` This is different from how
    [`message.say()`][machine.plugins.message.Message.say] works - which uses the Slack Web API.

    The reason for this is to keep consistency with how Slack recommends interacting with a user. For commands,
    using the `response_url` is the [recommended way](https://api.slack.com/interactivity/handling#message_responses)

If you read the aforementioned documentation on responding to commands carefully, you'll notice that as part of
acknowleding the receipt of a command payload, you can return a response to the user (which has to happen in 3
seconds). This is different from the `command.say()` method, which does not have any timing requirements. Slack
Machine supports returning an immediate response by turning your command handler into a _generator_ and returning an
immediate response through [`yield`](https://docs.python.org/3/reference/simple_stmts.html#yield):

```python
@command("/hello-again")
async def hello_again(self, command):
    print(f"I just received the following command: {command.command} with text {command.text}")
    # this is sent as part of the initial payload acknowledgement
    yield "This will be returned immediately to the user"
    # this is less time-sensitive
    await command.say("This will be sent after the initial acknowledgement")
```

## Opening modals

The [`Command`][machine.plugins.command.Command] object that your handler receives, contains an extra piece of
information you can use to trigger more varied reponses: the [`trigger_id`][machine.plugins.command.Command.trigger_id]
The `trigger_id` can used specifically to trigger [_modal responses_][modals]. You don't have to worry about the
`trigger_id` and instead can just call the [`open_modal`][machine.plugins.command.Command.open_modal] method on the
`Command` object to open a modal.
