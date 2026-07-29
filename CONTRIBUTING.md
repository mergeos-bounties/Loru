# Contributing to Loru

Thank you for your interest! Loru is an offline sign language toolkit funded through MergeOS bounties.

## Setup

```bash
git clone https://github.com/mergeos-bounties/Loru
cd Loru
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,gui]"
```

## Run tests

```bash
pytest -q        # unit tests
ruff check src tests  # lint
loru demo        # end-to-end smoke test
```

## PR checklist

- [ ] `pytest -q` passes
- [ ] `ruff check src tests` passes
- [ ] `loru demo` runs successfully
- [ ] Code follows existing style (line-length 100, py311)
- [ ] No new dependencies added unless discussed

## MergeOS bounties

This project rewards contributors with **MRG** credits.  
See [docs/BOUNTY.md](docs/BOUNTY.md) for the full claim flow.
