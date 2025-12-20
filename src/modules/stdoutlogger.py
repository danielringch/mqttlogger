import logging, sys
from typing import Dict

from .config import get_optional_config_key
from .helpers import log_formatter, ModuleFilter

_STDOUT_CONFIG_KEY = 'stdout'
_LEVEL_CONFIG_KEY = 'level'

def create_std_logger(config: Dict):
    if _STDOUT_CONFIG_KEY not in config:
        return

    level = get_optional_config_key(config, lambda x: getattr(logging, str(x).upper()), 'debug', None, _STDOUT_CONFIG_KEY, _LEVEL_CONFIG_KEY)

    logger = logging.getLogger()
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(log_formatter)
    handler.addFilter(ModuleFilter())
    logger.addHandler(handler)

