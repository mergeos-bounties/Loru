# Contributing to Loru

Thank you for considering contributing to Loru! This document outlines the process for contributing to the project.

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/Loru.git
   cd Loru
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev,gui]"
   ```
4. Set up pre-commit hooks (optional but recommended):
   ```bash
   pre-commit install
   ```

## Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-or-fix-name
   ```
2. Make your changes, ensuring you follow the project's coding style.
3. Add or update tests as necessary.
4. Run the test suite to ensure everything passes:
   ```bash
   uv run pytest -q
   ```
5. If you changed the GUI, you may need to update screenshots:
   ```bash
   python scripts/capture_gui_shots.py
   ```

## Pull Request Process

1. Push your branch to your fork:
   ```bash
   git push origin feature-or-fix-name
   ```
2. Open a pull request against the `main` branch of the upstream repository.
3. Fill in the PR template with a clear description of your changes.
4. Ensure your PR includes:
   - A clear title and description.
   - References to any related issues (e.g., `Fixes #issue-number`).
   - Passing CI checks.
   - Updated documentation if applicable.
5. Wait for a maintainer to review your PR. Address any feedback promptly.
6. Once approved, your PR will be merged.

## Reporting Issues

Please use the GitHub issue tracker to report bugs or request features. When reporting a bug, include:
- A clear and descriptive title.
- Steps to reproduce the issue.
- Expected behavior vs. actual behavior.
- Any relevant screenshots or logs.
- Your environment (OS, Python version, etc.).

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

## License

By contributing to Loru, you agree that your contributions will be licensed under the MIT License.

## MergeOS Bounty Claim Process

If you are working on a MergeOS bounty issue, follow these steps to claim your reward:

1. Star the Loru and MergeOS repositories:
   - https://github.com/mergeos-bounties/Loru
   - https://github.com/mergeos-bounties/mergeos
2. Comment on the bounty issue: `I claim this bounty`
3. Comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to the bounty issue.
4. Open a PR to Loru with `Fixes #<issue-number>` in the PR description.
5. After the maintainer reviews and merges your PR, you will receive MRG credit on the MergeOS ledger.

Happy contributing!