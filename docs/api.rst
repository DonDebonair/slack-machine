.. _api:

API Documentation
=================

This is the API documentation of all the classes and functions relevant for Plugin development. 
The rest of the code deals with the internal workings of Slack Machine and is very much an 
implementation detail and subject to change. Therefore it is not documented.

Plugin classes
--------------

The following 2 classes form the basis for Plugin development.

.. autoclass:: machine.plugins.base.MachineBasePlugin
   :members:

-----

.. autoclass:: machine.plugins.base.Message
   :members:

.. _decorators-section:

Decorators
----------

These are the decorators you can use to have Slack Machine respond to specific things 
(events, messages, etc.)

.. automodule:: machine.plugins.decorators
   :members:
