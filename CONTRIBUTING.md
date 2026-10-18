# Contributing to Loru

Thank you for your interest in contributing to Loru — an offline sign language toolkit (sign-to-text and sign-to-voice). This document covers setup, testing, the PR checklist, and how to claim MergeOS bounties.

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- For GUI development: PySide6 (included in `.[gui]`)

### Fork & Clone

1. **Fork** the repository on GitHub.
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Loru.git
   cd Loru
   ```
3. **Add upstream remote** (to sync later):
   ```bash
   git remote add upstream https://github.com/mergeos-bounties/Loru.git
   ```

### Setup

Create a virtual environment and install with dev dependencies:

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev,gui]"
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv venv
uv pip install -e ".[dev,gui]"
```

Verify installation:

```bash
loru version
loru data list
loru demo
```

### Optional Extras

```bash
pip install -e ".[torch]"     # ML training support
pip install -e ".[api]"       # FastAPI server
pip install -e ".[voice]"     # TTS voice synthesis
```

## Good First Issues

If you're new to the project, check out issues tagged with `good-first-issue` in the [issue tracker](https://github.com/mergeos-bounties/Loru/issues). These are beginner-friendly tasks that help you learn the codebase.

Suggested starting points:
- Adding a new gloss sample to `data/`
- Improving the CLI or GUI user experience
- Writing additional tests
- Improving documentation

## How to Contribute

- **Report bugs** by opening a GitHub Issue.
- **Suggest features** by opening a GitHub Issue with the `enhancement` label.
- **Add sign/gloss samples** by contributing to `data/` (with consent documentation).
- **Submit code** via a Pull Request.

## Development Workflow

1. Create a feature branch from `master`:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make your changes.
3. Run linting and tests:
   ```bash
   ruff check src tests
   pytest -q
   ```
4. Commit with a clear [Conventional Commits](https://www.conventionalcommits.org/) message:
   ```bash
   feat: add thank_you gloss sample
   ```
5. Push to your fork and open a Pull Request against `master`.
6. Link any related issues in the PR description using `Fixes #N`.

## Testing

### Run all tests

```bash
pytest -q
```

### Run a specific test file

```bash
pytest tests/test_infer.py -v
```

### Run with coverage

```bash
pytest --cov=src/loru --cov-report=term-missing
```

### Linting

```bash
ruff check src tests
ruff format --check src tests
```

### GUI smoke test

```bash
loru-gui
# or
loru gui
```

## Code Style

- Follow PEP 8 conventions.
- Run `ruff check` before committing.
- Write tests for new functionality.
- Line length limit: 100 characters.

## Pull Request Checklist

Before opening a PR, ensure:

- [ ] Code follows project style (`ruff check` passes)
- [ ] Tests added / updated for new functionality
- [ ] All existing tests pass (`pytest -q`)
- [ ] Documentation updated if needed
- [ ] PR description references related issues (`Fixes #N`)
- [ ] Changes are focused — one feature/fix per PR
- [ ] For sign/gloss data: consent documentation included

## Claim Flow (MergeOS MRG Bounties)

Loru participates in the [MergeOS bounty program](https://github.com/mergeos-bounties/mergeos). Contributors earn **MRG** tokens for merged work.

### How to claim a bounty

1. **Star** the repositories:
   - [Loru](https://github.com/mergeos-bounties/Loru)
   - [MergeOS](https://github.com/mergeos-bounties/mergeos)

2. **Comment** on the bounty issue: `I claim this bounty`

3. **Comment** on [MergeOS Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to the issue

4. **Open a PR** to Loru with `Fixes #<issue-number>` in the description

### Payout scale

| Scope | Typical MRG |
| --- | ---: |
| Small / good-first issue | 25 |
| Medium feature | 50 |
| Large system piece | 100 |
| Extra-large | 200 |

After the maintainer reviews and merges your PR, MRG is credited to `github:<your-username>` on the MergeOS ledger.

For full details, see [docs/BOUNTY.md](docs/BOUNTY.md).

## Need Help?

Open a [Discussion](https://github.com/mergeos-bounties/Loru/discussions) or ask in the relevant issue.