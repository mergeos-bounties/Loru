from pathlib import Path

from loru.infer.stream import stream_glosses
from loru.voice.tts import OfflineStubTTS, get_default_tts


def test_stream_glosses() -> None:
    r = stream_glosses(["hello", "thanks"])
    assert r["ok"]
    assert r["n"] == 2
    assert len(r["stream"]) == 2
    assert r["final_sentence"]


def test_offline_tts(tmp_path: Path) -> None:
    out = tmp_path / "t.wav"
    OfflineStubTTS().speak("hello world", out)
    assert out.exists() and out.stat().st_size > 100
    assert get_default_tts().backend_name
