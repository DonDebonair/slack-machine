from typing import Any, Mapping
from urllib.parse import urlparse


def gen_config_dict(settings: Mapping[str, Any]) -> Mapping[str, Any]:
    url = urlparse(settings["REDIS_URL"])
    db = url.path[1:] if hasattr(url, "path") and url.path else 0
    max_connections = settings.get("REDIS_MAX_CONNECTIONS", None)
    return {
        "host": url.hostname,
        "port": url.port,
        "db": db,
        "password": url.password,
        "max_connections": max_connections,
    }
