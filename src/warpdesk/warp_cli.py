from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict
from typing import Any

from .models import WarpState


class WarpCli:
    def __init__(self, binary: str = "warp-cli") -> None:
        self.binary = binary

    def is_available(self) -> bool:
        return shutil.which(self.binary) is not None

    def run(self, *args: str, json_output: bool = False) -> subprocess.CompletedProcess[str]:
        command = [self.binary, "--accept-tos"]
        if json_output:
            command.append("--json")
        command.extend(args)
        return subprocess.run(command, capture_output=True, text=True, timeout=12)

    def _run_text(self, *args: str) -> str:
        result = self.run(*args)
        output = (result.stdout or result.stderr).strip()
        if result.returncode != 0:
            raise RuntimeError(output or f"warp-cli {' '.join(args)} failed")
        return output

    def _run_json(self, *args: str) -> dict[str, Any]:
        result = self.run(*args, json_output=True)
        output = (result.stdout or result.stderr).strip()
        if not output:
            raise RuntimeError("No output from warp-cli")
        data = json.loads(output)
        if result.returncode != 0:
            code = data.get("code")
            error = data.get("error") or data.get("message") or output
            if code:
                raise RuntimeError(f"{code}: {error}")
            raise RuntimeError(error)
        return data

    def snapshot(self) -> WarpState:
        state = WarpState(cli_available=self.is_available())
        if not state.cli_available:
            state.error = "warp-cli not found. Install cloudflare-warp-bin first."
            return state

        try:
            status_json = self._run_json("status")
            state.daemon_reachable = True
            self._parse_status_json(status_json, state)
        except Exception as exc:
            message = str(exc)
            state.error = message
            state.raw_status = message
            if "FailedToConnectToDaemon" in message or "Maybe the daemon is not running" in message:
                state.error = "WARP daemon not reachable. Start warp-svc first."
            return state

        for loader in (self._load_settings, self._load_registration):
            try:
                loader(state)
            except Exception as exc:
                state.diagnostics.append(str(exc))

        return state

    def connect(self) -> str:
        return self._run_text("connect")

    def disconnect(self) -> str:
        return self._run_text("disconnect")

    def register(self) -> str:
        return self._run_text("registration", "new")

    def delete_registration(self) -> str:
        return self._run_text("registration", "delete")

    def set_mode(self, mode: str) -> str:
        return self._run_text("mode", mode)

    def set_protocol(self, protocol: str) -> str:
        return self._run_text("tunnel", "protocol", "set", protocol)

    def reset_protocol(self) -> str:
        return self._run_text("tunnel", "protocol", "reset")

    def settings_list(self) -> str:
        return self._run_text("settings", "list")

    def stats(self) -> str:
        return self._run_text("stats")

    def launch_privileged_service(self, action: str) -> subprocess.Popen[str]:
        return subprocess.Popen(["pkexec", "systemctl", action, "warp-svc"])

    def _parse_status_json(self, data: dict[str, Any], state: WarpState) -> None:
        if "error" in data:
            raise RuntimeError(data["error"])

        payload = data.get("result", data)
        normalized = json.dumps(payload).lower()
        status = (
            payload.get("status")
            or payload.get("state")
            or payload.get("connection_status")
            or payload.get("message")
            or "Unknown"
        )
        state.status = str(status)
        state.raw_status = json.dumps(payload, indent=2)
        state.connected = "connected" in normalized and "disconnected" not in normalized
        state.connecting = "connect" in normalized and not state.connected and "disconnect" not in normalized
        endpoint = payload.get("endpoint")
        if isinstance(endpoint, dict):
            host = endpoint.get("host") or endpoint.get("address") or ""
            port = endpoint.get("port") or ""
            state.endpoint = f"{host}:{port}".strip(":")
        elif endpoint:
            state.endpoint = str(endpoint)

    def _load_settings(self, state: WarpState) -> None:
        text = self.settings_list()
        mapping = self._parse_key_values(text)
        state.mode = self._normalize_mode(mapping.get("service mode", state.mode), mapping.get("mode"))
        state.service_mode = mapping.get("service mode", state.service_mode)
        state.protocol = mapping.get("tunnel protocol", state.protocol)
        state.support_url = mapping.get("support url", "")

    def _load_registration(self, state: WarpState) -> None:
        text = self._run_text("registration", "show")
        mapping = self._parse_key_values(text)
        state.registered = True
        state.organization = (
            mapping.get("organization")
            or mapping.get("team name")
            or mapping.get("organization name")
            or "Personal"
        )
        state.account_type = mapping.get("account type", state.account_type)
        state.device_name = mapping.get("device name", "")
        state.registration_id = mapping.get("id", "")

    @staticmethod
    def _parse_key_values(text: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            values[key.strip().lower()] = value.strip()
        return values

    @staticmethod
    def _normalize_mode(service_mode: str | None, explicit_mode: str | None) -> str:
        if explicit_mode:
            return explicit_mode
        mapping = {
            "WarpWithDnsOverHttps": "warp+doh",
            "DnsOverHttps": "doh",
            "TunnelOnly": "tunnel_only",
            "WarpProxy": "proxy",
            "PostureOnly": "proxy",
        }
        if not service_mode:
            return "warp+doh"
        return mapping.get(service_mode, service_mode)

    @staticmethod
    def debug_dump(state: WarpState) -> str:
        return json.dumps(asdict(state), indent=2)
