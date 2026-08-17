from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np

from loru.data.loader import list_sample_files, load_sequence


def hash_frame(frame: np.ndarray, decimals: int = 4) -> str:
    """Return MD5 hash of rounded flattened frame."""
    rounded = np.round(frame, decimals).flatten()
    return hashlib.md5(rounded.tobytes()).hexdigest()


def detect_duplicates(
    samples_dir: Path | None = None, min_sequence_length: int = 5, decimals: int = 4
) -> list[dict]:
    """
    Detect near-duplicate frame sequences across JSON samples.
    Returns a list of dicts describing overlaps.
    """
    paths = list_sample_files(samples_dir)
    file_info = []

    for path in paths:
        try:
            gloss, frames = load_sequence(path)
            if frames.size > 0:
                file_info.append({"path": path, "gloss": gloss, "frames": frames})
        except Exception:
            pass # S110

    hash_locations = defaultdict(list)
    for idx, info in enumerate(file_info):
        for f_idx, frame in enumerate(info["frames"]):
            h = hash_frame(frame, decimals=decimals)
            hash_locations[h].append((idx, f_idx))

    duplicates = []
    seen_overlaps = set()

    for idx_a, info_a in enumerate(file_info):
        frames_a = info_a["frames"]
        max_start = len(frames_a) - min_sequence_length
        if max_start < 0:
            continue

        for start_a in range(max_start + 1):
            h = hash_frame(frames_a[start_a], decimals=decimals)

            for idx_b, start_b in hash_locations.get(h, []):
                # Only compare distinct files (and avoid A->B vs B->A)
                if idx_b <= idx_a:
                    continue

                length = 1
                frames_b = file_info[idx_b]["frames"]
                while (start_a + length < len(frames_a) and start_b + length < len(frames_b)):
                    h_a = hash_frame(frames_a[start_a + length], decimals=decimals)
                    h_b = hash_frame(frames_b[start_b + length], decimals=decimals)
                    if h_a == h_b:
                        length += 1
                    else:
                        break

                if length >= min_sequence_length:
                    # Check if already subsumed
                    is_subsumed = False
                    for prev_a, prev_b, p_start_a, p_start_b, p_len in seen_overlaps:
                        if (
                            prev_a == idx_a and prev_b == idx_b
                            and p_start_a <= start_a and start_a + length <= p_start_a + p_len
                            and p_start_b <= start_b and start_b + length <= p_start_b + p_len
                            and start_a - p_start_a == start_b - p_start_b
                        ):
                            is_subsumed = True
                            break
                    if not is_subsumed:
                        seen_overlaps.add((idx_a, idx_b, start_a, start_b, length))
                        duplicates.append(
                            {
                                "file_a": info_a["path"].name,
                                "file_b": file_info[idx_b]["path"].name,
                                "offset_a": start_a,
                                "offset_b": start_b,
                                "length": length,
                            }
                        )

    return duplicates
