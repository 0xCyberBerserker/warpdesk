from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from warpdesk.profile_store import ProfileStore
from warpdesk.warp_cli import WarpCli
from warpdesk.window import MainWindow


def main() -> int:
    app = QApplication([])
    window = MainWindow(WarpCli(), ProfileStore())
    window.show()
    QTimer.singleShot(1200, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
