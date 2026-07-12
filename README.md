# Loru

**Loru** is a training and inference toolkit for **sign language recognition**:

| Mode | Description |
| --- | --- |
| **Sign → Text** | Video / landmark sequences → gloss or natural language text |
| **Sign → Voice** | Sign recognition → TTS audio output |

Built under the [mergeos-bounties](https://github.com/mergeos-bounties) org so delivery can be funded as MergeOS tasks with MRG payouts.

## Stack

- Python 3.11+
- CLI: `typer` + `rich`
- Dataset / sample pipeline (pluggable)
- Training stubs (PyTorch optional extra)
- Inference API sketch (FastAPI optional extra)
- TTS adapter interface (sign → voice)

## Quick start

```bash
cd Loru
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -e ".[dev]"
loru --help
```

## Commands

```bash
# Show config / version
loru version

# List sample dataset
loru data list

# Run a tiny offline demo: fake landmarks → text gloss
loru infer demo --sign hello

# Sign → text (demo model)
loru infer text --sequence data/samples/hello.json

# Sign → voice (writes wav via offline TTS stub)
loru infer voice --sequence data/samples/hello.json --out data/out/hello.wav

# Train a toy classifier on bundled samples
loru train toy --epochs 3

# Export training report
loru train report
```

## Layout

```
src/loru/
  cli.py              # Typer entry
  config.py
  models/             # gloss vocab + toy model
  data/               # loaders + sample sequences
  train/              # training loop stubs
  infer/              # sign→text pipeline
  voice/              # text→speech adapters
  api/                # optional FastAPI app
data/samples/         # tiny JSON landmark sequences
docs/BOUNTY.md        # MergeOS MRG claim rules
```

## MergeOS bounties

1. Star this repo + [mergeos](https://github.com/mergeos-bounties/mergeos)
2. Claim an issue labeled `bounty`
3. Also claim on MergeOS [issue #1](https://github.com/mergeos-bounties/mergeos/issues/1)
4. Open a PR with tests/evidence
5. Maintainer merges and credits MRG (25/50/100/200)

See [docs/BOUNTY.md](docs/BOUNTY.md).

## Privacy & ethics

- Prefer **consented** datasets and public research corpora with clear licenses.
- Do not scrape private video without permission.
- Document dataset licenses in every PR that adds data.

## License

MIT
