#!/usr/bin/env bash

set -e

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

docker run \
  --rm \
  -p 8086:8086 \
  -v influxdb-data:/var/lib/influxdb2 \
  -v influxdb-config:/etc/influxdb2 \
  -e DOCKER_INFLUXDB_INIT_MODE="${INFLUXDB_INIT_MODE}" \
  -e DOCKER_INFLUXDB_INIT_USERNAME="${INFLUXDB_INIT_USERNAME}" \
  -e DOCKER_INFLUXDB_INIT_PASSWORD="${INFLUXDB_INIT_PASSWORD}" \
  -e DOCKER_INFLUXDB_INIT_ORG="${INFLUXDB_INIT_ORG}" \
  -e DOCKER_INFLUXDB_INIT_BUCKET="${INFLUXDB_INIT_BUCKET}" \
  -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN="${INFLUXDB_INIT_ADMIN_TOKEN}" \
  influxdb:2.7

echo "InfluxDB started on http://localhost:8086"
