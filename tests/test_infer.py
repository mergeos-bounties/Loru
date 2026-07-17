from pathlib import Path

def test_thanks_gloss():
    thanks_path = Path("data/samples/thanks.json")
    assert thanks_path.exists(), "Thanks sample not found"
    gloss, _ = load_sequence(thanks_path)
    assert gloss == "thanks", "Thanks gloss not recognized"
