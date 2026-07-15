from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from loru.cli import app
from loru.data.wlasl import load_wlasl_manifest, write_wlasl_manifest


FIXTURES = Path(__file__).parent / "fixtures"


def test_load_wlasl_manifest_normalizes_entries() -> None:
    manifest = load_wlasl_manifest(FIXTURES / "wlasl_index.json", samples_dir=Path("data/samples"))

    assert [entry["gloss"] for entry in manifest] == ["thank_you", "hello"]
    assert manifest[0]["video_id"] == "wlasl-thank-you-001"
    assert manifest[0]["split"] == "train"
    assert manifest[0]["source_url"] == "https://example.invalid/wlasl/thank-you.mp4"
    assert manifest[0]["sequence_path"].endswith("data/samples/thank_you.json")
    assert manifest[0]["sequence_exists"] is True
    assert manifest[0]["frame_start"] == 1
    assert manifest[0]["frame_end"] == 48

    assert manifest[1]["gloss"] == "hello"
    assert manifest[1]["sequence_path"].endswith("data/samples/hello.json")
    assert manifest[1]["sequence_exists"] is True


def test_write_wlasl_manifest_outputs_loru_manifest(tmp_path: Path) -> None:
    out = tmp_path / "manifest.json"

    write_wlasl_manifest(FIXTURES / "wlasl_index.json", out, samples_dir=Path("data/samples"))

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["dataset"] == "wlasl"
    assert payload[0]["gloss"] == "thank_you"


def test_wlasl_manifest_cli_writes_manifest(tmp_path: Path) -> None:
    out = tmp_path / "manifest.json"
    result = CliRunner().invoke(
        app,
        [
            "data",
            "wlasl-manifest",
            "--index",
            str(FIXTURES / "wlasl_index.json"),
            "--samples-dir",
            "data/samples",
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0
    assert "WLASL manifest" in result.output
    assert json.loads(out.read_text(encoding="utf-8"))[1]["gloss"] == "hello"
