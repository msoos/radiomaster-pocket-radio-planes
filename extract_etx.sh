#!/bin/sh
# Unpack an .etx into backup/, replacing its contents. Usage: ./extract_etx.sh [file.etx]  (default backup.etx)
set -e
etx=$(realpath "${1:-backup.etx}")
cd "$(dirname "$0")"
# start fresh so models deleted on the radio don't linger
rm -rf backup/RADIO backup/MODELS
unzip -qo "$etx" -d backup
./check_sensors.py
