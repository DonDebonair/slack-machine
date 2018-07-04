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

More flexibility with Slack events
----------------------------------

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

.. _listen-events:

Events
------

Slack Machine can respond to events that are emitted by your plugin(s) or plugins of others, or 
events generated by parts of Slack Machine itself. You can use the 
:py:meth:`~machine.plugins.decorators.on` decorator on a function to run that function whenever 
a certain event is emitted somewhere.

Example:

.. code-block:: python

    @on('bathroom_used')
    def call_cleaning_department(self, **kwargs):
        self.say('cleaning-department', '<!here> Somebody used the toilet!')

This function will be called whenever the ``bathroom_used`` event is emitted somewhere.

Some things to be aware of:

    Event names are global, every plugin can emit and listen for the same events. This is by 
    design, because this way, you can use events to exchange data between plugins. Events can 
    be a way to expose a "public API" for plugins. But this can also mean your functions are 
    unexpectedly triggered by events sent by other plugins, especially if the event names you 
    choose are very generic.

    When emitting events, plugins can attach whatever variables they want to the event, and 
    when listening for an event, your function will be called with whatever arguments were 
    attached to the event when the event was emitted. It's therefor a good idea to always 
    include ``**kwargs`` as a catch-all, otherwise your function could return an error when 
    it's called with arguments that have not been explicitly defined.

You can read :ref:`emitting-events` to learn how to emit events from your plugins.

HTTP Listener
-------------

Slack Machine has a built-in HTTP server that can listen for incoming requests. `Bottle`_ is used
for this feature. You can use the :py:meth:`~machine.plugins.decorators.route` decorator to mark
functions in your plugin classes to listen for specific HTTP calls. The decorator accepts the same
arguments as the `Bottle route()`_ decorator. You can return anything that Bottle view functions
can return, because your functions will be delegated to the Bottle router.
You can of course also use any of the features that the
:py:class:`~machine.plugins.base.MachineBasePlugin` gives you, such as sending a message to a
user or a channel.

Example:

.. code-block:: python

    @route("/hello")
    @route("/hello/<name>")
    def my_exposed_function(self, name="World"):
        self.say('my-channel', '{} is talking to me'.format(name))
        return {"hello": name}

    # listen to specific HTTP verbs
    @route("/status", method=["POST", "GET"])
    def my_other_function(self):
        return {"status": "I'm a-okay!"}

Slack Machine supports any of the server backends that `Bottle supports`_. You can set the name
of the server backend you want in your settings as ``HTTP_SERVER_BACKEND``.

If you don't need this functionality, you can disable the HTTP server by setting ``DISABLE_HTTP``
to ``True`` in your settings.

The built-in HTTP server which can be configured using the following settings:

.. code-block:: python

    # Should the HTTP server be enabled?
    DISABLE_HTTP = False

    # Which serving backend should `bottle` use?
    HTTP_SERVER_BACKEND = 'wsgiref'

    # Host address to listen on
    HTTP_SERVER_HOST = '0.0.0.0'

    # Host port to listen on
    HTTP_SERVER_PORT = 8080

.. _Bottle: https://bottlepy.org
.. _Bottle route(): https://bottlepy.org/docs/0.12/api.html#bottle.route
.. _Bottle supports: https://bottlepy.org/docs/0.12/deployment.html#switching-the-server-backend
