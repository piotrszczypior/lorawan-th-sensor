import json
import os
from typing import Any

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import requests
from dotenv import load_dotenv

load_dotenv()

# MQTT Configuration (The Things Network)
HOST = os.getenv("MQTT_HOST", "eu1.cloud.thethings.network")
PORT = int(os.getenv("MQTT_PORT", "8883"))
USERNAME = os.getenv("MQTT_USERNAME", "")
KEY = os.getenv("MQTT_KEY", "")
APP_ID = os.getenv("MQTT_APP_ID", "")
DEV_EUI = os.getenv("MQTT_DEV_EUI", "")

# InfluxDB Configuration
INFLUX_HOST = os.getenv("INFLUX_HOST", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_INIT_ADMIN_TOKEN", "")
INFLUX_ORG = os.getenv("INFLUXDB_INIT_ORG", "pwr")
INFLUX_BUCKET = os.getenv("INFLUXDB_INIT_BUCKET", "pwr")

DEBUG = True


def parse_data(value) -> tuple[float, float]:
    temp, hum = value.split(",")
    temp = temp.split(":")[1]
    hum = hum.split(":")[1]

    return float(temp), float(hum)


def write_to_influx(device_id: str, value: str) -> None:
    """
    Send data to InfluxDB v2 via HTTP API.
    Line Protocol format: measurement,tag=value field=value
    """
    url = f"{INFLUX_HOST}/api/v2/write?org={INFLUX_ORG}&bucket={INFLUX_BUCKET}&precision=s"

    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain; charset=utf-8",
    }

    if DEBUG:
        temp, hum = 20.0, 50.0
    else:
        temp, hum = parse_data(value)

    line_protocol = f"measurements_ttn,device={device_id} T={temp},H={hum}"

    print(f"[DEBUG] Line Protocol: {line_protocol}")

    try:
        response = requests.post(url, data=line_protocol, headers=headers)
        if response.status_code == 204:
            print("-> Saved to FluxDB (HTTP 204)")
        else:
            print(
                f"! Error while saving to InfluxDB: {response.status_code} - {response.text}"
            )
    except requests.RequestException as e:
        print(f"! Exception while connecting to InfluxDB: {e}")


def on_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
    data = json.loads(message.payload.decode())
    print(data)
    payload_from_device = data["uplink_message"]["decoded_payload"]["text"]
    print(payload_from_device)

    write_to_influx(DEV_EUI, payload_from_device)


def main() -> None:
    mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION1)
    mqtt_client.username_pw_set(USERNAME, KEY)
    mqtt_client.tls_set()
    mqtt_client.on_message = on_message

    err = mqtt_client.connect(HOST, PORT, keepalive=60)
    if err != 0:
        print(f"Could not connect to MQTT broker, error code: {err}")
        return

    print("Connected to MQTT broker")

    sub = f"v3/{APP_ID}@ttn/devices/{DEV_EUI}/up"
    print(sub)
    mqtt_client.subscribe(sub)
    print(f"Subscribed to uplink of device {DEV_EUI}")

    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
