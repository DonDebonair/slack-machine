from functools import wraps
import re


def process(event_type):
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
