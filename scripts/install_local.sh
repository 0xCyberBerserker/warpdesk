#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_ID="io.warpdesk.app"
APP_NAME="WarpDesk"
LOCAL_BIN="${HOME}/.local/bin"
LOCAL_SHARE="${XDG_DATA_HOME:-$HOME/.local/share}"
APP_DIR="${LOCAL_SHARE}/applications"
ICON_DIR="${LOCAL_SHARE}/icons/hicolor/scalable/apps"
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || printf '%s/Escritorio' "$HOME")"
LAUNCHER_PATH="${LOCAL_BIN}/warpdesk"
DESKTOP_FILE="${APP_DIR}/${APP_ID}.desktop"
DESKTOP_SHORTCUT="${DESKTOP_DIR}/${APP_NAME}.desktop"
ICON_PATH="${ICON_DIR}/warpdesk-shield.svg"

mkdir -p "$LOCAL_BIN" "$APP_DIR" "$ICON_DIR" "$DESKTOP_DIR"

if [[ ! -d "${REPO_DIR}/.venv" ]]; then
  python3 -m venv "${REPO_DIR}/.venv"
fi

"${REPO_DIR}/.venv/bin/pip" install --upgrade pip >/dev/null
"${REPO_DIR}/.venv/bin/pip" install -e "$REPO_DIR"

install -m 755 "${REPO_DIR}/scripts/warpdesk-launch" "$LAUNCHER_PATH"
install -m 644 "${REPO_DIR}/assets/warpdesk-shield.svg" "$ICON_PATH"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${APP_NAME}
Comment=Desktop client for Cloudflare WARP on Linux
Exec=${LAUNCHER_PATH}
Icon=${ICON_PATH}
Terminal=false
Categories=Network;Security;Utility;
StartupNotify=true
StartupWMClass=WarpDesk
X-GNOME-UsesNotifications=true
EOF

cp "$DESKTOP_FILE" "$DESKTOP_SHORTCUT"
chmod +x "$DESKTOP_SHORTCUT"

update-desktop-database "$APP_DIR" >/dev/null 2>&1 || true
gtk-update-icon-cache "$LOCAL_SHARE/icons/hicolor" >/dev/null 2>&1 || true

printf 'Installed launcher: %s\n' "$LAUNCHER_PATH"
printf 'Installed desktop entry: %s\n' "$DESKTOP_FILE"
printf 'Installed desktop shortcut: %s\n' "$DESKTOP_SHORTCUT"
