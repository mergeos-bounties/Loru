# Contributing to Loru

Thank you for your interest in contributing to **Loru** — an offline sign language recognition toolkit (sign → text, sign → voice).

## Table of contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running tests](#running-tests)
- [Linting](#linting)
- [PR checklist](#pr-checklist)
- [Bounty claims (MergeOS MRG)](#bounty-claims-mergeos-mrg)

---

## Prerequisites

- Python **3.11+**
- `git`
- (Optional) `uv` for fast dependency installs — `pip install uv`

---

## Setup

```bash
# 1. Clone your fork
git clone https://github.com/<your-username>/Loru.git
cd Loru

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scriptsctivate         # Windows PowerShell

# 3. Install with dev extras
pip install -e ".[dev]"

# 4. Smoke-test the install
loru version
loru data list
loru demo
```

> **Tip:** use `pip install -e ".[dev,gui,api,voice]"` to enable all optional features.

---

## Running tests

```bash
pytest -q
```

All tests live under `tests/`. The config in `pyproject.toml` sets `testpaths = ["tests"]` and `pythonpath = ["src"]`, so no extra flags are needed.

To run a single file or test:

```bash
pytest tests/test_<module>.py -v
pytest -k "test_my_function"
```

---

## Linting

```bash
ruff check src tests
```

Auto-fix safe issues:

```bash
ruff check --fix src tests
```

Line length is **100** and the target is **Python 3.11** (see `pyproject.toml`).

---

## PR checklist

Before opening a pull request, make sure:

- [ ] `pytest -q` passes with no failures
- [ ] `ruff check src tests` reports no errors
- [ ] New behaviour is covered by at least one test
- [ ] Commit messages are clear and reference the relevant issue (e.g. `Fixes #19`)
- [ ] The PR description explains **what** changed and **why**
- [ ] Screenshots or command output are included for GUI or pipeline changes
- [ ] Dataset additions note the data license

---

## Bounty claims (MergeOS MRG)

Loru pays contributors in **MRG** through the [MergeOS bounty programme](docs/BOUNTY.md).

**Step-by-step:**

1. Star [mergeos-bounties/Loru](https://github.com/mergeos-bounties/Loru) and [mergeos-bounties/mergeos](https://github.com/mergeos-bounties/mergeos).
2. Comment `I claim this bounty` on the Loru issue you are working on.
3. Comment on [MergeOS Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to the Loru issue.
4. Open a PR to **Loru `master`** with `Fixes #<issue-number>` in the body.
5. After the PR is reviewed and merged, the maintainer credits `github:<your-username>` on the MergeOS ledger.

See [docs/BOUNTY.md](docs/BOUNTY.md) for the full payout scale and policy.

---

_Happy hacking! If you get stuck, open an issue or ping the maintainers._
