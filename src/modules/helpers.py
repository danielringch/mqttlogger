import logging

DISCORD_LOGGING_NAME = 'discord'

ALLOWED_LOGGING_NAMES = {'root', DISCORD_LOGGING_NAME}

class ModuleFilter(logging.Filter):
    def filter(self, record):
        return record.name in ALLOWED_LOGGING_NAMES

log_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
