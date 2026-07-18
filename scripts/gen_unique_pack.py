"""Generate a deterministic, gloss-specific unique landmark pack.

Usage:
    python scripts/gen_unique_pack.py --gloss work --cycle 2026-07-18a --out data/samples/work.json

Implements the documented unique-frame rule:
    seed   = sha256("demo-asl:{gloss}:{cycle_id}").hexdigest()[0:8]
    phase  = int(seed, 16) / 0xffffffff
then feeds `phase` into the synthetic spiral generator so each gloss gets a
repeatable but distinct landmark trajectory (no cloned/renamed frames).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

JOINTS = 21
FRAMES = 16


def phase_for(gloss: str, cycle_id: str) -> float:
    seed = hashlib.sha256(f"demo-asl:{gloss}:{cycle_id}".encode()).hexdigest()[0:8]
    return int(seed, 16) / 0xFFFFFF


def unique_frames(gloss: str, cycle_id: str, frames: int = FRAMES, joints: int = JOINTS) -> list:
    phase = phase_for(gloss, cycle_id)
    seq = []
    for f in range(frames):
        t = f / max(1, frames - 1)
        frame = []
        for j in range(joints):
            ang = t * math.pi * 2 + j * 0.15 + phase * math.pi * 2
            frame.append(
                [
                    round(0.5 + 0.2 * math.cos(ang), 6),
                    round(0.5 + 0.2 * math.sin(ang), 6),
                    round(0.02 * math.sin(ang * 2), 6),
                ]
            )
        seq.append(frame)
    return seq


def build(gloss: str, cycle_id: str) -> dict:
    return {
        "gloss": gloss,
        "language": "demo-asl",
        "fps": 15,
        "source": f"synthetic-unique-{cycle_id.split('-')[-1]}",
        "frames": unique_frames(gloss, cycle_id),
        "extractor": "unique-synthetic",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gloss", required=True)
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    payload = build(args.gloss, args.cycle)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} (source={payload['source']}, frames={len(payload['frames'])})")


if __name__ == "__main__":
    main()
