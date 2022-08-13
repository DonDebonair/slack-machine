from urllib.parse import urlparse


def gen_config_dict(settings):
    url = urlparse(settings["REDIS_URL"])
    if hasattr(url, "path") and getattr(url, "path"):
        db = url.path[1:]
    else:
        db = 0
    max_connections = settings.get("REDIS_MAX_CONNECTIONS", None)
    return {
        "host": url.hostname,
        "port": url.port,
        "db": db,
        "password": url.password,
        "max_connections": max_connections,
    }
