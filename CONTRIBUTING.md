# Contributing to Loru

Thank you for your interest in improving Loru — an offline sign-language toolkit that turns landmark sequences into gloss/text and sign into voice.

## Getting Started

1. **Star** the upstream repos: [mergeos-bounties/Loru](https://github.com/mergeos-bounties/Loru) and [mergeos-bounties/mergeos](https://github.com/mergeos-bounties/mergeos).
2. **Fork** this repository on GitHub.
3. **Clone** your fork:
   ```powershell
   git clone https://github.com/YOUR_USERNAME/Loru.git
   cd Loru
   ```
4. **Set up a development environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -e ".[dev,gui]"
   ```

## Running Tests

```powershell
pytest -q
ruff check src tests
loru demo
```

## Good First Issues

Look for issues tagged `good-first-issue` in the [issue tracker](https://github.com/mergeos-bounties/Loru/issues). Suggested starting points:

- Adding new gloss samples or sign packs
- Improving CLI help text or error messages
- Adding tests for edge cases in `src/loru/infer/`
- Refreshing GUI screenshots with `scripts/capture_gui_shots.py`

## Development Workflow

1. Create a feature branch from `master`:
   ```powershell
   git checkout -b feat/my-feature
   ```
2. Make your changes.
3. Run linting and tests:
   ```powershell
   pytest -q
   ruff check src tests
   ```
4. Commit with a clear message:
   ```text
   feat: add goodbye gloss sample
   ```
5. Push to your fork and open a Pull Request against `master`.
6. Link any related issues in the PR description using `Closes #N` or `Fixes #N`.

## Code Style

- Follow PEP 8 conventions.
- Run `ruff check src tests` before committing.
- Write tests for new functionality.
- Keep the offline / no-GPU smoke path working.

## Pull Request Checklist

- [ ] Code follows project style (`ruff` passes)
- [ ] Tests added / updated for new functionality
- [ ] All existing tests pass (`pytest -q`)
- [ ] Documentation updated if needed
- [ ] PR description references related issues

## MergeOS Bounty Claim Flow

Some issues are rewarded in **MRG** credits by MergeOS:

1. Star [mergeos-bounties/Loru](https://github.com/mergeos-bounties/Loru) and [mergeos-bounties/mergeos](https://github.com/mergeos-bounties/mergeos).
2. Comment `I claim this bounty` on the issue you want to work on.
3. Comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with a link to the issue.
4. Open a PR to **mergeos-bounties/Loru** with `Fixes #<issue-number>`.
5. After the maintainer merges the PR, MRG credit is recorded on the MergeOS ledger for `github:<your-username>`.

See [docs/BOUNTY.md](docs/BOUNTY.md) for the full policy.

## Need Help?

Open a [Discussion](https://github.com/mergeos-bounties/Loru/discussions) or ask in the relevant issue.
