# Contributing to Loru

Thanks for helping improve Loru! This guide covers how to get set up, find a
good first issue, and open a pull request that gets merged quickly.

## Getting started

1. **Star the repo** — helps the project surface to more contributors.
   - https://github.com/mergeos-bounties/Loru
   - https://github.com/mergeos-bounties/mergeos
2. Fork the repo and clone your fork.
3. Create a branch named `issue/NNN-short-description` (e.g. `issue/19-contributing`).

## Good first issues

Look for the `good first issue` label in the issue tracker. These are scoped,
well-described tasks ideal for new contributors. When you pick one up, comment
on the issue so maintainers can assign it and avoid duplicate work.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"   # or: pip install -r requirements.txt
```

- Run the test suite: `pytest`
- Format/lint before pushing: `ruff format . && ruff check .`

## Pull request checklist

- [ ] Branch is up to date with `main`.
- [ ] Changes are focused on a single issue (reference it with `Closes #NNN`).
- [ ] Tests pass locally (`pytest`).
- [ ] Code is formatted (`ruff format .`).
- [ ] PR description explains *what* and *why*.

## Code style

- Python: PEP 8, type hints where practical, descriptive names.
- Keep functions small and single-purpose.
- Add a test for any behavior change.

## Bounty / reward

Issues labeled `bounty` or `reward:*` are eligible for MergeOS (MRG) payouts.
Follow the claim steps in the issue (usually: star both repos, open the PR,
comment your wallet/claim details). Maintainers review and release rewards on merge.

## Questions

Open a Discussion or comment on the relevant issue — maintainers and contributors
are happy to help.
