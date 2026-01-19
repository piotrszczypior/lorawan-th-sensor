import json
import os
from typing import Any

import paho.mqtt.client as mqtt
import requests

from downlink import CMD_LED_OFF, CMD_LED_ON, send_downlink

INFLUX_HOST = os.getenv("INFLUX_HOST", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_INIT_ADMIN_TOKEN", "")
INFLUX_ORG = os.getenv("INFLUXDB_INIT_ORG", "pwr")
INFLUX_BUCKET = os.getenv("INFLUXDB_INIT_BUCKET", "pwr")

DEV_EUI = os.getenv("MQTT_DEV_EUI", "")

DEBUG = True


def parse_data(value) -> tuple[float, float]:
    if DEBUG:
        return 32.0, 50.0

    temp, hum = value.split(",")
    temp = temp.split(":")[1]
    hum = hum.split(":")[1]
    return float(temp), float(hum)


def write_to_influx(device_id: str, temp: float, hum: float) -> None:
    """
    Send data to InfluxDB v2 via HTTP API.
    Line Protocol format: measurement,tag=value field=value
    """
    url = f"{INFLUX_HOST}/api/v2/write?org={INFLUX_ORG}&bucket={INFLUX_BUCKET}&precision=s"

    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain; charset=utf-8",
    }

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

    temp, hum = parse_data(payload_from_device)

    write_to_influx(DEV_EUI, temp, hum)
