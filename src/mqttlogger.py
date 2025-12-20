import argparse, asyncio, logging, yaml
from typing import Dict

from modules.stdoutlogger import create_std_logger
from modules.filelogger import create_file_logger
from modules.discordlogger import create_discord_logger
from modules.mqttclient import MqttClient

__version__ = "1.1.0"

async def main():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('-c', '--config', type=str, required=True, help="Path to config file.")
    args = parser.parse_args()

    try:
        with open(args.config, "r") as stream:
            config: Dict = yaml.safe_load(stream)
    except Exception as e:
        logging.critical(f'Failed to load config file {args.config}: {e}')
        exit()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    create_std_logger(config)
    create_file_logger(config)
    create_discord_logger(config)

    logging.debug(f'mqttlogger {__version__}')

    mqtt_client = MqttClient(config)

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
