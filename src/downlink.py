import base64
import json
import os
from typing import Optional

import paho.mqtt.client as mqtt

CMD_LED_OFF = 0x00
CMD_LED_ON = 0x01

APP_ID = os.getenv("MQTT_APP_ID", "")
DEV_EUI = os.getenv("MQTT_DEV_EUI", "")

_mqtt_client: Optional[mqtt.Client] = None


def set_mqtt_client(client: mqtt.Client) -> None:
    global _mqtt_client
    _mqtt_client = client


def get_mqtt_client() -> Optional[mqtt.Client]:
    return _mqtt_client


def send_downlink(command: int) -> bool:
    """
    Send a downlink command to the device via TTN MQTT.
    Returns True if sent successfully, False if client not available.
    """
    client = _mqtt_client
    if client is None:
        print("[DOWNLINK] Error: MQTT client not initialized")
        return False

    topic = f"v3/{APP_ID}@ttn/devices/{DEV_EUI}/down/push"

    payload_bytes = bytes([command])
    payload_b64 = base64.b64encode(payload_bytes).decode("ascii")

    downlink_msg = {
        "downlinks": [
            {
                "f_port": 1,
                "frm_payload": payload_b64,
                "priority": "NORMAL"
            }
        ]
    }

    client.publish(topic, json.dumps(downlink_msg))
    cmd_name = "LED_ON" if command == CMD_LED_ON else "LED_OFF"
    print(f"[DOWNLINK] Sent {cmd_name} command to {DEV_EUI}")
    return True
