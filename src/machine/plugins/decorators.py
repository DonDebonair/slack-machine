from __future__ import annotations

import inspect
import re
from collections.abc import Awaitable
from datetime import datetime, tzinfo
from typing import Any, Callable, Protocol, TypeVar, Union, cast

from structlog.stdlib import get_logger
from typing_extensions import ParamSpec

from machine.plugins import ee
from machine.plugins.admin_utils import RoleCombinator, matching_roles_by_user_id
from machine.plugins.base import MachineBasePlugin
from machine.plugins.message import Message
from machine.plugins.metadata import ActionConfig, CommandConfig, MatcherConfig, Metadata, ModalConfig

logger = get_logger(__name__)

P = ParamSpec("P")
R = TypeVar("R", covariant=True, bound=Union[Awaitable[None], MachineBasePlugin])


class DecoratedPluginFunc(Protocol[P, R]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    metadata: Metadata


def process(slack_event_type: str) -> Callable[[Callable[P, R]], DecoratedPluginFunc[P, R]]:
    """Process Slack events of a specific type

    This decorator will enable a Plugin method to process [Slack events] of a specific type. The
    Plugin method will be called for each event of the specified type that the bot receives.
    The received event will be passed to the method when called.

    [Slack events]: https://api.slack.com/events

    Args:
        slack_event_type: type of event the method needs to process. Can be any event supported
            by the [Events API](https://api.slack.com/events?filter=Events)

    Returns:
        wrapped method
    """

    def process_decorator(f: Callable[P, R]) -> DecoratedPluginFunc[P, R]:
        fn = cast(DecoratedPluginFunc, f)
        fn.metadata = getattr(f, "metadata", Metadata())
        fn.metadata.plugin_actions.process.append(slack_event_type)
        return fn

    return process_decorator


def listen_to(
    regex: str, flags: re.RegexFlag | int = re.IGNORECASE, handle_message_changed: bool = False
) -> Callable[[Callable[P, R]], DecoratedPluginFunc[P, R]]:
    """Listen to messages matching a regex pattern

    This decorator will enable a Plugin method to listen to messages that match a regex pattern.
    The Plugin method will be called for each message that matches the specified regex pattern.
    The received [`Message`][machine.plugins.message.Message] will be passed to the method when called.
    Named groups can be used in the regex pattern, to catch specific parts of the message. These
    groups will be passed to the method as keyword arguments when called.

    Args:
        regex: regex pattern to listen for
        flags: regex flags to apply when matching
        handle_message_changed: if changed messages should trigger the decorated function

    Returns:
        wrapped method
    """

    def listen_to_decorator(f: Callable[P, R]) -> DecoratedPluginFunc[P, R]:
        fn = cast(DecoratedPluginFunc, f)
        fn.metadata = getattr(f, "metadata", Metadata())
        fn.metadata.plugin_actions.listen_to.append(MatcherConfig(re.compile(regex, flags), handle_message_changed))
        return fn

    return listen_to_decorator


def respond_to(
    regex: str, flags: re.RegexFlag | int = re.IGNORECASE, handle_message_changed: bool = False
) -> Callable[[Callable[P, R]], DecoratedPluginFunc[P, R]]:
    """Listen to messages mentioning the bot and matching a regex pattern

    This decorator will enable a Plugin method to listen to messages that are directed to the bot
    (ie. message starts by mentioning the bot) and match a regex pattern.
    The Plugin method will be called for each message that mentions the bot and matches the
    specified regex pattern. The received [`Message`][machine.plugins.message.Message] will be passed
    to the method when called. Named groups can be used in the regex pattern, to catch specific
    parts of the message. These groups will be passed to the method as keyword arguments when
    called.

    Args:
        regex: regex pattern to listen for
        flags: regex flags to apply when matching
        handle_message_changed: if changed messages should trigger the decorated function

    Returns:
        wrapped method
    """

    def respond_to_decorator(f: Callable[P, R]) -> DecoratedPluginFunc[P, R]:
        fn = cast(DecoratedPluginFunc, f)
        fn.metadata = getattr(f, "metadata", Metadata())
        fn.metadata.plugin_actions.respond_to.append(MatcherConfig(re.compile(regex, flags), handle_message_changed))
        return fn

    return respond_to_decorator


def command(slash_command: str) -> Callable[[Callable[P, R]], DecoratedPluginFunc[P, R]]:
    """Respond to a slash command

    This decorator will enable a Plugin method to respond to slash commands

    Args:
        slash_command: the slash command to respond to

    Returns:
        wrapped method
    """

    def command_decorator(f: Callable[P, R]) -> DecoratedPluginFunc[P, R]:
        fn = cast(DecoratedPluginFunc, f)
        fn.metadata = getattr(f, "metadata", Metadata())
        normalized_slash_command = f"/{slash_command}" if not slash_command.startswith("/") else slash_command
        fn.metadata.plugin_actions.commands.append(
            CommandConfig(command=normalized_slash_command, is_generator=inspect.isasyncgenfunction(f))
        )
        return fn

    return command_decorator


def action(
    action_id: Union[re.Pattern[str], str, None] = None, block_id: Union[re.Pattern[str], str, None] = None
) -> Callable[[Callable[P, R]], DecoratedPluginFunc[P, R]]:
    """Respond to block actions

    This decorator will enable a Plugin method to be triggered when certain block actions are
    received. The Plugin method will be called when a block action event is received for which
    the `action_id` and `block_id` match the provided values. `action_id` and `block_id` can be strings,
    in which case the incoming action_id and block_id must match exactly, or regex patterns, in
    which case the incoming action_id and block_id must match the regex pattern.

    Both action_id and block_id are optional, but **at least one of them must be provided**.

    Args:
        action_id: the action_id to respond to, can be a string or regex pattern
        block_id: the block_id to respond to, can be a string or regex pattern

    Returns:
        wrapped method
    """

    def action_decorator(f: Callable[P, R]) -> DecoratedPluginFunc[P, R]:
        fn = cast(DecoratedPluginFunc, f)
        fn.metadata = getattr(f, "metadata", Metadata())
        if action_id is None and block_id is None:
            raise ValueError("At least one of action_id or block_id must be provided")
        fn.metadata.plugin_actions.actions.append(ActionConfig(action_id=action_id, block_id=block_id))
        return fn

    return action_decorator


def modal(callback_id: Union[re.Pattern[str], str]) -> Callable[[Callable[P, R]], DecoratedPluginFunc[P, R]]:
    """Respond to modal submissions

    This decorator will enable a Plugin method to be triggered when certain modals are submitted.
    The Plugin method will be called when a modal submission event is received for which the
    `callback_id` matches the provided value. The `callback_id` can be a string or a regex pattern.

    Args:
        callback_id: the callback id to respond to, can be a string or regex pattern

    Returns:
        wrapped method
    """

    def modal_decorator(f: Callable[P, R]) -> DecoratedPluginFunc[P, R]:
        fn = cast(DecoratedPluginFunc, f)
        fn.metadata = getattr(f, "metadata", Metadata())
        is_generator = inspect.isasyncgenfunction(f)
        fn.metadata.plugin_actions.modal_submissions.append(
            ModalConfig(callback_id=callback_id, is_generator=is_generator)
        )
        return fn

    return modal_decorator


def modal_closed(callback_id: Union[re.Pattern[str], str]) -> Callable[[Callable[P, R]], DecoratedPluginFunc[P, R]]:
    """Respond to modal closures

    This decorator will enable a Plugin method to be triggered when certain modals are closed.
    The Plugin method will be called when a modal closure event is received for which the
    `callback_id` matches the provided value. The `callback_id` can be a string or a regex pattern.

    Note:
        In order to receive modal close events, the modal must have the `notify_on_close` property set to `True`.

    Args:
        callback_id: the callback id to respond to, can be a string or regex pattern

    Returns:
        wrapped method
    """

    def modal_closed_decorator(f: Callable[P, R]) -> DecoratedPluginFunc[P, R]:
        fn = cast(DecoratedPluginFunc, f)
        fn.metadata = getattr(f, "metadata", Metadata())
        is_generator = inspect.isasyncgenfunction(f)
        if is_generator:
            raise ValueError("Modal closed handlers cannot be async generators")
        fn.metadata.plugin_actions.modal_closures.append(ModalConfig(callback_id=callback_id))
        return fn

    return modal_closed_decorator


def schedule(
    year: int | str | None = None,
    month: int | str | None = None,
    day: int | str | None = None,
    week: int | str | None = None,
    day_of_week: int | str | None = None,
    hour: int | str | None = None,
    minute: int | str | None = None,
    second: int | str | None = None,
    start_date: datetime | str | None = None,
    end_date: datetime | str | None = None,
    timezone: tzinfo | str | None = None,
) -> Callable[[Callable[P, R]], DecoratedPluginFunc[P, R]]:
    """Schedule a function to be executed according to a crontab-like schedule

    The decorated function will be executed according to the schedule provided. Slack Machine uses
    APScheduler under the hood for scheduling. For more information on the interpretation of the
    provided parameters, see [`CronTrigger`][apscheduler.triggers.cron.CronTrigger]

    Args:
        year: 4-digit year
        month: month (1-12)
        day: day of the (1-31)
        week: ISO week (1-53)
        day_of_week: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        hour: hour (0-23)
        minute: minute (0-59)
        second: second (0-59)
        start_date: earliest possible date/time to trigger on (inclusive)
        end_date: latest possible date/time to trigger on (inclusive)
        timezone: time zone to use for the date/time calculations (defaults to scheduler timezone)

    Returns:
        wrapped method
    """
    kwargs = locals()

    def schedule_decorator(f: Callable[P, R]) -> DecoratedPluginFunc[P, R]:
        fn = cast(DecoratedPluginFunc, f)
        fn.metadata = getattr(f, "metadata", Metadata())
        fn.metadata.plugin_actions.schedule = kwargs
        return fn

    return schedule_decorator


# TODO: this will actually receive the `self` of the emitting plugin, not the plugin where this decorator is used
def on(event: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Listen for an event

    The decorated function will be called whenever a plugin (or Slack Machine itself) emits an
    event with the given name.

    Args:
        event: name of the event to listen for. Event names are global

    Returns:
        wrapped method
    """

    def on_decorator(f: Callable[P, R]) -> Callable[P, R]:
        ee.add_listener(event, f)
        return f

    return on_decorator


def required_settings(settings: list[str] | str) -> Callable[[Callable[P, R]], DecoratedPluginFunc[P, R]]:
    """Specify a required setting for a plugin or plugin method

    The settings specified with this decorator will be added to the required settings for the
    plugin. If one or more settings have not been defined by the user, the plugin will not be
    loaded and a warning will be written to the console upon startup.

    Args:
        settings: settings that are required (can be list of strings, or single string)

    Returns:
        wrapped method
    """

    def required_settings_decorator(f_or_cls: Callable[P, R]) -> DecoratedPluginFunc[P, R]:
        casted_f_or_cls = cast(DecoratedPluginFunc, f_or_cls)
        casted_f_or_cls.metadata = getattr(f_or_cls, "metadata", Metadata())
        if isinstance(settings, list):
            casted_f_or_cls.metadata.required_settings.extend(settings)
        elif isinstance(settings, str):
            casted_f_or_cls.metadata.required_settings.append(settings)
        return casted_f_or_cls

    return required_settings_decorator


# TODO: write tests for this decorator
def require_any_role(
    required_roles: list[str],
) -> Callable[[Callable[..., Awaitable[None]]], Callable[..., Awaitable[None]]]:
    """Specify required roles for a plugin method

    To use the plugin method where this decorator is applied, the user must have
    at least one of the listed roles.

    Args:
        required_roles: list of roles required to use the plugin method

    Returns:
        wrapped method
    """

    def middle(func: Callable[..., Awaitable[None]]) -> Callable[..., Awaitable[None]]:
        async def wrapper(self: MachineBasePlugin, msg: Message, **kwargs: Any) -> None:
            if await matching_roles_by_user_id(self, msg.sender.id, required_roles):
                logger.debug(f"User {msg.sender} has one of the required roles {required_roles}")
                return await func(self, msg, **kwargs)
            else:
                logger.debug(f"User {msg.sender} does not have any of the required roles {required_roles}")
                ee.emit(
                    "unauthorized-access",
                    self,
                    message=msg,
                    required_roles=required_roles,
                    combinator=RoleCombinator.ANY,
                )
                await msg.say("I'm sorry, but you don't have access to that command", ephemeral=True)
                return None

        # Copy any existing docs and metadata from container function to
        # generated function
        wrapper.__doc__ = func.__doc__
        casted_wrapper = cast(DecoratedPluginFunc, wrapper)
        casted_wrapper.metadata = getattr(func, "metadata", Metadata())
        return casted_wrapper

    return middle


# TODO: write tests for this decorator
def require_all_roles(
    required_roles: list[str],
) -> Callable[[Callable[..., Awaitable[None]]], Callable[..., Awaitable[None]]]:
    """Specify required roles for a plugin method

    To use the plugin method where this decorator is applied, the user must have
    all of the listed roles.

    Args:
        required_roles: list of roles required to use the plugin method

    Returns:
        wrapped method
    """

    def middle(func: Callable[..., Awaitable[None]]) -> Callable[..., Awaitable[None]]:
        async def wrapper(self: MachineBasePlugin, msg: Message, **kwargs: Any) -> None:
            if await matching_roles_by_user_id(self, msg.sender.id, required_roles) == len(required_roles):
                logger.debug(f"User {msg.sender} has all of the required roles {required_roles}")
                return await func(self, msg, **kwargs)
            else:
                logger.debug(f"User {msg.sender} does not have all of the required roles {required_roles}")
                ee.emit(
                    "unauthorized-access",
                    self,
                    message=msg,
                    required_roles=required_roles,
                    combinator=RoleCombinator.ALL,
                )
                await msg.say("I'm sorry, but you don't have access to that command", ephemeral=True)
                return None

        # Copy any existing docs and metadata from container function to
        # generated function
        wrapper.__doc__ = func.__doc__
        casted_wrapper = cast(DecoratedPluginFunc, wrapper)
        casted_wrapper.metadata = getattr(func, "metadata", Metadata())
        return casted_wrapper

    return middle
