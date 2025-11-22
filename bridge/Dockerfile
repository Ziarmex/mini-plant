FROM python:3.11-slim

RUN pip install --no-cache-dir paho-mqtt requests

COPY mqtt_to_influxdb.py /app/bridge.py

CMD ["python", "-u", "/app/bridge.py"]
