# Development

## Setup

```bash
cd warpdesk
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

```bash
warpdesk
```

or:

```bash
PYTHONPATH=src python3 -m warpdesk
```

## Useful checks

Compile all Python files:

```bash
python3 -m compileall src
```

Headless smoke run:

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python3 -m warpdesk
```

## Desktop reinstall

If you change launchers or icons:

```bash
./scripts/install_local.sh
```

## Packaging note

The repo is currently optimized for local editable installs.

If you publish it, the next sensible steps are:

- add screenshots
- add a license file
- add CI
- define a release packaging target
