from functools import wraps
import re


def process(event_type):
    """Decorator for processing Slack events of a specific type

    This decorator will enable a Plugin method to process `Slack events`_ of a specific type. The
    Plugin method will be called for each event of the specified type that the bot receives.
    The received event will be passed to the method when called.

    .. _Slack events: https://api.slack.com/events

    :param event_type: type of event the method needs to process. Can be any event supported by the
        RTM API
    :return: wrapped method
    """
    def process_decorator(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            return f(*args, **kwargs)

        wrapped_f.metadata = getattr(f, "metadata", {})
        wrapped_f.metadata['plugin_actions'] = wrapped_f.metadata.get('plugin_actions', {})
        wrapped_f.metadata['plugin_actions']['process'] = {}
        wrapped_f.metadata['plugin_actions']['process']['event_type'] = event_type
        return wrapped_f

    return process_decorator


def listen_to(regex, flags=re.IGNORECASE):
    """Decorator for listening to messages matching a regex pattern

    This decorator will enable a Plugin method to listen to messages that match a regex pattern.
    The Plugin method will be called for each message that matches the specified regex pattern.
    The received :py:class:`~machine.plugins.base.Message` will be passed to the method when called.
    Named groups can be used in the regex pattern, to catch specific parts of the message. These
    groups will be passed to the method as keyword arguments when called.

    :param regex: regex pattern to listen for
    :param flags: regex flags to apply when matching
    :return: wrapped method
    """
    def listen_to_decorator(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            return f(*args, **kwargs)

        wrapped_f.metadata = getattr(f, "metadata", {})
        wrapped_f.metadata['plugin_actions'] = wrapped_f.metadata.get('plugin_actions', {})
        wrapped_f.metadata['plugin_actions']['listen_to'] = {}
        wrapped_f.metadata['plugin_actions']['listen_to']['regex'] = re.compile(regex, flags)
        return wrapped_f

    return listen_to_decorator


def respond_to(regex, flags=re.IGNORECASE):
    """Decorator for listening to messages mentioning the bot and matching a regex pattern

    This decorator will enable a Plugin method to listen to messages that are directed to the bot
    (ie. message starts by mentioning the bot) and match a regex pattern.
    The Plugin method will be called for each message that mentions the bot and matches the
    specified regex pattern. The received :py:class:`~machine.plugins.base.Message` will be passed
    to the method when called. Named groups can be used in the regex pattern, to catch specific
    parts of the message. These groups will be passed to the method as keyword arguments when
    called.

    :param regex: regex pattern to listen for
    :param flags: regex flags to apply when matching
    :return: wrapped method
    """
    def respond_to_decorator(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            return f(*args, **kwargs)

        wrapped_f.metadata = getattr(f, "metadata", {})
        wrapped_f.metadata['plugin_actions'] = wrapped_f.metadata.get('plugin_actions', {})
        wrapped_f.metadata['plugin_actions']['respond_to'] = {}
        wrapped_f.metadata['plugin_actions']['respond_to']['regex'] = re.compile(regex, flags)
        return wrapped_f

    return respond_to_decorator
