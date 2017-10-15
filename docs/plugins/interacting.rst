.. _responding:

How to interact
===============

Slack Machine provides several convenient ways to interact with channels and users in your Slack 
workspace. To this end, two very similar sets of functions are exposed through two classes:

	The :py:class:`~machine.plugins.base.MachineBasePlugin` class every plugin extends, provides 
	methods to send messages to channels (public, private and DM), through the RTM API or using 
	the WebAPI (for rich messages/attachment support). It also supports adding reactions to messages, 
	replying in-thread, sending ephemeral messages to a channel (only visible to 1 user), and much 
	more.

	An instance of the :py:class:`~machine.plugins.base.Message` class is automatically supplied 
	to your plugin functions when using the :py:meth:`~machine.plugins.decorators.respond_to` or 
	:py:meth:`~machine.plugins.decorators.listen_to` decorators. It has a similar set of methods 
	as the :py:class:`~machine.plugins.base.MachineBasePlugin` class, but without the need to 
	manually specify the channel you want to talk to. It lets you send messages and reply to 
	messages in the same channel the original message was received in.

It is recommended to use the passed-in :py:class:`~machine.plugins.base.Message` object to 
interact with channels and users, whenever you use the :py:meth:`~machine.plugins.decorators.respond_to` 
or :py:meth:`~machine.plugins.decorators.listen_to` decorators, as this takes away the pain of 
having to manually target the right channels.

For a detailed description of all the methods available to you, please read the :ref:`api documentation`. 
What follows are some examples of how you would respond in common scenarios.

Responding to a message
-----------------------

If your plugin receives a message through the :py:meth:`~machine.plugins.decorators.respond_to` or 
:py:meth:`~machine.plugins.decorators.listen_to` decorators, the simplest way to reply is using 
:py:meth:`msg.reply() <machine.plugins.base.Message.reply>`. It takes 2 parameters:
	
	**text**: the message you want to send
	
	**in_thread**: if Slack Machine should reply to the original message in-thread

:py:meth:`msg.reply() <machine.plugins.base.Message.reply>` will start the reply with a mention 
of the sender of the original message.

Example:

.. code-block:: python

    @respond_to(r"^I love you")
    def spread_love(self, msg):
        msg.reply("I love you too!")

If this function is triggered by a message *@superbot I love you*, sent by **@john**, the 
response will be: *@john: I love you too!*

You can also use :py:meth:`msg.reply_webapi() <machine.plugins.base.Message.reply_webapi>` instead, 
which has 2 extra parameters that unlock 2 extra features:

	**attachments**: add `attachments`_ to your message

	**ephemeral**: if ``True``, the message will be visible only to the sender of the original message.

	.. _attachments: https://api.slack.com/docs/message-attachments

There are 2 more methods to respond to a message in the same channel: 
:py:meth:`msg.say() <machine.plugins.base.Message.say>` and 
:py:meth:`msg.say_webapi() <machine.plugins.base.Message.say_webapi>`. 
These are very similar to their ``reply`` counterparts, with the exception that these won't 
mention the sender of the original message.

If you want to reply to the sender of the original message in a DM instead of in the original 
channel, you can use the :py:meth:`msg.reply_dm() <machine.plugins.base.Message.reply_dm>` or 
:py:meth:`msg.reply_dm_webapi() <machine.plugins.base.Message.reply_dm_webapi>` methods. This 
will open a DM convo between the sender of the original message and the bot (if it doesn't exist 
already) and send a message there. If the original message was already received in a DM channel, 
this is no different than using ``reply()`` or ``reply_webapi()``.

Message properties
------------------

The :py:class:`~machine.plugins.base.Message` object your plugin function receives, has some 
convenient properties about the message that triggered the function:

	**sender**: a User object with information about the sender, such as their ``id`` and ``name``

	**channel**: a Channel object with information about the channel the message was received in

	**text**: the contents of the original message

Plugin properties
-----------------

The :py:class:`~machine.plugins.base.MachineBasePlugin` class every plugin extends, exposes 
some properties about your Slack workspace. These properties are not filled when your 
plugin is instantiated, but reflect the current status of the Slack client:

	**users**: a list of User objects for users that Slack Machine knows about. This is usually 
	all the active users in your Slack workspace

	**channels**: a list of Channel objects for channels that Slack Machine knows about. This 
	contains all the public channels in your Slack workspace, plus all private channels 
	that your Slack Machine instance was invited to

Sending messages without a msg object
-------------------------------------

There are situations in which you want to send messages to users/channels, but there is no 
original message to respond to. For example when implementing a ``catch_all`` method, or when 
using the :py:meth:`~machine.plugins.decorators.process` decorator. In this case you can call 
functions similar as those described before, but from your plugin itself: 
:py:meth:`self.say() <machine.plugins.base.MachineBasePlugin.say>`, 
:py:meth:`self.say_webapi() <machine.plugins.base.MachineBasePlugin.say_webapi>`, 
:py:meth:`self.send_dm() <machine.plugins.base.MachineBasePlugin.send_dm>` and 
:py:meth:`self.send_dm_webapi() <machine.plugins.base.MachineBasePlugin.send_dm_webapi>`.

These behave similar to their :py:class:`~machine.plugins.base.Message` counterparts, except that 
they require a channel id or name, or user id or name (in case of DM) to be passed in.

Scheduling messages
-------------------

Sometimes you want to reply to a message, send a message to some channel, send a DM etc. but 
you don't want to do it *now*. You want to do it in **the future**. Slack Machine provides 
**scheduled** versions of many methods, both in the 
:py:class:`~machine.plugins.base.MachineBasePlugin` all plugins extend from and in the 
:py:class:`~machine.plugins.base.Message` object :py:meth:`~machine.plugins.decorators.respond_to` 
and :py:meth:`~machine.plugins.decorators.listen_to` functions receive. These methods can be 
recognized by their **_scheduled** prefix. They work almost the same as their regular counterparts, 
except that they receive 1 extra argument: a :py:class:`datetime <datetime.datetime>` object that tells 
Slack Machine *when* to send the message.

Example:

.. code-block:: python

    @respond_to(r"greet me in the future")
    def future(self, msg):
        msg.say("command received!")
        in_10_sec = datetime.now() + timedelta(seconds=10)
        msg.reply_dm_scheduled(in_10_sec, "A Delayed Hello!")

This function will send a greeting 10 seconds after it has received a message: 
*@superbot greet me in the future*.

There are a couple of caveats:

	Scheduled versions of methods cannot reply to threads using ``in_thread`` or ``thread_ts``. 
	This was done because it doesn't make sense to reply to a thread in the future. Threads 
	are for interaction **now**.

	You cannot schedule a reaction to a message. It doesn't make sense to react to a message 
	in the future.

For more information about scheduling message, have a look at the :ref:`api documentation`.

.. _emitting-events:

Emitting events
---------------

Your plugin can emit arbitrary events that other plugins (or your own) can listen for. Events 
are a convenient mechanism for exchanging data between plugins. Emitting an event is done with 
:py:meth:`self.emit() <machine.plugins.base.MachineBasePlugin.emit>`. You have to provide a name 
for the event you want to emit, so others can listen for an event by that name. You can optionally 
provide extra data as keyword arguments.

Example:

.. code-block:: python

    @respond_to(r"I have used the bathroom")
    def broadcast_bathroom_usage(self, msg):
        self.emit('bathroom_used', toilet_flushed=True)


