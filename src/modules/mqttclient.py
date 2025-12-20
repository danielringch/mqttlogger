import struct, logging
import paho.mqtt.client as mqtt
from functools import partial
from ssl import CERT_NONE
from typing import Dict, Set

from .config import get_config_key, get_optional_config_key

_CONFIG_KEY_MQTT = 'mqtt'
_CONFIG_KEY_HOST = 'host'
_CONFIG_KEY_CA = 'ca'
_CONFIG_KEY_TLS_INSECURE = 'tls_insecure'
_CONFIG_KEY_USER = 'user'
_CONFIG_KEY_PASSWORD = 'password'

_CONFIG_KEY_TOPICS = 'topics'
_CONFIG_KEY_LEVEL = 'level'
_CONFIG_KEY_TYPE = 'type'

_DECODERS = {
    'bool': '!?',
    'uint8': '!B',
    'int8': '!b',
    'uint16': '!H',
    'int16': '!h',
    'uint32': '!I',
    'int32': '!i',
    'uint64': '!Q',
    'int64': '!q',
    'float': '!f',
    'double': '!d',
    'utf8': '!utf8'}

class MqttClient():
    def __init__(self, config: Dict):
        ip, port = get_config_key(config, lambda x: str(x).split(':'), None, _CONFIG_KEY_MQTT, _CONFIG_KEY_HOST)
        ca_path = get_optional_config_key(config, str, None, None, _CONFIG_KEY_MQTT, _CONFIG_KEY_CA)
        is_tls_insecure = get_optional_config_key(config, bool, False, None, _CONFIG_KEY_MQTT, _CONFIG_KEY_TLS_INSECURE)
        user = get_optional_config_key(config, str, None, None, _CONFIG_KEY_MQTT, _CONFIG_KEY_USER)
        password = get_optional_config_key(config, str, None, None, _CONFIG_KEY_MQTT, _CONFIG_KEY_PASSWORD)

        if _CONFIG_KEY_TOPICS not in config:
            raise KeyError('No topics given in config')

        self.__mqtt = mqtt.Client()
        self.__topics: Set[str] = set()

        try:
            topics_names = config[_CONFIG_KEY_TOPICS].keys()
        except:
            raise ValueError('Invalid list of topics')
        for topic_name in topics_names:
            level = get_config_key(config, lambda x: getattr(logging, str(x).upper()), None, _CONFIG_KEY_TOPICS, topic_name, _CONFIG_KEY_LEVEL)
            format = get_config_key(config, lambda x: _DECODERS[str(x)], None, _CONFIG_KEY_TOPICS, topic_name, _CONFIG_KEY_TYPE)
            self.__mqtt.message_callback_add(topic_name, partial(self.__process_message, level, format))
            self.__topics.add(topic_name)

        self.__mqtt.on_connect = self.__on_connect

        if ca_path or is_tls_insecure:
            self.__mqtt.tls_set(ca_certs=ca_path, cert_reqs=CERT_NONE if is_tls_insecure else None)

        if user or password:
            self.__mqtt.username_pw_set(user, password)

        self.__mqtt.connect(ip, int(port), 60)
        self.__mqtt.loop_start()

    def __on_connect(self, client, userdata, flags, rc):
        logging.debug(f'MQTT connected with code {rc}.')
        for topic in self.__topics:
            self.__mqtt.subscribe(topic, qos=1)

    def __process_message(self, level, format: str, client, userdata, msg):
        try:
            topic: str = msg.topic
            message: bytes = msg.payload
            if message is None or len(message) == 0:
                data = ''
            else:
                data = message.decode('utf-8') if format == '!utf8' else struct.unpack(format, message)[0]

            logging.log(level, f'MQTT @ {topic}: {data}')
        except Exception as e:
            logging.error(f'Unable to parse MQTT message on topic {topic}: {e}')
