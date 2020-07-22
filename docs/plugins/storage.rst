.. _plugin storage:

Storage
=======

Slack Machine provides persistent storage that can easily be accessed from plugins through
``self.storage``. This field contains an instance of :py:class:`~machine.storage.PluginStorage`,
which lets you store, retrieve and remove values by key, check for the existence of a key and get
information about the current size of the underlying storage.

The :py:class:`~machine.storage.PluginStorage` class interfaces with whatever storage backend Slack Machine
is configured with. You can read more about the available storage backends in the :ref:`user guide <storage options>`.

Example:

.. code-block:: python

    @respond_to(r"store (?P<text>.*) under (?P<key>\w+)")
    def store(self, msg, text, key):
        self.storage.set(key, text)
        msg.say("'{}' stored under {}!".format(text, key))

    @respond_to(r"retrieve (?P<key>\w+)")
    def retrieve(self, msg, key):
        data = self.storage.get(key)
        if data:
            msg.say("'{}' retrieved from <{}>!".format(data, key))
        else:
            msg.say("Key not found!")

    @respond_to(r"delete (?P<key>\w+)")
    def delete(self, msg, key):
        self.storage.delete(key)
        msg.say("data in <{}> deleted!".format(key))

    @respond_to(r"does (?P<key>\w+) exist?")
    def exists(self, msg, key):
        # if key in self.storage
        if self.storage.has(key):
            msg.say("<{}> exists.".format(key))
        else:
            msg.say("<{}> does not exist!".format(key))

    @respond_to(r"size")
    def size(self, msg):
        human_size = self.storage.get_storage_size_human()
        msg.say("storage size: {}".format(human_size))

Shared vs non-shared
--------------------

By default, when you store, retrieve and remove data by key, Slack Machine will automatically namespace
the keys you use with the fully qualified classname of the plugin the storage is used from. This is
done to prevent plugins from changing or even deleting each others data. So when you do this:

.. code-block:: python

	class MyPlugin:
	# resides in module my.plugin.package

	def some_function():
		self.set('my-key', 'my-data')

Slack Machine will send the key ``my.plugin.package.MyPlugin:my-key`` to the storage backend.

You can override this behaviour by setting the ``shared`` parameter to ``True`` when calling a storage
related function that requires a key as parameter. This keep the key global (ie. non-namespaced). This
is useful when you want to share data between plugins. Use this feature with care though, as you can
destroy data that belongs to other plugins!

Implementing your own storage backend
-------------------------------------

You can implement your own storage backend by subclassing :py:class:`~machine.storage.backends.base.MachineBaseStorage`.
You only have to implement a couple of methods and you don't have to take care of namespacing of keys, as
Slack Machine will do that for you.
