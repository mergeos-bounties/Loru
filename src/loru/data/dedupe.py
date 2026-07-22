from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

import numpy as np
from rich.console import Console
from rich.table import Table

from loru.data.compare import compare_gloss_samples
from loru.data.loader import list_sample_files, load_sequence

console = Console()


def _frame_hash(frames: np.ndarray) -> str:
    """SHA256 hash of canonical JSON-serialized frames for exact duplicate detection."""
    flat = frames.astype(np.float64)
    payload = json.dumps(flat.tolist(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _detect_exact_duplicates(
    directory: Path,
    threshold: float = 0.0,
) -> list[dict]:
    """Find gloss files whose frame data hashes identically."""
    files = list_sample_files(directory)
    hash_map: dict[str, list[Path]] = {}
    for path in files:
        _, frames = load_sequence(path)
        if frames.size == 0:
            continue
        h = _frame_hash(frames)
        hash_map.setdefault(h, []).append(path)

    results = []
    for h, paths in hash_map.items():
        if len(paths) < 2:
            continue
        results.append({
            "hash": h[:16],
            "count": len(paths),
            "files": [str(p) for p in sorted(paths)],
            "type": "exact",
        })
    return results


def _detect_near_duplicates(
    directory: Path,
    threshold: float = 0.01,
    max_comparisons: int = 5000,
) -> list[dict]:
    """Compare all sample pairs by frame similarity; flag those within threshold."""
    files = list_sample_files(directory)
    n = len(files)
    if n < 2:
        return []

    # Limit combinatorial explosion for large catalogs
    total_pairs = n * (n - 1) // 2
    pairs_to_check = min(total_pairs, max_comparisons)

    results = []
    checked = 0
    for i in range(n):
        for j in range(i + 1, n):
            if checked >= pairs_to_check:
                break
            checked += 1
            a, b = files[i], files[j]
            try:
                cmp = compare_gloss_samples(a, b)
            except ValueError:
                continue  # incompatible dimensions
            dist = cmp["mean_landmark_distance"]
            if dist <= threshold:
                results.append({
                    "file_a": str(a),
                    "file_b": str(b),
                    "gloss_a": cmp["a"]["gloss"],
                    "gloss_b": cmp["b"]["gloss"],
                    "mean_distance": dist,
                    "frame_delta": cmp["frame_delta"],
                    "type": "near",
                })
        if checked >= pairs_to_check:
            break

    results.sort(key=lambda r: r["mean_distance"])
    return results


def detect_duplicates(
    directory: Path,
    near_threshold: float = 0.01,
    max_comparisons: int = 5000,
) -> dict:
    """Run exact hash + near-similarity duplicate scan across all gloss samples.

    Returns a structured report with exact duplicates, near-matches, and summary stats.
    """
    exact = _detect_exact_duplicates(directory)
    near = _detect_near_duplicates(
        directory, threshold=near_threshold, max_comparisons=max_comparisons
    )
    files = list_sample_files(directory)
    return {
        "scanned": len(files),
        "exact_duplicate_groups": len(exact),
        "exact_duplicates": exact,
        "near_duplicate_pairs": len(near),
        "near_duplicates": near,
        "threshold": near_threshold,
    }


def _find_group_hash(files: list[Path]) -> Optional[str]:
    """Return hash if all files share identical frames, else None."""
    if len(files) < 2:
        return None
    hashes = set()
    for p in files:
        _, frames = load_sequence(p)
        if frames.size == 0:
            return None
        hashes.add(_frame_hash(frames))
    if len(hashes) == 1:
        return hashes.pop()[:16]
    return None


def dedupe_report_table(report: dict) -> None:
    """Pretty-print duplicate detection results with rich."""
    console.print(f"\n[bold]Duplicate Scan[/bold] — {report['scanned']} samples scanned")

    if report["exact_duplicate_groups"] > 0:
        console.print(
            f"[red]{report['exact_duplicate_groups']} exact-duplicate groups found[/red]"
        )
        table = Table(title="Exact Duplicates")
        table.add_column("Hash (first 16)", style="dim")
        table.add_column("Count", justify="right")
        table.add_column("Files")
        for dup in report["exact_duplicates"]:
            table.add_row(dup["hash"], str(dup["count"]), ", ".join(dup["files"]))
        console.print(table)
    else:
        console.print("[green]No exact-frame duplicates found[/green]")

    if report["near_duplicate_pairs"] > 0:
        console.print(
            f"[yellow]{report['near_duplicate_pairs']} near-duplicate pairs "
            f"(≤ {report['threshold']})[/yellow]"
        )
        table = Table(title="Near Duplicates")
        table.add_column("Mean Distance", justify="right")
        table.add_column("File A")
        table.add_column("File B")
        table.add_column("Frame Δ", justify="right")
        for nd in report["near_duplicates"]:
            table.add_row(
                str(nd["mean_distance"]),
                nd["file_a"],
                nd["file_b"],
                str(nd["frame_delta"]),
            )
        console.print(table)
    else:
        console.print("[green]No near-duplicate pairs found[/green]")

    console.print("[bold]Scan complete.[/bold]")