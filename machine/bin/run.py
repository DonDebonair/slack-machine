# -*- coding: utf-8 -*-

import asyncio
import sys
import os

from machine import core


def main():
    # When running this function as console entry point, the current working dir is not in the
    # Python path, so we have to add it
    sys.path.insert(0, os.getcwd())

    loop = asyncio.new_event_loop()
    core.start(loop)

    sys.exit(0)
