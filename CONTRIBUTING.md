# Contributing to Loru

Thanks for helping improve Loru. This guide keeps local setup, testing, pull
requests, and MergeOS bounty claims consistent for contributors.

## Local Setup

Loru requires Python 3.11 or newer.

```powershell
git clone https://github.com/mergeos-bounties/Loru.git
cd Loru
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
```

Install optional extras only when you need them:

```powershell
pip install -e ".[gui]"    # Qt desktop app
pip install -e ".[api]"    # FastAPI integration
pip install -e ".[voice]"  # local TTS output
pip install -e ".[torch]"  # torch-backed model work
```

## Development Commands

Run the focused checks before opening a pull request:

```powershell
pytest -q
ruff check src tests
loru demo
```

For GUI changes, refresh screenshots when the visible UI changes:

```powershell
python scripts/capture_gui_shots.py
```

For CLI changes, include the exact `loru ...` command you used to verify the
behavior in your pull request description.

## Pull Request Checklist

- Keep each pull request focused on one bug, feature, data pack, or document.
- Link the issue with `Fixes #<issue-number>` when the work closes a bounty or
  bug report.
- Include the commands you ran locally and the result of each command.
- Update README or docs when setup, CLI behavior, screenshots, or bounty flow
  changes.
- Avoid committing virtual environments, caches, generated audio, or temporary
  output files.
- Use synthetic or consented sign-language samples only; do not add private
  recordings or identifying user data.

## MergeOS Bounty Claim Flow

For bounty issues marked with MergeOS rewards:

1. Star `mergeos-bounties/Loru`.
2. Star `mergeos-bounties/mergeos`.
3. Comment `I claim this bounty` on the Loru bounty issue before starting.
4. Comment on
   [MergeOS Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1)
   with a link to the bounty issue.
5. Open a pull request to Loru with `Fixes #<issue-number>`.
6. After maintainer review and merge, the reward is credited on the MergeOS
   ledger to `github:<your-github-username>`.

See [docs/BOUNTY.md](docs/BOUNTY.md) for the project bounty policy.
