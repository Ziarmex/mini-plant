#!/usr/bin/env python3
"""
Pont MQTT -> InfluxDB
Souscrit aux topics IoT MQTT et écrit les points de données dans InfluxDB 2.x
"""

import os
import sys
import json
import time
import struct
import base64
import hashlib
import requests
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "iot/plant/#")

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "mini-plant")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "iot-data")

client = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[pont] Connecté au broker MQTT sur {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC, qos=1)
        print(f"[pont] Abonné à {MQTT_TOPIC}")
    else:
        print(f"[pont] Échec de connexion MQTT : {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_type = payload.get("device_type", "inconnu")
        device_id = payload.get("device_id", "inconnu")

        fields = {}
        for key, value in payload.items():
            if isinstance(value, (int, float)) and key not in ("timestamp", "device_id", "device_type", "status"):
                fields[key] = value

        if not fields:
            return

        line = f"{device_type},device_id={device_id}"
        field_parts = []
        for k, v in fields.items():
            field_parts.append(f"{k}={v}")
        line += " " + ",".join(field_parts)

        resp = requests.post(
            f"{INFLUXDB_URL}/api/v2/write?org={INFLUXDB_ORG}&bucket={INFLUXDB_BUCKET}&precision=s",
            headers={"Authorization": f"Token {INFLUXDB_TOKEN}"},
            data=line,
            timeout=5
        )

        if resp.status_code == 204:
            print(f"[pont] Écrit {device_id} : {fields}")
        else:
            print(f"[pont] Erreur d'écriture InfluxDB {resp.status_code} : {resp.text}")

    except Exception as e:
        print(f"[pont] Erreur : {e}")

def main():
    global client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "pont-mqtt-influxdb")
    client.on_connect = on_connect
    client.on_message = on_message

    for attempt in range(10):
        try:
            print(f"[pont] Connexion au broker MQTT (tentative {attempt+1}/10)...")
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_forever()
        except Exception as e:
            print(f"[pont] Connexion échouée : {e}")
            if attempt < 9:
                time.sleep(5)

    print("[pont] Arrêt")
    sys.exit(1)

if __name__ == "__main__":
    main()
