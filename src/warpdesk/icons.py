from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap


ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"

ICON_CONNECTED = ASSET_DIR / "cloudflare-zero-trust-connected.svg"
ICON_DISCONNECTED = ASSET_DIR / "cloudflare-zero-trust-disconnected.svg"
ICON_ERROR = ASSET_DIR / "cloudflare-zero-trust-error.svg"
ICON_LAUNCHER = ASSET_DIR / "cloudflare-zero-trust-orange.svg"


def _icon_from(path: Path) -> QIcon:
    return QIcon(str(path))


def make_app_icon(connected: bool = False, warning: bool = False) -> QIcon:
    if warning and ICON_ERROR.exists():
        return _icon_from(ICON_ERROR)
    if connected and ICON_CONNECTED.exists():
        return _icon_from(ICON_CONNECTED)
    if ICON_DISCONNECTED.exists():
        return _icon_from(ICON_DISCONNECTED)
    if ICON_LAUNCHER.exists():
        return _icon_from(ICON_LAUNCHER)
    return QIcon()


def launcher_icon() -> QIcon:
    if ICON_LAUNCHER.exists():
        return _icon_from(ICON_LAUNCHER)
    return make_app_icon()


def launcher_pixmap(size: int = 28) -> QPixmap:
    icon = launcher_icon()
    return icon.pixmap(size, size)
