# mqttlogger

Logs MQTT messages to STDOUT, file or a Discord channel.

## Introduction

This repository is part of the [homebattery project](https://github.com/danielringch/homebattery). Its primary goal is to enable push notifications in Discord when a message is published to an error relevant MQTT topic. Of course, usage as an MQTT data logger or debugging tool is also perfectly possible.

The working principle is simple: all MQTT messages received on the configured MQTT topics are written to the logs (with their timestamp and topic).

Things worth to notice:

- MQTT topic wildcards are supported.
- The log files written by this tool are rotated at midnight.
- The log levels DEBUG and CRITICAL are reserved for the output of the tool itself and can not be used for MQTT.

## Discord setup steps

Please read the tutorial from [discord.py](https://discordpy.readthedocs.io/en/stable/discord.html).

## Prerequisites

- Python version 3.12 or newer with pip + venv

This program should run on any OS, but I have no capacity to test this, so feedback is appreciated. My test machines run Ubuntu and Raspbian.

## Install

```
git clone https://github.com/danielringch/mqttlogger.git
python3 -m venv <path to virtual environment>
source <path to virtual environment>/bin/activate
python3 -m pip install -r requirements.txt
```

## Configuration

The configuration is done via yaml file. The example file can be found in [config/sample.yaml](config/sample.yaml)

| Key | Rules | Explanation |
| -- | -- | -- |
| ``mqtt`` -> ``host`` | string, ``<host>:<port>`` | Host and port of the MQTT server to connect to. |
| ``mqtt`` -> ``ca`` | optional, string | Enables TLS encryption and sets the path to the TLS public certificate chain file. |
| ``mqtt`` -> ``tls_insecure`` | optional, bool | If set to true, TLS encryption is enabled, but the TLS certificates are not checked (not recommended). |
| ``mqtt`` -> ``user`` | string | The user name for log in to the MQTT server. |
| ``mqtt`` -> ``password`` | string | The password for log in to the MQTT server. |
| ``stdout`` | optional | Enables logging to STDOUT. |
| ``stdout`` -> ``level`` | string; ``DEBUG``, ``INFO``, ``WARN``, ``ERROR`` or ``CRITICAL`` | Minimum level a log message must have to be written to this output. |
| ``file`` | optional | Enables logging to file. |
| ``file`` -> ``level`` | string; ``DEBUG``, ``INFO``, ``WARN``, ``ERROR`` or ``CRITICAL`` | Minimum level a log message must have to be written to this output. |
| ``file`` -> ``path`` | string | Path to the written log file. |
| ``file`` -> ``days`` | optional, int | If set, log files are deleted after the given number of days. |
| ``discord`` | optional | Enables logging to Discord. |
| ``discord`` -> ``level`` | string; ``DEBUG``, ``INFO``, ``WARN``, ``ERROR`` or ``CRITICAL`` | Minimum level a log message must have to be written to this output. |
| ``discord`` -> ``token_path`` | string | Path to the Discord bot token file. |
| ``discord`` -> ``channel_id`` | int | Id of the Discord channel to write to. |
| ``topics`` -> ``<MQTT topic>`` | - | Enables logging of the MQTT topic. |
| ``topics`` -> ``<MQTT topic>`` -> ``level`` | string; ``INFO``, ``WARN`` or ``ERROR`` | Log level to the created message. |
| ``topics`` -> ``<MQTT topic>`` -> ``type`` | string; ``bool``, ``uint8``, ``int8``, ``uint16``, ``int16``, ``uint32``, ``int32``, ``uint64``, ``int64``, ``float``, ``double`` or ``utf8`` | Binary format of the payload received in this topic. |


## **Usage**

```
source <path to virtual environment>/bin/activate
python3 -B src/mqttlogger.py --config /path/to/your/config/file.yaml
```

## **Get support**

You have trouble getting started? Something does not work as expected? You have some suggestions or thoughts? Please let me know.

Feel free to open an issue here on github or contact me on reddit: [3lr1ng0](https://www.reddit.com/user/3lr1ng0).
