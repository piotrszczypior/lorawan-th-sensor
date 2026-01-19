from webhook import run_flask

import base64
import json
import os
from typing import Any
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import requests
from dotenv import load_dotenv
import threading


load_dotenv()

# LED command bytes (must match firmware)
CMD_LED_OFF = 0x00
CMD_LED_ON = 0x01

# Alarm configuration
TEMP_THRESHOLD = 20.0
DEBUG_ALARM = False  # Set to True to simulate high temperature for testing
DEBUG_ALARM_TEMP = 20.0  # Simulated temperature when DEBUG_ALARM is True

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

DEBUG = False


def parse_data(value) -> tuple[float, float]:
    if DEBUG:
        return 20.0, 50.0

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


def send_downlink(client: mqtt.Client, command: int) -> None:
    """
    Send a downlink command to the device via TTN MQTT.
    """
    topic = f"v3/{APP_ID}@ttn/devices/{DEV_EUI}/down/push"

    payload_bytes = bytes([command])
    payload_b64 = base64.b64encode(payload_bytes).decode("ascii")

    downlink_msg = {
        "downlinks": [
            {
                "f_port": 1,
                "frm_payload": payload_b64,
                "priority": "NORMAL",
            }
        ]
    }

    client.publish(topic, json.dumps(downlink_msg))
    cmd_name = "LED_ON" if command == CMD_LED_ON else "LED_OFF"
    print(f"[DOWNLINK] Sent {cmd_name} command to {DEV_EUI}")


def check_temperature_alarm(client: mqtt.Client, temp: float) -> None:
    """
    Check if temperature exceeds threshold and send alarm command.
    """
    # command = CMD_LED_ON if temp > TEMP_THRESHOLD else CMD_LED_OFF

    if temp > TEMP_THRESHOLD:
        print(f"[ALARM] Temperature {temp}°C exceeds threshold {TEMP_THRESHOLD}°C!")
        command = CMD_LED_ON
    else:
        print(f"[OK] Temperature {temp}°C is below threshold {TEMP_THRESHOLD}°C")
        command = CMD_LED_OFF

    print(f"Sending downlink to device. Command: {command}")
    # if DEBUG:
        # return

    send_downlink(client, command)


def on_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
    data = json.loads(message.payload.decode())
    print(data)
    payload_from_device = data["uplink_message"]["decoded_payload"]["text"]
    print(payload_from_device)

    temp, hum = parse_data(payload_from_device)

    write_to_influx(DEV_EUI, temp, hum)

    # Parse temperature and check alarm
    if DEBUG_ALARM:
        temp = DEBUG_ALARM_TEMP
        print(f"[DEBUG_ALARM] Using simulated temperature: {temp}°C")

    check_temperature_alarm(client, temp)


def main() -> None:
    mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
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
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    main()

   