# Contributing to WarpDesk

WarpDesk is intentionally small and intended to be community-friendly.

If you want to help, the most useful contribution areas are:

- translations
- packaging
- desktop integration fixes
- backend parsing and error handling
- UI polish
- CI and release automation

## Project status

WarpDesk should be treated as community-maintained.

The goal is to keep the project useful and easy to inherit, not to make maintenance depend on a single person.

## Development setup

```bash
git clone https://github.com/0xCyberBerserker/warpdesk.git
cd warpdesk
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install ruff
warpdesk
```

## Validation

Run lint:

```bash
ruff check src scripts
```

Run a quick smoke test:

```bash
QT_QPA_PLATFORM=offscreen python scripts/smoke_run.py
```

Regenerate the public screenshot if needed:

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python3 scripts/generate_screenshot.py
```

## Translations

Current public languages:

- English
- Spanish
- Catalan

If you want to add another language:

1. open a pull request
2. keep wording concise and native-sounding
3. update both the app UI and any public-facing documentation or Pages content affected by the change

## Pull requests

Please keep pull requests focused.

Good examples:

- one language addition
- one packaging target
- one UI improvement
- one backend parsing fix

Avoid mixing unrelated changes in the same PR.

## Maintainers wanted

If you want to help maintain the project long term, open a PR first or start by handling issues in one area such as:

- translations
- AUR / Flatpak
- CI
- Qt UI

Sustained contributors can be considered for a larger maintenance role over time.
