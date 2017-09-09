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



