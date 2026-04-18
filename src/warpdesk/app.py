from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .profile_store import ProfileStore
from .warp_cli import WarpCli
from .window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("WarpDesk")
    app.setApplicationDisplayName("WarpDesk")
    app.setDesktopFileName("io.warpdesk.app")
    app.setOrganizationName("WarpDesk")
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow(WarpCli(), ProfileStore())
    window.show()
    return app.exec()
