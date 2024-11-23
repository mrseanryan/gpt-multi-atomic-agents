from . import config


def print_debug(message, config: config.Config):
    if config.is_debug:
        print(message)
