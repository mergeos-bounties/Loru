# Contributing to Loru

Thank you for your interest in contributing to Loru, an offline sign language toolkit.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Loru.git
   cd Loru
   ```
3. **Set up a development environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Prerequisites

- Python 3.11+
- PySide6 (installed automatically via pip)
- No GPU required for development

## Running Tests

```bash
pytest
```

Run a specific test file:
```bash
pytest tests/test_sign.py
```

## Code Style

- Follow PEP 8 conventions
- Run `ruff check` before committing:
  ```bash
  ruff check src tests
  ```

## Development Workflow

1. Create a feature branch from `master`:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make your changes
3. Run linting and tests:
   ```bash
   ruff check src tests
   pytest
   ```
4. Commit with a clear message:
   ```
   feat: add sign transition smoothing for XYZ
   ```
5. Push to your fork and open a Pull Request against `master`
6. Link any related issues using `Fixes #N` in the PR description

## Pull Request Checklist

- [ ] Code follows project style (ruff passes)
- [ ] Tests added or updated for new functionality
- [ ] All existing tests pass
- [ ] Documentation updated if needed
- [ ] PR description references related issues

## How to Contribute

- **Report bugs** by opening a GitHub Issue
- **Suggest features** by opening a GitHub Issue with the `enhancement` label
- **Submit code** via a Pull Request

## MergeOS Bounty Claim Flow

This repository participates in the MergeOS bounty program.

1. Star the [Loru repo](https://github.com/mergeos-bounties/Loru) and the [MergeOS repo](https://github.com/mergeos-bounties/mergeos)
2. Comment `I claim this bounty` on the target issue
3. Comment on [MergeOS Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to the issue
4. Open a PR with `Fixes #<issue-number>` in the description
5. After review and merge, the maintainer will release the bounty

See [docs/BOUNTY.md](docs/BOUNTY.md) for full policy details.

## Need Help?

Open a [Discussion](https://github.com/mergeos-bounties/Loru/discussions) or ask in the relevant issue.
