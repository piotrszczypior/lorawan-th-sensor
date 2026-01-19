import os
import threading

from dotenv import load_dotenv

load_dotenv()

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from downlink import set_mqtt_client
from uplink import on_message
from webhook import run_flask

# MQTT Configuration (The Things Network)
HOST = os.getenv("MQTT_HOST", "eu1.cloud.thethings.network")
PORT = int(os.getenv("MQTT_PORT", "8883"))
USERNAME = os.getenv("MQTT_USERNAME", "")
KEY = os.getenv("MQTT_KEY", "")
APP_ID = os.getenv("MQTT_APP_ID", "")
DEV_EUI = os.getenv("MQTT_DEV_EUI", "")


def initialize_mqtt_client() -> None:
    mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    mqtt_client.username_pw_set(USERNAME, KEY)
    mqtt_client.tls_set()
    mqtt_client.on_message = on_message

    err = mqtt_client.connect(HOST, PORT, keepalive=60)
    if err != 0:
        print(f"Could not connect to MQTT broker, error code: {err}")
        return

    print("Connected to MQTT broker")
    set_mqtt_client(mqtt_client)

    sub = f"v3/{APP_ID}@ttn/devices/{DEV_EUI}/up"
    print(sub)
    mqtt_client.subscribe(sub)
    print(f"Subscribed to uplink of device {DEV_EUI}")

    mqtt_client.loop_forever()


def main():
    # start webhook for downlink
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # start mqtt subscription for uplinks
    initialize_mqtt_client()


if __name__ == "__main__":
    main()
