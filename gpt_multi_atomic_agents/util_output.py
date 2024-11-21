from . import config

def print_debug(message):
    if config.IS_DEBUG:
        print(message)
