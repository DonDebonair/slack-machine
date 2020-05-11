# -*- coding: utf-8 -*-
from typing import List, Union


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def find_shortest_indent(
    text: Union[str, List[str]], ignore_empty: bool = True, delimiter: str = "\n"
) -> int:
    """ Given a block of text, find the shortest indent in use.
        If there is a line with an indent of 0, skips the loop and returns 0.
        If `ignore_empty` is set, lines that are empty are skipped.
        If a shortest indent can't be determined, returns 0.
    """

    if isinstance(text, str):
        text = text.split(delimiter)

    indent_sizes = []

    for line in text:
        if ignore_empty and line.strip() == "":
            continue

        count = 0
        for char in line:
            if char.isspace():
                count += 1
            else:
                break

        if count == 0:
            return 0

        indent_sizes.append(count)

    if not indent_sizes:
        return 0

    return min(indent_sizes)
