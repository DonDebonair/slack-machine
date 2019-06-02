from clint.textui import puts, colored


def show_valid(valid_str):
    puts(colored.green(f"✓ {valid_str}"))


def show_invalid(valid_str):
    puts(colored.red(f"✗ {valid_str}"))


def warn(warn_string):
    puts(colored.yellow(f"Warning: {warn_string}"))


def error(err_string):
    puts(colored.red(f"ERROR: {err_string}"))


def announce(string):
    puts(colored.cyan(string))
