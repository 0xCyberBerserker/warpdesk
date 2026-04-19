from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from warpdesk.models import WarpState
from warpdesk.profile_store import ProfileStore
from warpdesk.window import MainWindow


class MockWarpCli:
    def snapshot(self) -> WarpState:
        return WarpState(
            cli_available=True,
            daemon_reachable=True,
            connected=True,
            registered=True,
            account_type="Free",
            organization="Personal",
            mode="warp+doh",
            protocol="MASQUE",
            service_mode="WarpWithDnsOverHttps",
            status="Connected",
            endpoint="engage.cloudflareclient.com:2408",
            device_name="WarpDesk Demo",
            raw_status='{"status":"Connected"}',
        )

    def connect(self) -> str:
        return "Connected"

    def disconnect(self) -> str:
        return "Disconnected"

    def register(self) -> str:
        return "Registered"

    def set_mode(self, mode: str) -> str:
        return mode

    def set_protocol(self, protocol: str) -> str:
        return protocol

    def reset_protocol(self) -> str:
        return "Reset"

    def launch_privileged_service(self, action: str) -> None:
        return None


def main() -> int:
    app = QApplication([])
    window = MainWindow(MockWarpCli(), ProfileStore(path=Path("/tmp/warpdesk-profiles.json")))
    window.resize(1320, 860)
    window.show()
    QApplication.processEvents()
    output = Path(__file__).resolve().parents[1] / "docs" / "media" / "warpdesk-main.png"
    output.parent.mkdir(parents=True, exist_ok=True)

    def capture() -> None:
        window.grab().save(str(output))
        app.quit()

    QTimer.singleShot(600, capture)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
