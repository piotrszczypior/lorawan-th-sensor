from flask import Flask, request, jsonify

from downlink import CMD_LED_OFF, CMD_LED_ON, send_downlink

app = Flask(__name__)


@app.route("/webhook/alert", methods=["POST"])
def handle_grafana_alert():
    data = request.json

    # https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/webhook-notifier/
    status = data.get("status")

    if status == "firing":
        handle_alarm_on()
    elif status == "resolved":
        handle_alarm_off()

    return jsonify({"status": "ok"}), 200


def handle_alarm_on():
    send_downlink(CMD_LED_ON)
    print(f"[ALARM] Temperature exceeds threshold!")


def handle_alarm_off():
    send_downlink(CMD_LED_OFF)
    print(f"[ALARM OFF] Temperature below threshold!")


def run_flask():
    app.run(host="0.0.0.0", port=5000)
