# Introduction

## Philosophy

Slack Machine is a sexy, simple, yet powerful and extendable bot
platform for Slack.

Slack Machine should be:

-   Full-featured
-   Easy to extend
-   Easy to contribute to (the core)
-   Fun to use
-   Fun to extend

My dream would be, that a community springs up around Slack Machine,
that produces a myriad of useful plugins that are easy to install and
use.

## Non-goals

These are non-goals for me at the moment, but that might change in the
future:

-   Support for other backends than Slack
-   Built-in AI. At least not in the core, although whatever
    intelligence developers put into their plugins, is cool of course

## Why Slack Machine was built

I love Slack, and I use it on a daily basis, both at work and in my
private life. Due to the powerful APIs that Slack exposes, it's not
only great for chatting, but also for automation. We developers *love*
automation, so I wanted to add some of that to the Slack teams I'm a
member of. Obviously, there have already been many attempts to leverage
this extensibility of Slack, considering the many bots/bot
frameworks/chatops frameworks out there.

**Why build another one?!**

All of the options that I could find, were inadequate for some reason.
I've used [Hubot](https://hubot.github.com/) a lot in the past, but
Coffeescript (or Javascript for that matter), just doesn't click with
me. I personally feel that Python is a *great* language to tackle this
sort of problem, so I started looking for Slack bots written in Python.
At the time I created Slack Machine, these were the options I could find:

- [python-rtmbot](https://github.com/slackapi/python-rtmbot): Created
  by the Slack team, this bot is very barebones and exposes a very
  low-level plugin API. This makes it hard/tedious to write plugins for it.
  It is not mainainted anymore
- [slackbot](https://github.com/lins05/slackbot): Has a more
  high-level plugin API, which is built on the right ideas in terms of
  developer friendlyness. But it was lacking some features that I want
  in a bot (among other things: scheduling, persistent storage and a
  help-feature), and I found that the plugin architecture didn't
  allow for proper plugin organisation. This made me decide not to
  contribute, and instead start my own project.
- [Will](http://skoczen.github.io/will/): This was originally not a bot for Slack,
  but for Hipchat. I'm including it anyways, because Will comes
  closests to what I want, both in terms of feature set and plugin
  API. At the time I created Slack Machine, it only supported HipChat
  ([for the time being](http://skoczen.github.io/will/roadmap/#project-roadmap),
  anyways), and I personally found the code quite hard to read.
  Update: Will now also supports Slack. But I feel that a framework
  specialized in a specific chat platforms is better than a framework
  trying to support different platforms.

So, in the end I decided that writing a full-featured, easy-to-extend
Slack bot, written in Python, would be cool new project to take up.

!!! note

    The above was written 4 years ago and a lot has changed since then.
    The Slack team has created [Bolt](https://slack.dev/bolt-python/tutorial/getting-started),
    a bot framework that is quite similar to Slack Machine. There are still
    differences in the way code is organized and I feel that Slack Machine
    is better suited to build complex Slack bots with in which code is
    organized in multiple plugins.

    I plan to keep maintaining Slack Machine and bringing it up to date
    with current best practices, so that the features and developer experience
    are on-par with or better than Bolt

## Acknowledgements

Slack Machine owes a great deal of debt to the aforementioned packages.
Parts of the API of Slack Machine were inspired by those packages, and I
was at a great advantage while building Slack Machine because I was able
to look at existing code to get an idea on how to approach certain
problems. While obviously I'd like to think I have improved upon my
inspirations, Slack Machine couldn't have existed without them.

## Slack Machine License

> MIT License
>
> Copyright (c) 2018 Daan Debie
>
> Permission is hereby granted, free of charge, to any person obtaining
> a copy of this software and associated documentation files (the
> "Software"), to deal in the Software without restriction, including
> without limitation the rights to use, copy, modify, merge, publish,
> distribute, sublicense, and/or sell copies of the Software, and to
> permit persons to whom the Software is furnished to do so, subject to
> the following conditions:
>
> The above copyright notice and this permission notice shall be
> included in all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
> EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
> MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
> IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
> CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
> TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
> SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
