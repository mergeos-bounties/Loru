from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SEQUENCE_PATH_KEYS = ("sequence_path", "loru_sequence", "sample_path")
SOURCE_URL_KEYS = ("url", "source_url", "video_url")
METADATA_KEYS = ("bbox", "fps", "signer_id", "source", "variation_id")


def normalize_gloss(gloss: object) -> str:
    """Normalize WLASL gloss text to the sample-file style used by Loru."""
    value = str(gloss or "").strip().lower().replace("-", " ")
    return "_".join(part for part in value.split() if part)


def load_wlasl_manifest(index_path: Path, samples_dir: Path | None = None) -> list[dict[str, Any]]:
    """Convert a WLASL-style index JSON file into Loru manifest entries.

    The adapter reads local metadata only. It does not download source videos; if
    a matching local Loru sample exists, the manifest points at that JSON file.
    """
    index_path = Path(index_path)
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    manifests: list[dict[str, Any]] = []

    for entry in _index_entries(payload):
        original_gloss = _lookup(entry, (), ("gloss", "word"))
        gloss = normalize_gloss(original_gloss)
        if not gloss:
            continue

        instances = entry.get("instances") if isinstance(entry.get("instances"), list) else [entry]
        for position, instance in enumerate(instances):
            if not isinstance(instance, dict):
                continue
            sequence_path = _resolve_sequence_path(instance, index_path.parent, gloss, samples_dir)
            manifests.append(
                {
                    "dataset": "wlasl",
                    "gloss": gloss,
                    "original_gloss": str(original_gloss or gloss),
                    "video_id": str(_lookup(instance, entry, ("video_id", "id")) or f"{gloss}-{position}"),
                    "split": _lookup(instance, entry, ("split", "subset")),
                    "source_url": _lookup(instance, entry, SOURCE_URL_KEYS),
                    "frame_start": _optional_int(_lookup(instance, entry, ("frame_start", "start_frame"))),
                    "frame_end": _optional_int(_lookup(instance, entry, ("frame_end", "end_frame"))),
                    "sequence_path": str(sequence_path) if sequence_path else None,
                    "sequence_exists": bool(sequence_path and sequence_path.exists()),
                    "metadata": {
                        key: instance[key]
                        for key in METADATA_KEYS
                        if key in instance and instance[key] is not None
                    },
                }
            )

    return manifests


def write_wlasl_manifest(
    index_path: Path,
    out_path: Path,
    samples_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Write a Loru WLASL manifest JSON file and return its entries."""
    manifest = load_wlasl_manifest(index_path, samples_dir=samples_dir)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def _index_entries(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [entry for entry in payload if isinstance(entry, dict)]
    if isinstance(payload, dict):
        entries = payload.get("entries") or payload.get("data")
        if isinstance(entries, list):
            return [entry for entry in entries if isinstance(entry, dict)]
        return [payload]
    return []


def _lookup(
    primary: dict[str, Any],
    fallback: dict[str, Any] | tuple[()],
    keys: tuple[str, ...],
) -> Any:
    for key in keys:
        if key in primary and primary[key] is not None:
            return primary[key]
    if isinstance(fallback, dict):
        for key in keys:
            if key in fallback and fallback[key] is not None:
                return fallback[key]
    return None


def _resolve_sequence_path(
    instance: dict[str, Any],
    index_root: Path,
    gloss: str,
    samples_dir: Path | None,
) -> Path | None:
    for key in SEQUENCE_PATH_KEYS:
        raw_path = instance.get(key)
        if raw_path:
            path = Path(str(raw_path))
            return path if path.is_absolute() else (index_root / path).resolve()

    if samples_dir is None:
        return None

    path = Path(samples_dir) / f"{gloss}.json"
    return path if path.is_absolute() else path.resolve()


def _optional_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
