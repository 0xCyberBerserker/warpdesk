from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class WarpState:
    cli_available: bool = False
    daemon_reachable: bool = False
    connected: bool = False
    connecting: bool = False
    registered: bool = False
    account_type: str = "Unknown"
    organization: str = "Personal"
    mode: str = "warp+doh"
    protocol: str = "MASQUE"
    service_mode: str = "Unknown"
    status: str = "Unavailable"
    endpoint: str = ""
    support_url: str = ""
    device_name: str = ""
    registration_id: str = ""
    raw_status: str = ""
    error: str = ""
    diagnostics: list[str] = field(default_factory=list)

    @property
    def display_mode(self) -> str:
        mapping = {
            "warp": "WARP",
            "warp+doh": "WARP + DNS",
            "warp+dot": "WARP + DoT",
            "doh": "DNS over HTTPS",
            "dot": "DNS over TLS",
            "proxy": "Local Proxy",
            "tunnel_only": "Tunnel Only",
        }
        return mapping.get(self.mode, self.mode)

    @property
    def status_line(self) -> str:
        if self.error:
            return self.error
        if self.connecting:
            return "Connecting"
        return self.status or "Unknown"


@dataclass(slots=True)
class WarpProfile:
    name: str
    mode: str
    protocol: str

    @property
    def summary(self) -> str:
        return f"{self.mode} / {self.protocol}"
