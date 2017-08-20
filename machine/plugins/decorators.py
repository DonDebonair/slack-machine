from functools import wraps


def process(event_type):
    def process_decorator(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            return f(*args, **kwargs)
        wrapped_f.metadata = getattr(f, "metadata", {})
        wrapped_f.metadata['plugin_action_type'] = 'process'
        wrapped_f.metadata['plugin_action_config'] = {}
        wrapped_f.metadata['plugin_action_config']['event_type'] = event_type
        return wrapped_f
    return process_decorator
