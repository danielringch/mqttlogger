FROM python:alpine

WORKDIR /mqttlogger

COPY requirements.txt ./
COPY src ./src

RUN pip install --no-cache-dir -r ./requirements.txt

ENV PYTHONUNBUFFERED=1
CMD [ "python3", "./src/mqttlogger.py","--config","/config/mqttlogger.yaml"]
