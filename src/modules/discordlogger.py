import logging, discord, asyncio
from discord.ext import tasks
from queue import Queue
from typing import Dict

from .config import get_config_key, get_optional_config_key
from .helpers import log_formatter, ModuleFilter, DISCORD_LOGGING_NAME

_DISCORD_CONFIG_KEY = 'discord'
_TOKEN_CONFIG_KEY = 'token'
_TOKEN_PATH_CONFIG_KEY = 'token_path'
_LEVEL_CONFIG_KEY = 'level'
_CHANNEL_ID_CONFIG_KEY = 'channel_id'

_TOKEN_ENV_NAME = 'MQLO_DISCORD_TOKEN'
_TOKEN_PATH_ENV_NAME = 'MQLO_DISCORD_TOKEN_PATH'
_CHANNEL_ID_ENV_NAME = 'MQLO_DISCORD_CHANNEL_ID'

_MAX_MESSAGE_LENGTH = 2000

discord_logging = logging.getLogger(DISCORD_LOGGING_NAME)

def create_discord_logger(config: Dict):
    if _DISCORD_CONFIG_KEY not in config:
        return
    
    if (token_path := get_optional_config_key(config, str, None, _TOKEN_PATH_ENV_NAME, _DISCORD_CONFIG_KEY, _TOKEN_PATH_CONFIG_KEY)):
        try:
            with open(token_path, "r") as stream:
                token = stream.readline()
        except:
            raise FileNotFoundError(f'Can not open token file {token_path}')
    elif (token := get_optional_config_key(config, str, None, _TOKEN_ENV_NAME, _DISCORD_CONFIG_KEY, _TOKEN_CONFIG_KEY)):
        pass
    else:
        raise KeyError('No discord token or token path was given in the configuration')
    
    level = get_optional_config_key(config, lambda x: getattr(logging, str(x).upper()), 'warning', None, _DISCORD_CONFIG_KEY, _LEVEL_CONFIG_KEY)
    channel_id = get_config_key(config, int, _CHANNEL_ID_ENV_NAME, _DISCORD_CONFIG_KEY, _CHANNEL_ID_CONFIG_KEY)

    logger = logging.getLogger()

    handler = DiscordHandler(token, channel_id)
    handler.setLevel(level)
    handler.setFormatter(log_formatter)
    handler.addFilter(ModuleFilter())
    logger.addHandler(handler)


class DiscordHandler(logging.Handler):
    def __init__(self, token: str, channel_id: int):
        self.__bot = DiscordBot(token, channel_id)
        logging.Handler.__init__(self=self)

    def emit(self, record: logging.LogRecord):
        self.__bot.send_log_record(record)

class DiscordBot(discord.Client):
    def __init__(self, token: str, channel_id: int):
        self.__channel_id = channel_id
        self.__buffer = Queue(maxsize=100)

        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        asyncio.create_task(self.start(token))

    async def setup_hook(self):
        self.flusher.start()

    async def close(self):
        self.flusher.cancel()
        await super().close()

    @tasks.loop(seconds=2)
    async def flusher(self):
        if self.__buffer.empty():
            return
        if (channel := self.get_channel(self.__channel_id)) is None:
            discord_logging.critical(f'Discord channel is not available: {self.__channel_id}.')
            return
        while not self.__buffer.empty():
            try:
                await channel.send(self.__buffer.get(block=False))
            except Exception as e:
                discord_logging.critical(f'Failed sending a message: {e}.')

    @flusher.before_loop
    async def before_flusher(self):
        await self.wait_until_ready()
        discord_logging.debug('Discord logging handler ready.')

    def send_log_record(self, record: logging.LogRecord):
        if record.name == DISCORD_LOGGING_NAME:
            return
        message = record.getMessage()
        for sub_message in (message[i:i + _MAX_MESSAGE_LENGTH] for i in range(0,len(message), _MAX_MESSAGE_LENGTH)):
            try:
                self.__buffer.put(item=sub_message, block=False)
            except:
                discord_logging.critical(f'Failed sending a message: send queue overflow.')
