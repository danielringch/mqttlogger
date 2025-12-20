import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Dict

from .config import get_config_key, get_optional_config_key
from .helpers import log_formatter, ModuleFilter

_CONFIG_KEY_FILE = 'file'
_CONFIG_KEY_LEVEL = 'level'
_CONFIG_KEY_PATH = 'path'
_CONFIG_KEY_DAYS = 'days'

def create_file_logger(config: Dict):
    if _CONFIG_KEY_FILE not in config:
        return
    
    level = get_optional_config_key(config, lambda x: getattr(logging, str(x).upper()), 'debug', None, _CONFIG_KEY_FILE, _CONFIG_KEY_LEVEL)
    path = get_config_key(config, str, None, _CONFIG_KEY_FILE, _CONFIG_KEY_PATH)
    days = get_optional_config_key(config, int, 0, None, _CONFIG_KEY_FILE, _CONFIG_KEY_DAYS)
    
    logger = logging.getLogger()

    handler = TimedRotatingFileHandler(path, when="midnight", interval=1, backupCount=days)
    handler.setLevel(level)
    handler.setFormatter(log_formatter)
    handler.addFilter(ModuleFilter())
    logger.addHandler(handler)
