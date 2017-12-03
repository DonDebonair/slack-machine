from clint.textui import puts, colored


def show_valid(valid_str):
    puts(colored.green(u"✓ %s" % valid_str))


def show_invalid(valid_str):
    puts(colored.red(u"✗ %s" % valid_str))


def warn(warn_string):
    puts(colored.yellow("Warning: %s" % warn_string))


def error(err_string):
    puts(colored.red("ERROR: %s" % err_string))


def announce(string):
    puts(colored.cyan(string))
