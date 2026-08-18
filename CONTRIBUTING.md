# Contributing to Loru

Thank you for your interest in contributing to **Loru** — an offline sign language toolkit for landmark sequences → gloss/text and sign → voice.

---

## 🚀 Quick Setup

```bash
# 1. Fork & clone
https://github.com/mergeos-bounties/Loru
cd Loru

# 2. Create virtual environment (Python 3.11+)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. (Optional) Install GUI dependencies
pip install -e ".[gui]"

# 5. (Optional) Install API dependencies
pip install -e ".[api]"
```

---

## 🧪 Test Commands

```bash
# Run all tests with coverage
pytest --cov=loru --cov-report=term --cov-fail-under=75

# Run tests only (no coverage)
pytest

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v
```

---

## 🔍 Code Quality Checks

```bash
# Format check (run in CI)
ruff format --check .

# Auto-format
ruff format .

# Lint check
ruff check .

# Auto-fix lint issues
ruff check --fix .
```

---

## ✅ PR Checklist

Before submitting a PR, please ensure:

- [ ] **Tests pass**: `pytest --cov=loru --cov-fail-under=75`
- [ ] **Format check passes**: `ruff format --check .`
- [ ] **Lint passes**: `ruff check .`
- [ ] **Type hints** added for new public functions (where practical)
- [ ] **Docstrings** for new modules/classes/functions (Google style)
- [ ] **README updated** if CLI commands or features change
- [ ] **CHANGELOG.md** updated (if exists) or version bump noted
- [ ] **Linked issue**: PR description includes `Fixes #<issue-number>`
- [ ] **Single commit** or clean history (squash if needed)

---

## 📝 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

**Examples**:
- `feat(cli): add --voice flag to infer command`
- `fix(data): handle empty landmark sequences`
- `docs: update CLI reference in README`
- `test(core): add unit tests for gloss mapper`

---

## 🌿 Branch Naming

- `feat/<short-description>` — new features
- `fix/<short-description>` — bug fixes
- `docs/<short-description>` — documentation only
- `refactor/<short-description>` — code restructuring
- `test/<short-description>` — test additions

---

## 🔄 Pull Request Flow

1. **Create branch** from `main`
2. **Make changes** with tests
3. **Run checks** locally (see above)
4. **Push branch** and open PR against `main`
5. **Link issue** in PR description: `Fixes #123`
6. **Wait for CI** (GitHub Actions) to pass
7. **Address review feedback**
8. **Merge** (squash & merge preferred)

---

## 🏷️ Good First Issues

Look for issues labeled **`good first issue`** on the [issue tracker](https://github.com/mergeos-bounties/Loru/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). These are scoped for new contributors.

---

## 💰 MergeOS Bounties & Claim Flow

Loru is part of **MergeOS** — a bounty platform for open-source contributors.

### How to Claim a Bounty

1. **Star the repos**
   - ⭐ [mergeos-bounties/Loru](https://github.com/mergeos-bounties/Loru)
   - ⭐ [mergeos-bounties/mergeos](https://github.com/mergeos-bounties/mergeos)

2. **Comment on the bounty issue**: `I claim this bounty`

3. **Comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1)** with a link to the bounty issue

4. **Open a PR** to Loru with `Fixes #<bounty-issue-number>` in the description

### Payout

- Maintainer reviews PR → merges on Loru
- **MRG credit** issued on MergeOS ledger to `github:<author>`
- Bounty scale: 25 / 50 / 100 / 200 MRG

### Policy

See [docs/BOUNTY.md](docs/BOUNTY.md) for full bounty policy.

---

## 📚 Resources

- **README**: [README.md](README.md)
- **CLI Reference**: `loru --help`
- **GUI**: `loru-gui` (requires `[gui]` extras)
- **API**: `loru serve` (requires `[api]` extras)
- **MergeOS**: [mergeos-bounties/mergeos](https://github.com/mergeos-bounties/mergeos)

---

## 🤝 Code of Conduct

By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md) (or the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) if no file exists).

---

## ❓ Questions?

- Open a [Discussion](https://github.com/mergeos-bounties/Loru/discussions)
- Comment on the relevant issue
- Check existing [PRs](https://github.com/mergeos-bounties/Loru/pulls)

Thank you for contributing! 🙏
