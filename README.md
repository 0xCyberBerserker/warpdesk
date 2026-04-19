# WarpDesk

Desktop UI for Cloudflare WARP on Linux.

WarpDesk was built for fun and for the community. The idea is simple: there was no native-feeling, friendly Linux desktop experience for people who just want to manage WARP in two clicks without dropping to a terminal for a small everyday task.

Made with 🖤 in Barcelona City 🇪🇸

Languages:

- [English](README.md)
- [Español](README.es.md)
- [Català](README.ca.md)

![WarpDesk screenshot](docs/media/warpdesk-main.png)

## Why

The stock Linux WARP flow is functional, but not especially friendly if what you want is:

- a proper desktop window
- a tray entry with quick actions
- a compact view of connection state
- easy mode / protocol switching
- saved profiles
- no command memorization for routine usage

WarpDesk keeps `warp-cli` as the backend and focuses on a better desktop UX on top.

## Features

- Connect / disconnect from a native Qt window
- MASQUE / WireGuard switching
- WARP mode switching
- Saved profiles
- Diagnostics panel
- Tray icon with quick actions
- Desktop integration for launcher and menu entry
- Locale-aware UI for English, Spanish, and Catalan
- Theme-aware palette so it fits better into Linux desktops

## Screenshot

The screenshot above is generated from the app itself in offscreen mode and can be regenerated with:

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python3 scripts/generate_screenshot.py
```

## Requirements

- Linux desktop
- Python 3.11+
- PySide6
- Cloudflare WARP installed

Arch / CachyOS:

```bash
sudo pacman -S cloudflare-warp-bin
```

## Run from source

```bash
cd warpdesk
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
warpdesk
```

## Install as desktop app

This creates:

- `~/.local/bin/warpdesk`
- `~/.local/share/applications/io.warpdesk.app.desktop`
- `~/Escritorio/WarpDesk.desktop`
- `~/.local/share/icons/hicolor/scalable/apps/warpdesk-shield.svg`

Run:

```bash
cd warpdesk
./scripts/install_local.sh
```

## Public notes

- WarpDesk depends on `warp-cli` and `warp-svc`
- uninstalling `cloudflare-warp-bin` removes the backend WarpDesk talks to
- privileged service actions rely on `pkexec`

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Branding / Icons](docs/BRANDING.md)

## Roadmap

Roadmap items live as GitHub issues so progress stays visible and actionable.

## Contributions

If you want to contribute a translation for another language, open a pull request and I will be happy to review it and merge it if it fits the project. The same applies to feature ideas, UX improvements, packaging work, or any other useful contribution.
