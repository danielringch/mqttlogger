import logging, sys
from typing import Dict

from .config import get_optional_config_key
from .helpers import log_formatter, ModuleFilter

_CONFIG_KEY_STDOUT = 'stdout'
_CONFIG_KEY_LEVEL = 'level'

def create_std_logger(config: Dict):
    if _CONFIG_KEY_STDOUT not in config:
        return

    level = get_optional_config_key(config, lambda x: getattr(logging, str(x).upper()), 'debug', None, _CONFIG_KEY_STDOUT, _CONFIG_KEY_LEVEL)

    logger = logging.getLogger()
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(log_formatter)
    handler.addFilter(ModuleFilter())
    logger.addHandler(handler)

