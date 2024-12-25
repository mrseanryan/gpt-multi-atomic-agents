from rich.console import Console

from . import config

console = Console()


def print_debug(message: str, config: config.Config) -> None:
    if config.is_debug:
        print(message)


def print_warning(message: str) -> None:
    console.log(f":warning: {message}", style="yellow")
