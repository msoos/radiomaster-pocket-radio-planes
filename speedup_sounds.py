#!/usr/bin/env python3
"""Speed up sound-pack WAVs and trim leading/trailing silence.

Usage: speedup_sounds.py [--speed 1.5] SRC_DIR DST_DIR
"""
import argparse
import os
import shutil
import subprocess
import sys
import wave
from array import array
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SILENCE_DB = -45
PAD_MS = 10


def convert(src, dst, speed):
    with wave.open(str(src)) as w:
        rate, channels, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
    if channels != 1 or width != 2:
        raise ValueError(f"expected 16-bit mono, got {channels}ch {8 * width}-bit")

    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(src), "-filter:a", f"atempo={speed}",
         "-ar", str(rate), "-ac", "1", "-f", "s16le", "-"],
        check=True, capture_output=True).stdout
    samples = array("h", raw)
    if sys.byteorder == "big":
        samples.byteswap()

    thr = 32768 * 10 ** (SILENCE_DB / 20)
    loud = [i for i, x in enumerate(samples) if abs(x) > thr]
    # an all-silent clip is a deliberate pause, keep its length
    if loud:
        pad = rate * PAD_MS // 1000
        samples = samples[max(0, loud[0] - pad):loud[-1] + 1 + pad]

    if sys.byteorder == "big":
        samples.byteswap()
    dst.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(dst), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(samples.tobytes())
    return len(samples) / rate


def main():
    ap = argparse.ArgumentParser(description="Speed up sound-pack WAVs and trim leading/trailing silence.")
    ap.add_argument("--speed", type=float, default=1.5)
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    args = ap.parse_args()
    if args.src.resolve() == args.dst.resolve():
        ap.error("SRC_DIR and DST_DIR must differ")

    files = sorted(p for p in args.src.rglob("*") if p.is_file())
    wavs = [p for p in files if p.suffix.lower() == ".wav"]
    for p in files:
        if p not in wavs:
            out = args.dst / p.relative_to(args.src)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)

    def job(p):
        try:
            return convert(p, args.dst / p.relative_to(args.src), args.speed)
        except Exception as e:
            print(f"FAILED {p}: {e}", file=sys.stderr)
            return None

    with ThreadPoolExecutor(os.cpu_count()) as ex:
        durations = list(ex.map(job, wavs))
    failed = durations.count(None)
    print(f"{len(wavs) - failed} converted, {failed} failed, "
          f"{sum(d for d in durations if d):.1f}s total")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
