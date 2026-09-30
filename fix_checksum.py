#!/usr/bin/env python3
# Recompute the checksum line of EdgeTX radio.yml after hand edits. Usage: ./fix_checksum.py [radio.yml]
import re, sys
from pathlib import Path


# CRC-16 poly 0x1021, init 0xFFFF, over everything after the checksum line (radio/src/storage/sdcard_yaml.cpp)
def crc16(data, c=0xFFFF):
    for b in data:
        c ^= b << 8
        for _ in range(8):
            c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c


p = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / 'backup/RADIO/radio.yml')
raw = p.read_bytes()
m = re.match(rb'(checksum: *)(\d+)([\r\n]+)', raw)
if not m:
    sys.exit(f'{p}: no checksum line')
new = crc16(raw[m.end():])
if new != int(m[2]):
    p.write_bytes(m[1] + str(new).encode() + m[3] + raw[m.end():])
    print(f'{p}: checksum {int(m[2])} -> {new}')
