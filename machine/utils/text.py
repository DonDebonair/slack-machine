from clint.textui import puts, colored


def show_valid(valid_str: str) -> None:
    puts(colored.green(f"✓ {valid_str}"))


def show_invalid(invalid_str: str) -> None:
    puts(colored.red(f"✗ {invalid_str}"))


def warn(warn_string: str) -> None:
    puts(colored.yellow(f"Warning: {warn_string}"))


def error(err_string: str) -> None:
    puts(colored.red(f"ERROR: {err_string}"))


def announce(string: str) -> None:
    puts(colored.cyan(string))
