#!/bin/sh
# Rebuild backup.etx from the backup/ folder. Usage: ./make_etx.sh
set -e
cd "$(dirname "$0")"
./fix_checksum.py
# zip -r into an existing archive keeps entries deleted from backup/, so start fresh
rm -f backup.etx
cd backup
zip -qrXD ../backup.etx RADIO MODELS
