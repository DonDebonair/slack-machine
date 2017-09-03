.. _introduction:

Introduction
============

Philosophy
----------

Slack Machine should be:

- Full-featured
- Easy to extend
- Easy to contribute to (the core)
- Fun to use
- Fun to extend

My dream would be, that a community springs up around Slack Machine, that produces a myriad of 
useful plugins that are easy to install and use.

Non-goals
---------

These are non-goals for me at the moment, but that might change in the future:

- Support for other backends than Slack
- Build-in AI. At least not in the core, although whatever intelligence developers put into their 
plugins, is cool of course

Why Slack Machine was built
---------------------------

I love Slack, and I use it on a daily basis, both at work and in my private life. Due to the powerful 
APIs that Slack exposes, it's not only great for chatting, but also for automation. We developers 
*love* automation, so I wanted to add some of that to the Slack teams I'm a member of. 
Obviously, there have already been many attempts to leverage this extensibility of 
Slack, considering the many bots/bot frameworks/chatops frameworks out there.

**Why build another one?!**

All of the options that I could find, were inadequate for some reason. I've used `Hubot`_ a lot 
in the past, but Coffeescript (or Javascript for that matter), just doesn't click with me.
I personally feel that Python is a *great* language to tackle this sort of problem, so I 
started looking for Slack bots written in Python. These are the options I could find, and why I 
decided not to go with each of them:

- `python-rtmbot`_: Created by the Slack team, this bot is very barebones and exposes a very 
  low-level plugin API. This makes it hard/tedious to write plugins for it.
- `slackbot`_: Has a more high-level plugin API, which is built on the right ideas in terms of 
  developer friendlyness. But it was lacking some features that I want in a bot (among other things: 
  scheduling, persistent storage and a help-feature), and I found that the plugin architecture didn't 
  allow for proper plugin organisation. This made me decide not to contribute, and instead start my 
  own project.
- `Will`_: This not a bot for Slack, but for Hipchat. I'm including it anyways, because Will 
  comes closests to what I want, both in terms of feature set and plugin API. Sadly, it only 
  supports HipChat (`for the time being`_, anyways), and I personally found the code quite hard 
  to read.

So, in the end I decided that writing a full-featured, easy-to-extend Slack bot, written in Python, 
would be cool new project to take up.

.. _Hubot: https://hubot.github.com/
.. _python-rtmbot: https://github.com/slackapi/python-rtmbot
.. _slackbot: https://github.com/lins05/slackbot
.. _Will: http://skoczen.github.io/will/
.. _for the time being: http://skoczen.github.io/will/roadmap/#project-roadmap

Slack Machine License
---------------------

    .. include:: ../../LICENSE