import sys
import os

from machine import Machine


def main():
    # When running this function as console entry point, the current working dir is not in the
    # Python path, so we have to add it
    sys.path.insert(0, os.getcwd())
    bot = Machine()
    try:
        bot.run()
    except (KeyboardInterrupt, SystemExit):
        print("Thanks for playing!")
        sys.exit(0)
