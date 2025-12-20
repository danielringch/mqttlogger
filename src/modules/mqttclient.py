import struct, logging
import paho.mqtt.client as mqtt
from functools import partial
from ssl import CERT_NONE
from typing import Dict

from .config import get_config_key, get_optional_config_key

_MQTT_CONFIG_KEY = 'mqtt'
_HOST_CONFIG_KEY = 'host'
_CA_CONFIG_KEY = 'ca'
_TLS_INSECURE_CONFIG_KEY = 'tls_insecure'
_USER_CONFIG_KEY = 'user'
_PASSWORD_CONFIG_KEY = 'password'

_TOPICS_CONFIG_KEY = 'topics'
_LEVEL_CONFIG_KEY = 'level'
_TYPE_CONFIG_KEY = 'type'

_HOST_ENV_NAME = 'MQLO_MQTT_HOST'
_USER_ENV_NAME = 'MQLO_MQTT_USER'
_PASS_ENV_NAME = 'MQLO_MQTT_PASS'

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
        self.__mqtt = mqtt.Client()
        self.__mqtt.on_connect = self.__on_connect

        ip, port = get_config_key(config, lambda x: str(x).split(':'), _HOST_ENV_NAME, _MQTT_CONFIG_KEY, _HOST_CONFIG_KEY)

        ca_path = get_optional_config_key(config, str, None, None, _MQTT_CONFIG_KEY, _CA_CONFIG_KEY)
        is_tls_insecure = get_optional_config_key(config, bool, False, None, _MQTT_CONFIG_KEY, _TLS_INSECURE_CONFIG_KEY)
        if ca_path or is_tls_insecure:
            self.__mqtt.tls_set(ca_certs=ca_path, cert_reqs=CERT_NONE if is_tls_insecure else None)

        user = get_optional_config_key(config, str, None, _USER_ENV_NAME, _MQTT_CONFIG_KEY, _USER_CONFIG_KEY)
        password = get_optional_config_key(config, str, None, _PASS_ENV_NAME, _MQTT_CONFIG_KEY, _PASSWORD_CONFIG_KEY)
        if user or password:
            self.__mqtt.username_pw_set(user, password)

        try:
            self.__topics: set[str] = set(config[_TOPICS_CONFIG_KEY].keys())
        except:
            raise ValueError('No topics or invalid list of topics given in config.')
        for topic_name in self.__topics:
            level = get_config_key(config, lambda x: getattr(logging, str(x).upper()), None, _TOPICS_CONFIG_KEY, topic_name, _LEVEL_CONFIG_KEY)
            format = get_config_key(config, lambda x: _DECODERS[str(x)], None, _TOPICS_CONFIG_KEY, topic_name, _TYPE_CONFIG_KEY)
            self.__mqtt.message_callback_add(topic_name, partial(self.__process_message, level, format))

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
