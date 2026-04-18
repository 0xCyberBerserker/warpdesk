from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .i18n import I18N
from .models import WarpProfile


class ProfileStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (Path.home() / ".config" / "warpdesk" / "profiles.json")
        self.i18n = I18N()

    def _default_profiles(self) -> list[WarpProfile]:
        return [
            WarpProfile(name=self.i18n.t("secure_default"), mode="warp+doh", protocol="MASQUE"),
            WarpProfile(name=self.i18n.t("compat_mode"), mode="warp+doh", protocol="WireGuard"),
            WarpProfile(name=self.i18n.t("dns_only"), mode="doh", protocol="MASQUE"),
        ]

    def load(self) -> list[WarpProfile]:
        if not self.path.exists():
            return self._default_profiles()

        try:
            data = json.loads(self.path.read_text())
        except Exception:
            return self._default_profiles()

        profiles: list[WarpProfile] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            mode = str(item.get("mode", "")).strip()
            protocol = str(item.get("protocol", "")).strip()
            if not name or not mode or not protocol:
                continue
            profiles.append(WarpProfile(name=name, mode=mode, protocol=protocol))

        return profiles or self._default_profiles()

    def save(self, profiles: list[WarpProfile]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(profile) for profile in profiles]
        self.path.write_text(json.dumps(payload, indent=2) + "\n")
