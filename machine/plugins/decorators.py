import re

from blinker import signal


def process(slack_event_type):
    """Process Slack events of a specific type

    This decorator will enable a Plugin method to process `Slack events`_ of a specific type. The
    Plugin method will be called for each event of the specified type that the bot receives.
    The received event will be passed to the method when called.

    .. _Slack events: https://api.slack.com/events

    :param slack_event_type: type of event the method needs to process. Can be any event supported
        by the RTM API
    :return: wrapped method
    """

    def process_decorator(f):
        f.metadata = getattr(f, "metadata", {})
        f.metadata['plugin_actions'] = f.metadata.get('plugin_actions', {})
        f.metadata['plugin_actions']['process'] = \
            f.metadata['plugin_actions'].get('process', {})
        f.metadata['plugin_actions']['process']['event_type'] = slack_event_type
        return f

    return process_decorator


def listen_to(regex, flags=re.IGNORECASE):
    """Listen to messages matching a regex pattern

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
        f.metadata = getattr(f, "metadata", {})
        f.metadata['plugin_actions'] = f.metadata.get('plugin_actions', {})
        f.metadata['plugin_actions']['listen_to'] = \
            f.metadata['plugin_actions'].get('listen_to', {})
        f.metadata['plugin_actions']['listen_to']['regex'] = \
            f.metadata['plugin_actions']['listen_to'].get('regex', [])
        f.metadata['plugin_actions']['listen_to']['regex'].append(re.compile(regex, flags))
        return f

    return listen_to_decorator


def respond_to(regex, flags=re.IGNORECASE):
    """Listen to messages mentioning the bot and matching a regex pattern

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
        f.metadata = getattr(f, "metadata", {})
        f.metadata['plugin_actions'] = f.metadata.get('plugin_actions', {})
        f.metadata['plugin_actions']['respond_to'] = \
            f.metadata['plugin_actions'].get('respond_to', {})
        f.metadata['plugin_actions']['respond_to']['regex'] = \
            f.metadata['plugin_actions']['respond_to'].get('regex', [])
        f.metadata['plugin_actions']['respond_to']['regex'].append(re.compile(regex, flags))
        return f

    return respond_to_decorator


def schedule(year=None, month=None, day=None, week=None, day_of_week=None, hour=None, minute=None,
             second=None, start_date=None, end_date=None, timezone=None):
    """Schedule a function to be executed according to a crontab-like schedule

    The decorated function will be executed according to the schedule provided. Slack Machine uses
    APScheduler under the hood for scheduling. For more information on the interpretation of the
    provided parameters, see :class:`CronTrigger<apscheduler:apscheduler.triggers.cron.CronTrigger>`

    :param int|str year: 4-digit year
    :param int|str month: month (1-12)
    :param int|str day: day of the (1-31)
    :param int|str week: ISO week (1-53)
    :param int|str day_of_week: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    :param int|str hour: hour (0-23)
    :param int|str minute: minute (0-59)
    :param int|str second: second (0-59)
    :param datetime|str start_date: earliest possible date/time to trigger on (inclusive)
    :param datetime|str end_date: latest possible date/time to trigger on (inclusive)
    :param datetime.tzinfo|str timezone: time zone to use for the date/time calculations (defaults
        to scheduler timezone)
    """
    kwargs = locals()

    def schedule_decorator(f):
        f.metadata = getattr(f, "metadata", {})
        f.metadata['plugin_actions'] = f.metadata.get('plugin_actions', {})
        f.metadata['plugin_actions']['schedule'] = kwargs
        return f

    return schedule_decorator


def on(event):
    """Listen for an event

    The decorated function will be called whenever a plugin (or Slack Machine itself) emits an
    event with the given name.

    :param event: name of the event to listen for. Event names are global
    """

    def on_decorator(f):
        e = signal(event)
        e.connect(f)
        return f

    return on_decorator


def required_settings(settings):
    """Specify a required setting for a plugin or plugin method

    The settings specified with this decorator will be added to the required settings for the
    plugin. If one or more settings have not been defined by the user, the plugin will not be
    loaded and a warning will be written to the console upon startup.

    :param settings: settings that are required (can be list of strings, or single string)
    """

    def required_settings_decorator(f_or_cls):
        f_or_cls.metadata = getattr(f_or_cls, "metadata", {})
        f_or_cls.metadata['required_settings'] = f_or_cls.metadata.get('required_settings', [])
        if (isinstance(settings, list)):
            f_or_cls.metadata['required_settings'].extend(settings)
        elif (isinstance(settings, str)):
            f_or_cls.metadata['required_settings'].append(settings)
        return f_or_cls

    return required_settings_decorator


def route(path, **kwargs):
    """Define a http route that should trigger the function

    The parameters to this decorator will be passed to the ``route`` function of Bottle

    :param path: path to match
    :param kwargs: additional keyword arguments to be passed to Bottle
    """

    def route_decorator(f):
        f.metadata = getattr(f, "metadata", {})
        f.metadata['plugin_actions'] = f.metadata.get('plugin_actions', {})
        f.metadata['plugin_actions']['route'] = \
            f.metadata['plugin_actions'].get('route', [])
        kwargs['path'] = path
        f.metadata['plugin_actions']['route'].append(kwargs)
        return f

    return route_decorator
