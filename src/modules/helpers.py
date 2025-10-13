import logging
from typing import Dict, Any, Callable

DISCORD_LOGGING_NAME = 'discord'

ALLOWED_LOGGING_NAMES = {'root', DISCORD_LOGGING_NAME}

class ModuleFilter(logging.Filter):
    def filter(self, record):
        return record.name in ALLOWED_LOGGING_NAMES

def get_config_key(config: Dict, converter: Callable[[Any], Any], *keys: str):
    raw = config
    try:
        for key in keys:
            raw: Dict = raw[key]
    except:
        raise KeyError(f'Key {"/".join(keys)} is missing in configuration')
    try:
        return converter(raw) if converter else raw
    except:
        raise ValueError(f'Unknown value for key {"/".join(keys)}: {raw}')

def get_optional_config_key(config: Dict, converter: Callable[[Any], Any], default: Any, *keys: str):
    raw = config
    try:
        for key in keys:
            raw = raw.get(key)
            if raw is None:
                return default
    except:
        raise KeyError(f'Key {"/".join(keys)} is unreachable')
    try:
        return converter(raw) if converter else raw
    except:
        raise ValueError(f'Unknown value for key {"/".join(keys)}: {raw}')

log_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

