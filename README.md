# WarpDesk

WarpDesk is a Qt desktop frontend for Cloudflare WARP on Linux.

This project was built for fun and for the community.

The reason is simple: on Linux there was no native-feeling, friendly way to manage this without dropping to a terminal. WarpDesk exists for people who do not want to launch commands for a small day-to-day task and would rather manage WARP in two clicks from a proper desktop app.

Made with 🖤 in Barcelona City 🇪🇸

It uses `warp-cli` as the backend and adds:

- a desktop window that is easier to use than the stock Linux client
- tray actions
- mode and protocol switching
- persistent profiles
- local menu / desktop integration
- locale-aware UI for English, Spanish, and Catalan

## Status

Current scope:

- `connect` / `disconnect`
- WARP mode switching
- MASQUE / WireGuard switching
- profile save/apply/delete
- daemon state visibility
- registration action
- diagnostics panel
- tray icon and menu

Current backend constraint:

- WarpDesk depends on `warp-cli` and `warp-svc`
- if you uninstall `cloudflare-warp-bin`, WarpDesk loses its backend

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

Without installing editable:

```bash
cd warpdesk
PYTHONPATH=src python3 -m warpdesk
```

## Install as desktop app

This creates:

- `~/.local/bin/warpdesk`
- `~/.local/share/applications/io.warpdesk.app.desktop`
- `~/Escritorio/WarpDesk.desktop`
- `~/.local/share/icons/hicolor/scalable/apps/warpdesk.svg`

Run:

```bash
cd warpdesk
./scripts/install_local.sh
```

## Repository layout

- `src/warpdesk/app.py`: Qt app bootstrap
- `src/warpdesk/window.py`: main window and tray integration
- `src/warpdesk/warp_cli.py`: `warp-cli` wrapper
- `src/warpdesk/profile_store.py`: saved profiles
- `src/warpdesk/i18n.py`: locale-aware strings
- `src/warpdesk/theme.py`: palette-driven Plasma-like styling
- `assets/`: launcher and tray icon assets
- `scripts/install_local.sh`: local desktop installation

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Development](docs/DEVELOPMENT.md)
- [Localization](docs/LOCALIZATION.md)
- [Branding / Icons](docs/BRANDING.md)

## Notes

- Privileged service actions use `pkexec`
- the app respects the system theme better by relying on `QPalette`
- locale resolution prioritizes real system locales and ignores neutral `C` / `POSIX`
- the custom WarpDesk shield icon is used for launcher / menu branding
- Cloudflare state icons are still kept for connection-status signaling inside the app
