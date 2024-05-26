# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), with a smattering of
[Common Changelog](https://common-changelog.org/#21-file-format) thrown in, most notably _references_, _authors_ and
_prefixes_. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.37.0] - 2024-05-26

### Added

- Support for **Block actions**, coming from interactive elements from [Block Kit](https://api.slack.com/block-kit)
  ([#1034](https://github.com/DonDebonair/slack-machine/pull/1034) with help from
  [**pawelros**](https://github.com/pawelros))

### Changed

- Bump `slack-sdk` from 3.27.1 to 3.27.2

## [0.36.0] - 2024-05-04

### Added

- Replace `flake8`, `isort` and `black` with `ruff` ([#1027](https://github.com/DonDebonair/slack-machine/pull/1027))
- Add Python 3.12 ([#1028](https://github.com/DonDebonair/slack-machine/pull/1028))

### Changed

- Update Github Actions ([#1008](https://github.com/DonDebonair/slack-machine/pull/1008))
- Bump `slack-sdk` from 3.21.3 to 3.27.1
- Bump `httpx` from 0.24.1 to 0.27.0
- Bump `pydantic` from 2.3.0 to 2.7.1
- Bump `cryptography` from 41.0.3 to 42.0.4
- Bump `aiohttp` from 3.8.5 to 3.9.5
- Bump `urllib3` from 1.26.16 1.26.18
- Bump `structlog` from 23.1.0 to 24.1.0
- Bump `redis` from 5.0.0 to 5.0.4
- Bump `pyee` from 11.0.0 to 11.1.0
- Bump `aioboto3` from 11.3.0 to 12.4.0
- Bump `tzdata` from 2023.3 to 2024.1
- Bump `aiosqlite` from 0.19.0 to 0.20.0
- Bump `hiredis` from 2.2.3 to 2.3.2

## [0.35.0] - 2023-09-03

### Added

- Incoming requests/events from Slack that the Slack App is subscribed to, will be logged when `LOGLEVEL` is set to
  `DEBUG` ([#876](https://github.com/DonDebonair/slack-machine/pull/876))

### Changed

- **Breaking:** the optional `init()` method of plugins is now expected to be `async`. This allows plugin authors to
  interact with Slack during plugin initialization through Slack Machine's plugin API.
  ([#868](https://github.com/DonDebonair/slack-machine/pull/868))
- Standard app manifest for Slack Machine now also enables listening for the `app_home_opened` event
- Bump `aiosqlite` from 0.18.0 to 0.19.0
- Bump `apscheduler` from 3.10.1 to 3.10.4
- Bump `redis` from 4.6.0 to 5.0.0
- Bump `pyee` from 10.0.2 to 11.0.0
- Bump `pydantic` from 2.2.1 to 2.3.0

### Fixed

- Use conversations_setTopic instead of channels_setTopic for setting channel topic
  ([#869](https://github.com/DonDebonair/slack-machine/pull/869) by
  [**@jogendra**](https://github.com/jogendra))

## [0.34.2] - 2023-08-13

### Fixed

- Users indexed by email and related functions are now exposed through the plugin interface
  ([#852](https://github.com/DonDebonair/slack-machine/pull/852))

## [0.34.1] - 2023-08-13

### Added

- Slack users are now indexed by their email as well, allowing fast lookups by email
  ([#849](https://github.com/DonDebonair/slack-machine/pull/849))

### Fixed

- All logging in Slack Machine is now done through structlog instead of the Python stdlib logger
  ([#850](https://github.com/DonDebonair/slack-machine/pull/850))

## [0.34.0] - 2023-08-13

### Added

- Add support to set topic on channels ([#839](https://github.com/DonDebonair/slack-machine/pull/839) by
  [**@jogendra**](https://github.com/jogendra))
- Add SQLite storage backend ([#844](https://github.com/DonDebonair/slack-machine/pull/844) by
  [**@cp-richard**](https://github.com/cp-richard))

### Changed

- Bump `httpx` from 0.24.0 to 0.24.1
- Bump `aiohttp` from 3.8.4 to 3.8.5
- Bump `certifi` from 2022.12.7 to 2023.7.22
- Bump `pyee` from 9.1.0 to 10.0.2
- Bump `pydantic` from 1.10.7 to 2.1.1 ([#840](https://github.com/DonDebonair/slack-machine/pull/840))

### Removed

- **Breaking:** Remove Python 3.7 support ([#846](https://github.com/DonDebonair/slack-machine/pull/846))

## [0.33.0] - 2023-05-15

### Added

- Add support for [slash commands](https://api.slack.com/interactivity/slash-commands)
  ([#787](https://github.com/DonDebonair/slack-machine/pull/787))

### Changed

- **Breaking:** move `Message` class from `machine.plugins.base` to `machine.plugins.message`
- Use dots only for referencing the fully-qualified name of classes and functions instead of using a colon before
  the class name
- Bump `tzdata` from 2022.6 to 2023.3
- Bump `slack-sdk` from 3.19.4 to 3.21.3
- Bump `aioboto3` from 10.1.0 to 11.2.0
- Bump `aiohttp` from 3.8.3 to 3.8.4
- Bump `redis` from 4.3.5 to 4.5.5
- Bump `hiredis` from 2.0.0 to 2.2.3
- Bump `pydantic` from 1.10.2 to 1.10.7
- Bump `httpx` from 0.23.1 to 0.24.0
- Bump `apscheduler` from 3.9.1.post1 to 3.10.1
- Bump `structlog` from 22.3.0 to 23.1.0
- Bump `pyee` from 9.0.4 to 9.1.0

## [0.32.0] - 2022-11-27

### Added

- Add Python 3.11 support ([#676](https://github.com/DonDebonair/slack-machine/pull/676))
- Expose web client of Slack SDK ([#677](https://github.com/DonDebonair/slack-machine/pull/677))

### Changed

- Bump `dill` from 0.3.5.1 to 0.3.6
- Bump `slack-sdk` from 3.19.1 to 3.19.4
- Bump `tzdata` from 2022.5 to 2022.6
- Bump `apscheduler` from 3.9.1 to 3.9.1.post1
- Bump `httpx` from 0.23.0 to 0.23.1
- Bump `redis` from 4.3.4 to 4.3.5
- Bump `structlog` from 22.1.0 to 22.3.0

### Fixed

- Fix documentation typos ([#665](https://github.com/DonDebonair/slack-machine/pull/665) by
  [**@bennylu2**](https://github.com/bennylu2))

## [0.31.0] - 2022-10-21

### Changed

- Moved Slack Machine community chat to [Slack](https://join.slack.com/t/slack-machine-chat/shared_invite/zt-1g87tzvlf-8bV_WnY3JZyaYNnRFwRd~w)
- Type-hint coverage is now 100% so mypy is happy ([#633](https://github.com/DonDebonair/slack-machine/pull/633))
- Update _pyproject.toml_ to conform to Poetry 1.2 dependency specification
  ([#657](https://github.com/DonDebonair/slack-machine/pull/657))
- Replace `dacite` with `pydantic` to create models for Slack API interactions
  ([#659](https://github.com/DonDebonair/slack-machine/pull/659))
- Bump `aiohttp` from 3.8.1 to 3.8.3
- Bump `slack-sdk` from 3.18.3 to 3.19.1
- Bump `tzdata` from 2022.4 to 2022.5
- Bump `aioboto3` from 10.0.0 to 10.1.0
- Add changelog to keep track of updates
- Move to [structlog](https://www.structlog.org) for logging, fixes
  [#599](https://github.com/DonDebonair/slack-machine/issues/599)
  ([#663](https://github.com/DonDebonair/slack-machine/pull/663))

### Removed

- Remove unused settings: `DISABLE_HTTP`, `HTTP_SERVER_HOST`, `HTTP_SERVER_PORT`, `HTTP_SERVER_BACKEND`, `HTTPS_PROXY`,
  `KEEP_ALIVE`

## [0.30.0] - 2022-08-30

### Changed

- Bump `slack-sdk` from 3.18.1 to 3.18.3 ([#619](https://github.com/DonDebonair/slack-machine/pull/619))

### Removed

- **Breaking:** Remove sync version, it's all async now baby! :dancing_men:

## [0.28.2] - 2022-08-30

### Changed

- Make handling changed message configurable in async mode ([#613](https://github.com/DonDebonair/slack-machine/pull/613))
- Add tests for slack client ([#614](https://github.com/DonDebonair/slack-machine/pull/614))

## [0.28.1] - 2022-08-28

### Added

- Add support for pinning/unpinning of messages ([#611](https://github.com/DonDebonair/slack-machine/pull/611))

### Changed

- Add support for listening to message change events ([#594](https://github.com/DonDebonair/slack-machine/pull/594)
  with help from [**@cchadowitz-pf**](https://github.com/cchadowitz-pf))

## [0.28.0] - 2022-08-28

### Added

- Add support to async version for scheduling messages and running plugin functions on a schedule
  ([#610](https://github.com/DonDebonair/slack-machine/pull/610))

## [0.27.2] - 2022-08-14

### Fixed

- `aioboto3` types are only relevant for type checking, so move imports inside type checking guard

## [0.27.1] - 2022-08-14

### Changed

- Add documentation for DynamoDB storage backend ([#603](https://github.com/DonDebonair/slack-machine/pull/603))

### Fixed

- Add `aioboto3` as optional dependency so extras can be satisfied ([#604](https://github.com/DonDebonair/slack-machine/pull/604))

## [0.27.0] - 2022-08-14

### Added

- Add DynamoDB storage backend ([#602](https://github.com/DonDebonair/slack-machine/pull/602) by
  [**@jkmathes**](https://github.com/jkmathes))
- Add `black`, `isort` and other linters/formatters to create uniform code style ([#597](https://github.com/DonDebonair/slack-machine/pull/597))

### Changed

- Update documentation for builtin plugins, fixes [#396](https://github.com/DonDebonair/slack-machine/issues/396)
  ([#598](https://github.com/DonDebonair/slack-machine/pull/598))
- Replace `requests` with `httpx` for async http calls in meme plugin and share memes as blocks
  ([#600](https://github.com/DonDebonair/slack-machine/pull/600))
- Replace `requests` with `httpx` for async http calls in Google image search plugin ([#601](https://github.com/DonDebonair/slack-machine/pull/601))

## [0.26.1] - 2022-08-13

### Fixed

- Various documentation fixes
- Fix project metadata

## [0.26.0] - 2022-08-13

### Added

- Slack Machine now supports [asyncio](https://docs.python.org/3/library/asyncio.html) using the [Slack Events API](https://api.slack.com/apis/connections/events-api)
  and [Socket Mode](https://api.slack.com/apis/connections/socket)! :racing_car:

### Changed

- Bump `redis` from 4.2.0 to 4.3.4
- Bump `slack-sdk` from 3.15.2 to 3.18.1

## [0.25.0] - 2022-03-27

### Changed

- Bump `redis` from 4.0.2 to 4.2.0
- Bump `slack-sdk` from 3.12.0 to 3.15.2
- Bump `requests` from 2.26.0 to 2.27.1
- Bump `apscheduler` from 3.8.1 to 3.9.1

### Fixed

- Fix expected payload of events when updating channel cache, fixes [#526](https://github.com/DonDebonair/slack-machine/issues/526)
  ([#565](https://github.com/DonDebonair/slack-machine/pull/565))

## [0.24.0] - 2021-12-01

### Added

- Add Python 3.10 support

### Changed

- Bump `redis` from 3.5.3 to 4.0.2
- Bump `apscheduler` from 3.8.0 to 3.8.1
- Move documentation from Sphinx to MkDocs and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
  for beautiful docs ([#514](https://github.com/DonDebonair/slack-machine/pull/514))
- Switch from `slackclient` to `slack_sdk` library, fixes [#443](https://github.com/DonDebonair/slack-machine/issues/443)

### Removed

- **Breaking:** Remove Python 3.6 support

## [0.23.2] - 2021-10-17

### Fixed

- Bring back script to run Slack Machine

## [0.23.1] - 2021-10-17

### Changed

- Document all contributors

### Fixed

- Install the right extra packages for Redis

### Removed

- **Breaking:** HBase storage backend has been removed

## [0.23.0] - 2021-10-16

### Changed

- Switch to Poetry for project and dependency management
- Bump `apscheduler` from 3.7.0 to 3.8.0

### Fixed

- Various CI fixes

## [0.22.0] - 2021-09-12

### Changed

- Bump `dill` from 0.3.3 to 0.3.4
- Bump `requests` from 2.25.1 to 2.26.0
- Bump `cython` from 0.29.23 to 0.29.24
- Use Github Actions for CI and drop Travis ([#492](https://github.com/DonDebonair/slack-machine/pull/492))
- Switch `master` branch to `main` to get with the times

### Fixed

- Only cover named channels when attempting to find a channel by name ([#483](https://github.com/DonDebonair/slack-machine/pull/483)
  by [**@arusahni**](https://github.com/arusahni))

## [0.21.1] - 2021-08-01

### Changed

- Add channel members to `Channel` model and keep members up-to-date through Slack events ([#485](https://github.com/DonDebonair/slack-machine/pull/485)
  by [**@arusahni**](https://github.com/arusahni))

## [0.21.0] - 2021-04-25

### Added

- Add Gitter chat room to facilitate discussions about Slack Machine
- Add Role-based access controls feature for plugins ([#321](https://github.com/DonDebonair/slack-machine/pull/321)
  by [**@davidolrik**](https://github.com/davidolrik))
- Add Python 3.9 support

### Changed

- Move to Dependabot from PyUp to manage automatic dependency updates
- Bump `slackclient` from 2.7.3 to 2.9.3
- Bump `requests` from 2.24.0 to 2.25.1
- Bump `dill` from 0.3.2 to 0.3.3
- Bump `dacite` from 1.5.1 to 1.6.0
- Bump `cython` from 0.29.21 to 0.29.23
- Bump `apscheduler` from 3.6.3 to 3.7.0

### Fixed

- Make channel topic creator an optional field in the `Channel` model ([#439](https://github.com/DonDebonair/slack-machine/pull/439)
  by [**@eguven**](https://github.com/eguven))
- Always respond to plugin functions decorated with `@listen_to`, also when bot is addressed in direct message ([#436](https://github.com/DonDebonair/slack-machine/pull/436)
  by [**@eddyg**](https://github.com/eddyg))
- Use `conversations.open` endpoint on Slack WebAPI instead of `im.open` endpoint to open direct message conversations,
  because the latter is deprecated ([#401](https://github.com/DonDebonair/slack-machine/pull/401)
  by [**@cchadowitz-pf**](https://github.com/cchadowitz-pf))

## [0.20.1] - 2020-07-23

### Fixed

- Use `conversations.info` endpoint on Slack WebAPI instead of `channels.info` endpoint, which is deprecated and
  mark optional fields as such in `User` and `Channel` objects
  ([#386](https://github.com/DonDebonair/slack-machine/pull/386) by [**@repudi8or**](https://github.com/repudi8or))

## [0.20.0] - 2020-07-22

### Added

- Support Python 3.8

### Changed

- Bump `dacite` from 1.0.2 to 1.5.1
- Bump `redis` from 3.3.11 to 3.5.3
- Bump `cython` from 0.29.14 to 0.29.21
- Bump `dill` from 0.3.1.1 to 0.3.2
- Bump `requests` from 2.22.0 to 2.24.0
- Bump `slackclient` from 2.5.0 to 2.7.3
- Add `is_thread` property to `Message` class ([#286](https://github.com/DonDebonair/slack-machine/pull/286) by
  [**@davidolrik**](https://github.com/davidolrik))
- Use `conversations.list` endpoint on Slack WebAPI instead of `channels.list` endpoint, which is deprecated and
  include private channels in channel cache ([#329](https://github.com/DonDebonair/slack-machine/pull/329) by
  [**@repudi8or**](https://github.com/repudi8or))
- Include direct messages in channel cache
- Add pre-commit hooks to verify basic things before commiting

### Fixed

- `deleted` property is optional on user responses from Slack WebAPI

## [0.19.2] - 2020-01-05

### Changed

- **Breaking:**: `thread_ts` property on the `Message` class has been renamed to `ts`

### Fixed

- `EchoPlugin` will not respond to itself anymore
- Fixed PyPI classifiers

## [0.19.1] - 2020-01-05

### Fixed

- Fix help plugin
- Fix various typos in the documentation

## [0.19.0] - 2020-01-05

### Changed

- Major version upgrade of `slackclient` from 1.3.1 to 2.5.0
- Refactor code to capture Slack API responses in dataclasses for easier development
- Split internal Slack client into low-level client and high-level facade
- Start adding type hints
- **Breaking:** `self.users` and `self.channels` on the base plugin class now return different objects than before.
  See API documentation for more details. These properties should behave more consistently however, even in workspaces
  with many users.

### Removed

- **Breaking:** Remove `catch_all()` method from base plugin class because it's not supported by the `slackclient`
  library anymore
- **Breaking:** The `*_webapi` methods to send messages do not exist anymore, use the regular counterparts instead. All
  messages are now sent using the Slack WebAPI. The RTM API is still used for listening to messages and events

## [0.18.2] - 2019-11-17

### Fixed

- Fix `bottle` import

## [0.18.1] - 2019-11-17

### Changed

- Bump `apscheduler` from 3.5.3 to 3.6.3
- Bump `redis` from 3.2.0 to 3.3.11
- Bump `happybase` from 1.1.0 to 1.2.0
- Bump `cython` from 0.29.6 to 0.29.14
- Bump `dill` from 0.2.9 to 0.3.1.1
- Bump `bottle` from 0.12.16 to 0.12.17
- Include `bottle` as a vendored dependency to not be dependent on the long release cycles of `bottle`
- Fix deprecation warnings to prepare for Python 3.8
- Allow matching multiline messages in `@listen_to` and `@respond_to` decorators ([#178](https://github.com/DonDebonair/slack-machine/pull/178)
  by [**@seerickcode**](https://github.com/seerickcode))

### Removed

- **Breaking:** drop support for Python 3.4 and 3.5

## [0.18.0] - 2019-03-10

### Changed

- Bump `slackclient` from 1.3.0 to 1.3.1
- Bump `dill` from 0.2.8.2 to 0.2.9
- Bump `bottle` from 0.12.13 to 0.12.16
- Bump `redis` from 2.10.6 to 3.2.0
- Bump `Cython` from 0.28.5 to 0.29.6

## [0.17.0] - 2018-11-10

### Added

- Add support for bot aliases ([#108](https://github.com/DonDebonair/slack-machine/pull/108)
  by [**@seerickcode**](https://github.com/seerickcode))

## [0.16.1] - 2018-09-28

### Changed

- Allow not only direct subclasses of MachineBasePlugin be plugins, but also deeper decendants ([#95](https://github.com/DonDebonair/slack-machine/pull/95)
  by [**@gfreezy**](https://github.com/gfreezy))
- Bump `slackclient` from 1.2.1 to 1.3.0 ([#88](https://github.com/DonDebonair/slack-machine/pull/88))

## [0.16.0] - 2018-09-06

### Added

- Add HBase storage backend

## [0.15.0] - 2018-09-03

### Added

- Add optional keep-alive ping in background thread to keep the connection to Slack alive ([#79](https://github.com/DonDebonair/slack-machine/pull/79)
  by [**@preludedrew**](https://github.com/preludedrew))

  This helps when Slack Machine is running in environments that occasionally "go to sleep", such as Heroku

### Changed

- Bump `apscheduler` from 3.5.1 to 3.5.3
- Fix Python 3.7 builds by using Xenial distro

## [0.14.0] - 2018-07-31

### Added

- Add Python 3.7 support

### Changed

- Add support for configuring HTTP proxy for Slack client ([#69](https://github.com/DonDebonair/slack-machine/pull/64)
  by [**@gfreezy**](https://github.com/gfreezy))

## [0.13.2] - 2018-07-04

### Changed

- Make HTTP server host & port configurable ([#64](https://github.com/DonDebonair/slack-machine/pull/64) by
  [**@pirogoeth**](https://github.com/pirogoeth))
- Bump `dill` from 0.2.7.1 to 0.2.8.2
- Bump `slackclient` from 1.1.3 to 1.2.1

## [0.13.1] - 2018-03-06

### Changed

- Mention webserver functionality in README

## [0.13.0] - 2018-03-06 [YANKED]

_:warning: NOTE: release was yanked due to lack of documentation_

### Added

- Add webserver functionality so plugins can have functions triggered by HTTP requests

### Changed

- Bump `slackclient` from 1.1.2 to 1.1.3

## [0.12.2] - 2018-02-26

### Changed

- Bump `slackclient` from 1.1.0 to 1.1.2
- Memes plugin: support custom meme templates

### Fixed

- Plugin help now properly distinguishes between robot or human help

## [0.12.1] - 2018-01-26

### Fixed

- Fix tests for new plugins

## [0.12.0] - 2018-01-26

### Added

- Add Google Image search plugin
- Add memes plugin based on [Memegen](https://memegen.link/)

## [0.11.0] - 2018-01-22

### Added

- Add help feature so users can see what a bot can do based on documentation provided by plugin authors

## [0.10.0] - 2018-01-21

### Added

- Add optional plugin initialization
- Allow plugins to mark settings as _required_

### Changed

- Bump `apscheduler` from 3.4.0 to 3.5.1

## [0.9.0] - 2017-12-03

### Changed

- Bump `apscheduler` from 3.3.1 to 3.4.0
- Bump `slackclient` from 1.0.9 to 1.1.0
- WebAPI methods will return deserialized API responses ([#14](https://github.com/DonDebonair/slack-machine/pull/14)
  by [**@pirogoeth**](https://github.com/pirogoeth))

### Removed

- **Breaking:** drop support for Python 3.3

## [0.8.0] - 2017-10-15

### Added

- Add support for event listeners and emitting events for inter-plugin communication

## [0.7.0] - 2017-10-13

### Added

- Add scheduling functionality to send messages and run plugin functions on a schedule

### Changed

- Refactor client classes to be singletons so they don't need to be persisted by APScheduler
- Add PyUp to automatically update dependencies

## [0.6.0] - 2017-09-14

### Added

- Add pluggable plugin storage so plugins can store data
- Add 2 storage backends: in-memory and Redis

### Changed

- Drastically improve tests and increase coverage

## [0.5.0] - 2017-09-09

### Changed

- Finish documentation

## [0.4.0] - 2017-09-06

### Added

- Document how to create plugins + plugin API

### Changed

- Decorators can now be used multiple times on the same function

## [0.3.0] - 2017-09-03

### Added

- Basic documentation

## [0.2.0] - 2017-09-01

### Added

- Add tests and CI

## [0.1.0] - 2017-08-29

_First release. Rejoice!_ :wave:

### Added

- A simple, yet powerful and extendable Slack bot framework


[Unreleased]: https://github.com/DonDebonair/slack-machine/compare/v0.37.0...HEAD
[0.37.0]: https://github.com/DonDebonair/slack-machine/compare/v0.36.0...v0.37.0
[0.36.0]: https://github.com/DonDebonair/slack-machine/compare/v0.35.0...v0.36.0
[0.35.0]: https://github.com/DonDebonair/slack-machine/compare/v0.34.2...v0.35.0
[0.34.2]: https://github.com/DonDebonair/slack-machine/compare/v0.34.1...v0.34.2
[0.34.1]: https://github.com/DonDebonair/slack-machine/compare/v0.34.0...v0.34.1
[0.34.0]: https://github.com/DonDebonair/slack-machine/compare/v0.33.0...v0.34.0
[0.33.0]: https://github.com/DonDebonair/slack-machine/compare/v0.32.0...v0.33.0
[0.32.0]: https://github.com/DonDebonair/slack-machine/compare/v0.31.0...v0.32.0
[0.31.0]: https://github.com/DonDebonair/slack-machine/compare/v0.30.0...v0.31.0
[0.30.0]: https://github.com/DonDebonair/slack-machine/compare/v0.28.2...v0.30.0
[0.28.2]: https://github.com/DonDebonair/slack-machine/compare/v0.28.1...v0.28.2
[0.28.1]: https://github.com/DonDebonair/slack-machine/compare/v0.28.0...v0.28.1
[0.28.0]: https://github.com/DonDebonair/slack-machine/compare/v0.27.2...v0.28.0
[0.27.2]: https://github.com/DonDebonair/slack-machine/compare/v0.27.1...v0.27.2
[0.27.1]: https://github.com/DonDebonair/slack-machine/compare/v0.27.0...v0.27.1
[0.27.0]: https://github.com/DonDebonair/slack-machine/compare/v0.26.1...v0.27.0
[0.26.1]: https://github.com/DonDebonair/slack-machine/compare/v0.26.0...v0.26.1
[0.26.0]: https://github.com/DonDebonair/slack-machine/compare/v0.25...v0.26.0
[0.25.0]: https://github.com/DonDebonair/slack-machine/compare/v0.24...v0.25
[0.24.0]: https://github.com/DonDebonair/slack-machine/compare/v0.23...v0.24
[0.23.2]: https://github.com/DonDebonair/slack-machine/compare/v0.23.1...v0.23.2
[0.23.1]: https://github.com/DonDebonair/slack-machine/compare/v0.23...v0.23.1
[0.23.0]: https://github.com/DonDebonair/slack-machine/compare/v0.22...v0.23
[0.22.0]: https://github.com/DonDebonair/slack-machine/compare/v0.21.1...v0.22
[0.21.1]: https://github.com/DonDebonair/slack-machine/compare/v0.21...v0.21.1
[0.21.0]: https://github.com/DonDebonair/slack-machine/compare/v0.20.1...v0.21
[0.20.1]: https://github.com/DonDebonair/slack-machine/compare/v0.20...v0.20.1
[0.20.0]: https://github.com/DonDebonair/slack-machine/compare/v0.19.2...v0.20
[0.19.2]: https://github.com/DonDebonair/slack-machine/compare/v0.19.1...v0.19.2
[0.19.1]: https://github.com/DonDebonair/slack-machine/compare/v0.19...v0.19.1
[0.19.0]: https://github.com/DonDebonair/slack-machine/compare/v0.18.2...v0.19
[0.18.2]: https://github.com/DonDebonair/slack-machine/compare/v0.18.1...v0.18.2
[0.18.1]: https://github.com/DonDebonair/slack-machine/compare/v0.18...v0.18.1
[0.18.0]: https://github.com/DonDebonair/slack-machine/compare/v0.17...v0.18
[0.17.0]: https://github.com/DonDebonair/slack-machine/compare/v0.16.1...v0.17
[0.16.1]: https://github.com/DonDebonair/slack-machine/compare/v0.16...v0.16.1
[0.16.0]: https://github.com/DonDebonair/slack-machine/compare/v0.15...v0.16
[0.15.0]: https://github.com/DonDebonair/slack-machine/compare/v0.14...v0.15
[0.14.0]: https://github.com/DonDebonair/slack-machine/compare/v0.13.2...v0.14
[0.13.2]: https://github.com/DonDebonair/slack-machine/compare/v0.13.1...v0.13.2
[0.13.1]: https://github.com/DonDebonair/slack-machine/compare/v0.13...v0.13.1
[0.13.0]: https://github.com/DonDebonair/slack-machine/compare/v0.12.2...v0.13
[0.12.2]: https://github.com/DonDebonair/slack-machine/compare/v0.12.1...v0.12.2
[0.12.1]: https://github.com/DonDebonair/slack-machine/compare/v0.12...v0.12.1
[0.12.0]: https://github.com/DonDebonair/slack-machine/compare/v0.11...v0.12
[0.11.0]: https://github.com/DonDebonair/slack-machine/compare/v0.10...v0.11
[0.10.0]: https://github.com/DonDebonair/slack-machine/compare/v0.9...v0.10
[0.9.0]: https://github.com/DonDebonair/slack-machine/compare/v0.8...v0.9
[0.8.0]: https://github.com/DonDebonair/slack-machine/compare/v0.7...v0.8
[0.7.0]: https://github.com/DonDebonair/slack-machine/compare/v0.6...v0.7
[0.6.0]: https://github.com/DonDebonair/slack-machine/compare/v0.5...v0.6
[0.5.0]: https://github.com/DonDebonair/slack-machine/compare/v0.4...v0.5
[0.4.0]: https://github.com/DonDebonair/slack-machine/compare/v0.3...v0.4
[0.3.0]: https://github.com/DonDebonair/slack-machine/compare/v0.2...v0.3
[0.2.0]: https://github.com/DonDebonair/slack-machine/compare/v0.1...v0.2
[0.1.0]: https://github.com/DonDebonair/slack-machine/commits/v0.1
