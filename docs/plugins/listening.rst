.. _listening:

Listening for things
====================

Slack Machine allows you to listen for various different things and respond to that. By decorating 
functions in your plugin using the :ref:`decorators-section` Slack Machine provides, you can tell 
Slack Machine to run those functions when something specific happens.

Listen for a mention
--------------------

The :py:meth:`~machine.plugins.decorators.respond_to` decorator tells Slack Machine to listen 
for messages mentioning your bot and matching a specific pattern. Slack Machine will hear messages 
sent in any channel or private group it is a member of. For a message to trigger a function 
decorated by ``@respond_to(...)``, the message has to *start* with a mention of your 
bot. The exception is direct messages sent to the bot, they don't have to include a mention 
to trigger ``@respond_to``.

``@respond_to`` takes 2 parameters:
    
    ``regex`` (*required*): the regular expression Slack Machine should listen for. The regex 
    pattern should **not** account for the mention of your bot, as Slack Machine will remove 
    the mention before looking for a match. Slack Machine listens for any occurrence of the 
    pattern in the message, so if you want to specifically match the whole message, you can 
    anchor your pattern using the ``^`` and ``$`` symbols.

    ``flags`` (optional): can be used to pass flags for the regex matching 
    as defined in the :py:mod:`re` module. By default :py:data:`re.IGNORECASE` is applied.

How your function will be called
""""""""""""""""""""""""""""""""

Your function will be called with a :py:class:`~machine.plugins.base.Message` object that represents the message that 
triggered the function. It not only contains the message text itself, but also has many convenient 
methods for replying.

Example:

.. code-block:: python

    @respond_to(r"^I love you")
    def spread_love(self, msg):
        msg.reply("I love you too!")

The regex pattern can optionally contain `named groups`_ that will be captured and passed to your 
function as keyword arguments.

.. _named groups: http://www.regular-expressions.info/named.html

Example:

.. code-block:: python

    @respond_to(r"You deserve (?P<num_stars>\d+) stars!")
    def award(self, msg, num_stars):
        stars_back = int(num_stars) + 1
        msg.reply("Well, you deserve {}!".format(stars_back))

Hear any message
----------------

The :py:meth:`~machine.plugins.decorators.listen_to` decorator works similar as the 
The :py:meth:`~machine.plugins.decorators.respond_to` decorator, but it will hear *any* 
message matching a pattern, without the bot being explicitly mentioned. ``@listen_to`` takes 
the same parameters as ``@respond_to``.

Example:

.. code-block:: python

    @listen_to(r"go for it")
    @listen_to(r"go 4 it")
    def go_for_it(self, msg):
        msg.say("https://a-z-animals.com/media/animals/images/original/gopher_2.jpg")

As you can see, you can also apply the same decorator multiple times to a function, each 
time with different arguments. Of course you can also combine different decorators on one 
function.

More flexibility with events
----------------------------

If you want your bot to respond to other things than messages, you can do so using the 
:py:meth:`~machine.plugins.decorators.process` decorator. ``@process`` requires an ``event_type`` 
as parameter and will trigger the decorated function any time an event of the specified type 
happens. It can listen to any `Slack event`_ that is supported by the RTM API.

The received event will be passed to your function.

.. _Slack event: https://api.slack.com/events

The following example will listen for the `reaction_added`_ event to know if a *reaction* was 
added to a message, and will match that reaction:

.. code-block:: python

    @process("reaction_added")
    def match_reaction(self, event):
        emoji = event['reaction']
        channel = event['item']['channel']
        ts = event['item']['ts']
        self.react(channel, ts, emoji)

.. _reaction_added: https://api.slack.com/events/reaction_added

As you can see, ``@process`` gives you a lot of flexibility by allowing you to process any 
event Slack Machine does not provide a specific decorator for.

Catch all
---------

Slack Machine also provides a way to listen to **all events** that Slack produces. Your plugin 
should implement a method ``catch_all`` that takes one parameter. That function will be called 
for each event, with the received event.

Take action on a Schedule
-------------------------

Slack Machine can also run functions on a schedule, using the :py:meth:`~machine.plugins.decorators.schedule` 
decorator. ``@schedule`` behaves like Linux/Unix `Crontab`_, and receives similar parameters. You can 
specify on what schedule your function should be called. When your function is called, it will not receive 
any arguments except ``self``, but you can of course call any :py:class:`~machine.plugins.base.MachineBasePlugin` 
methods to send message and do other things.

Example:

.. code-block:: python

    @schedule(hour='9-17', minute='*/30')
    def movement_reminder(self):
        self.say('general',
                 '<!here> maybe now is a good time to take a short walk!')

.. _Crontab: http://www.adminschoice.com/crontab-quick-reference


