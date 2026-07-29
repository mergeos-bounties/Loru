# Contributing to Loru

Thank you for considering contributing to **Loru**! We welcome bug reports, feature requests, documentation improvements, and pull requests from community members and bounty hunters alike.

---

## 🚩 Good First Issues & MergeOS Bounties

We use **MergeOS** to manage open-source bounties (`MRG`). If you are looking for a `good-first-issue` or wish to claim an active bounty, follow the official claim process below:

### Claiming a Bounty (MergeOS MRG Flow)

1. **Star the Repositories**:
   - [Loru Repository](https://github.com/mergeos-bounties/Loru)
   - [MergeOS Repository](https://github.com/mergeos-bounties/mergeos)

2. **Reserve / Claim the Issue**:
   - Browse open issues with the `good-first-issue` or `bounty` label.
   - Comment on the issue following the MergeOS claim command syntax (e.g., `/claim`) or link your MergeOS account on the platform to lock in your claim.

3. **Submit & Receive Rewards**:
   - Submit your PR referencing the exact issue (e.g., `Fixes #19`).
   - Once your pull request is reviewed, approved, and merged into `master`, your MergeOS MRG token reward will automatically trigger.

---

## 🛠️ Development Setup

Before installing dependencies, inspect the repository root to verify the environment.

### Standard Python Environment Setup

1. **Fork and Clone the Repository**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Loru.git
   cd Loru
   ```

2. **Add Upstream Remote**:
   ```bash
   git remote add upstream https://github.com/mergeos-bounties/Loru.git
   ```

3. **Create & Activate Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -e ".[dev,gui]"
   ```

---

## 🧪 Running Tests & Quality Checks

Always ensure local tests and linters pass cleanly before opening a pull request:

```bash
# Execute unit test suite
pytest -q

# Linting & Formatting checks
ruff check src tests

# Verify CLI & Demo path
loru version
loru demo
```

---

## 📋 Pull Request Checklist

When submitting a PR, please confirm that your submission hits all of the following requirements:

- [ ] **Branch Naming**: Created a descriptive topic branch off `master` (e.g., `fix/issue-19-contributing`).
- [ ] **Tests**: Added or updated test coverage for new functionality or fixed bugs.
- [ ] **CI Pass**: Local linting (`ruff`), type checks, and tests (`pytest`) pass cleanly without errors.
- [ ] **Documentation**: Updated `README.md`, docstrings, or user guides if public APIs or behaviors changed.
- [ ] **Commit Hygiene**: Clear, concise commit messages adhering to standard conventions.
- [ ] **Issue Linking**: The PR description includes `Fixes #<issue-number>` to link the relevant GitHub/MergeOS issue.

---

## 💬 Support & Community

If you need help setting up your environment or clarifying requirements:
- Open an issue or discussion topic in the [GitHub Issues](https://github.com/mergeos-bounties/Loru/issues) tracker.
- Connect with maintainers via MergeOS platform channels.

Thank you for helping make Loru better! 🚀
