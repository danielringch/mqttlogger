import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Dict

from .config import get_config_key, get_optional_config_key
from .helpers import log_formatter, ModuleFilter

_FILE_CONFIG_KEY = 'file'
_LEVEL_CONFIG_KEY = 'level'
_PATH_CONFIG_KEY = 'path'
_DAYS_CONFIG_KEY = 'days'

def create_file_logger(config: Dict):
    if _FILE_CONFIG_KEY not in config:
        return
    
    level = get_optional_config_key(config, lambda x: getattr(logging, str(x).upper()), 'debug', None, _FILE_CONFIG_KEY, _LEVEL_CONFIG_KEY)
    path = get_config_key(config, str, None, _FILE_CONFIG_KEY, _PATH_CONFIG_KEY)
    days = get_optional_config_key(config, int, 0, None, _FILE_CONFIG_KEY, _DAYS_CONFIG_KEY)
    
    logger = logging.getLogger()

    handler = TimedRotatingFileHandler(path, when="midnight", interval=1, backupCount=days)
    handler.setLevel(level)
    handler.setFormatter(log_formatter)
    handler.addFilter(ModuleFilter())
    logger.addHandler(handler)
