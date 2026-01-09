# LoRaWAN Temperature & Humidity Sensor

Collects temperature and humidity data from LoRaWAN sensors via The Things Network (TTN) and stores them in InfluxDB.

## Configuration

Copy the template below to `.env` file and fill in your credentials:

```env
# InfluxDB Configuration
INFLUX_HOST=http://localhost:8086
INFLUXDB_INIT_MODE=setup
INFLUXDB_INIT_USERNAME=admin
INFLUXDB_INIT_PASSWORD=your-password
INFLUXDB_INIT_ORG=your-org
INFLUXDB_INIT_BUCKET=your-bucket
INFLUXDB_INIT_ADMIN_TOKEN=your-influxdb-token

# MQTT Configuration (The Things Network)
MQTT_HOST=eu1.cloud.thethings.network
MQTT_PORT=8883
MQTT_USERNAME=your-app@ttn
MQTT_KEY=your-ttn-api-key
MQTT_APP_ID=your-app-id
MQTT_DEV_EUI=your-device-eui
```
