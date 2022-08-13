from importlib import import_module
import inspect
from typing import List, Tuple, Type


def import_string(dotted_path: str) -> List[Tuple[str, Type]]:
    """
    Import all Classes from the module specified by
    the dotted_path. If dotted_path is not a module, try
    importing it as a member of a module instead

    returns: list of classes or list of single class
    """

    try:
        module = import_module(dotted_path)
        return [(f"{dotted_path}:{name}", cls) for name, cls in inspect.getmembers(module, predicate=inspect.isclass)]
    except ImportError:
        try:
            module_path, class_name = dotted_path.rsplit(".", 1)
            module = import_module(module_path)
            return [(f"{module_path}:{class_name}", getattr(module, class_name))]
        except (ImportError, AttributeError):
            msg = f"{dotted_path} doesn't look like a module or class"
            raise ImportError(msg)
