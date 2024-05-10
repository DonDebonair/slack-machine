# Listening for things

Slack Machine allows you to listen for various different things and respond to that. By decorating functions in your
plugin using the [decorators](../api.md#decorators) Slack Machine provides, you can tell Slack Machine to run those
functions when something specific happens.

## Listen for a mention

The [`respond_to`][machine.plugins.decorators.respond_to] decorator tells Slack Machine to listen for messages
mentioning your bot and matching a specific pattern. Slack Machine will hear messages sent in any channel or private
group it is a member of. For a message to trigger a function decorated by `@respond_to(...)`, the message has to *start*
with a mention of your bot or with any alias the user configured using the `ALIASES` setting. The exception is direct
messages sent to the bot, they don't have to include a mention to trigger `@respond_to`.

`@respond_to` takes 3 parameters:

:   **regex** (_required_): the regular expression Slack Machine should listen for. The regex pattern should **not**
account for the mention of your bot, as Slack Machine will remove the mention before looking for a match. Slack Machine
listens for any occurrence of the pattern in the message, so if you want to specifically match the whole message, you
can anchor your pattern using the `^` and `$` symbols.

:   **flags** (optional): can be used to pass flags for the regex matching as defined in the [`re`][re] module. By
default, [`re.IGNORECASE`][re.IGNORECASE] is applied.

:   **handle_message_changed** (optional): is used to configure if Slack Machine should trigger this function for
messages that have been _changed_. By default, only _new_ messages will trigger the decorated function.

### How your function will be called

Your function will be called with a [`Message`][machine.plugins.message.Message] object that represents the message
that triggered the function. It not only contains the message text itself, but also has many convenient
methods for replying.

Example:

```python
@respond_to(r"^I love you")
async def spread_love(self, msg):
    await msg.reply("I love you too!")
```

The regex pattern can optionally contain [named groups](http://www.regular-expressions.info/named.html)
that will be captured and passed to your function as keyword arguments.

Example:

```python
@respond_to(r"You deserve (?P<num_stars>\d+) stars!")
async def award(self, msg, num_stars):
    stars_back = int(num_stars) + 1
    await msg.reply("Well, you deserve {}!".format(stars_back))
```

## Hear any message

The [`@listen_to`][machine.plugins.decorators.listen_to] decorator works similar as the
[`@respond_to`][machine.plugins.decorators.respond_to] decorator, but it will hear *any* message matching a pattern,
without the bot being explicitly mentioned. `@listen_to` takes the same parameters as `@respond_to`.

Example:

```python
@listen_to(r"go for it")
@listen_to(r"go 4 it")
async def go_for_it(self, msg):
    await msg.say("https://a-z-animals.com/media/animals/images/original/gopher_2.jpg")
```

As you can see, you can also apply the same decorator multiple times to a function, each time with different arguments.
Of course, you can also combine different decorators on one function.

## More flexibility with Slack events

If you want your bot to respond to other things than messages, you can do so using the
[`@process`][machine.plugins.decorators.process] decorator. `@process` requires an `event_type` as parameter and will
trigger the decorated function any time an event of the specified type happens. It can listen to
any [Slack event](https://api.slack.com/events) that is supported by the Events API.

The received event will be passed to your function.

The following example will listen for the [reaction_added](https://api.slack.com/events/reaction_added) event to
know if a *reaction* was added to a message, and will match that reaction:

```python
@process("reaction_added")
async def match_reaction(self, event):
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    ts = event["item"]["ts"]
    await self.react(channel, ts, emoji)
```

As you can see, `@process` gives you a lot of flexibility by allowing you to process any event Slack Machine does not
provide a specific decorator for.

## Take action on a Schedule

Slack Machine can also run functions on a schedule, using the [`@schedule`][machine.plugins.decorators.schedule]
decorator. `@schedule` behaves like Linux/Unix [Crontab](http://www.adminschoice.com/crontab-quick-reference), and
receives similar parameters. You can specify on what schedule your function should be called. When your function is
called, it will not receive any arguments except `self`, but you can of course call any
[`MachineBasePlugin`][machine.plugins.base.MachineBasePlugin] methods to send message and do other things.

Example:

```python
@schedule(hour="9-17", minute="*/30")
async def movement_reminder(self):
    await self.say("general", "<!here> maybe now is a good time to take a short walk!")
```

## Slack Machine events

Slack Machine can respond to events that are emitted by your plugin(s) or plugins of others, or events generated by
parts of Slack Machine itself. You can use the [`@on`][machine.plugins.decorators.on] decorator on a function to run
that function whenever a certain event is emitted somewhere.

Example:

```python
@on("bathroom_used")
async def call_cleaning_department(self, **kwargs):
    await self.say("cleaning-department", "<!here> Somebody used the toilet!")
```

This function will be called whenever the `bathroom_used` event is emitted somewhere.

!!! important "Some things to be aware of"

    Event names are global, every plugin can emit and listen for the same events. This is by design, because this
    way, you can use events to exchange data between plugins. Events can be a way to expose a "public API" for
    plugins. But this can also mean your functions are unexpectedly triggered by events sent by other plugins,
    especially if the event names you choose are very generic.

    When emitting events, plugins can attach whatever variables they want to the event, and when listening for an
    event, your function will be called with whatever arguments were attached to the event when the event was
    emitted. It's therefor a good idea to always include `**kwargs` as a catch-all, otherwise your function could
    return an error when it's called with arguments that have not been explicitly defined.

So what is this event system useful for? As mentioned in the above note, events can be used to communicate between
plugins and/or for plugins to respond to events that happen within the core of Slack Machine. A good example of this,
is the `unauthorized-access` event. This event will be emitted whenever someone tries to use a bot command protected
by the [`require_any_role`][machine.plugins.decorators.require_any_role] or
[`require_all_roles`][machine.plugins.decorators.require_all_roles] decorators without having the right roles to
issue that command. By listening to this event, your plugins can take action when this happens. The built-in RBAC
plugin also listens for this event.

You can read [emitting events][emitting-events] to learn how to emit events from your own plugins.
