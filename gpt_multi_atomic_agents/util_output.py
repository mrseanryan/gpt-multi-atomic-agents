from rich.console import Console

from . import config

console = Console()


def print_debug(message, config: config.Config):
    if config.is_debug:
        print(message)


def print_warning(message):
    console.log(f":warning: {message}")
