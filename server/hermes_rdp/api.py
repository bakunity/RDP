from __future__ import annotations

import json
import logging
import ssl
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from . import __version__
from .config import Config
from .db import Registry
from .tunnel import close_tunnel, endpoint_listener_state


LOG = logging.getLogger("hermes_rdp.api")
MAX_BODY = 128 * 1024


class ApiServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], config: Config, registry: Registry):
        self.config = config
        self.registry = registry
        super().__init__(address, ApiHandler)


class ApiHandler(BaseHTTPRequestHandler):
    server: ApiServer
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        LOG.info("%s - %s", self.address_string(), fmt % args)

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > MAX_BODY:
            raise ValueError("invalid request body size")
        raw = self.rfile.read(length)
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON object required")
        return data

    def _bearer(self) -> str:
        value = self.headers.get("Authorization", "")
        if not value.startswith("Bearer "):
            return ""
        return value[7:].strip()

    def _device_auth(self, device_id: str) -> dict[str, Any] | None:
        return self.server.registry.authenticate(device_id, self._bearer())

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/healthz":
            self._json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "service": "hermes-rdp",
                    "version": __version__,
                    "fingerprint": self.server.config.tls_fingerprint,
                    "tunnel": "openssh",
                    "ssh_port": self.server.config.ssh_bind_port,
                },
            )
            return
        self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/v1/pair":
                self._pair()
                return
            parts = [part for part in path.split("/") if part]
            if len(parts) == 4 and parts[:2] == ["v1", "devices"]:
                device_id, action = parts[2], parts[3]
                if action == "telemetry":
                    self._telemetry(device_id)
                    return
                if action == "command-result":
                    self._command_result(device_id)
                    return
                if action == "revoke-self":
                    self._revoke_self(device_id)
                    return
            self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})
        except json.JSONDecodeError:
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid JSON"})
        except ValueError as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
        except Exception:
            LOG.exception("request failed")
            self._json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"ok": False, "error": "internal server error"},
            )

    def _pair(self) -> None:
        body = self._read_json()
        code = str(body.get("code", "")).strip().upper()
        if len(code) != 8:
            raise ValueError("invalid pair code")
        # Validate/read server identity before consuming the one-time code.
        ssh_host_key = self.server.config.ssh_host_key
        device, device_token = self.server.registry.pair_device(
            code=code,
            display_name=str(body.get("display_name", "")),
            machine_name=str(body.get("machine_name", "")),
            fingerprint=str(body.get("fingerprint", "")),
            ssh_public_key=str(body.get("ssh_public_key", "")),
        )
        self._json(
            HTTPStatus.CREATED,
            {
                "ok": True,
                "device": {
                    "id": device["id"],
                    "name": device["display_name"],
                    "rdp_port": device["rdp_port"],
                    "token": device_token,
                },
                "api": {
                    "base_url": self.server.config.api_base_url,
                    "fingerprint": self.server.config.tls_fingerprint,
                },
                "ssh": {
                    "host": self.server.config.public_host,
                    "port": self.server.config.ssh_bind_port,
                    "user": self.server.config.ssh_user,
                    "host_key": ssh_host_key,
                    "remote_bind": "0.0.0.0",
                },
            },
        )

    def _telemetry(self, device_id: str) -> None:
        device = self._device_auth(device_id)
        if not device:
            self._json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
            return
        body = self._read_json()
        telemetry = body.get("telemetry")
        if not isinstance(telemetry, dict):
            raise ValueError("telemetry object required")

        # Endpoint truth belongs to the Linux server. A Windows-side TCP probe
        # can be a false positive behind VPN/TUN/proxy routing, so never trust
        # the client value for the public Hermes listener.
        telemetry = dict(telemetry)
        endpoint_state = endpoint_listener_state(int(device["rdp_port"]))
        if endpoint_state is None:
            telemetry.pop("endpoint_available", None)
            telemetry["endpoint_source"] = "unknown"
        else:
            telemetry["endpoint_available"] = endpoint_state
            telemetry["endpoint_source"] = "server_listener"

        command = self.server.registry.update_telemetry(device_id, telemetry)
        self._json(HTTPStatus.OK, {"ok": True, "command": command})

    def _command_result(self, device_id: str) -> None:
        if not self._device_auth(device_id):
            self._json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
            return
        body = self._read_json()
        self.server.registry.complete_command(
            device_id,
            int(body.get("seq", 0)),
            bool(body.get("ok", False)),
            str(body.get("message", "")),
        )
        self._json(HTTPStatus.OK, {"ok": True})

    def _revoke_self(self, device_id: str) -> None:
        device = self._device_auth(device_id)
        if not device:
            self._json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
            return
        self.server.registry.revoke_device(device_id)
        try:
            close_tunnel(self.server.config, int(device["rdp_port"]))
        except Exception as exc:
            LOG.warning("self-revoke tunnel close failed: %s", exc)
        self._json(HTTPStatus.OK, {"ok": True})


def create_api_server(config: Config, registry: Registry) -> ApiServer:
    server = ApiServer(("0.0.0.0", config.api_port), config, registry)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(config.tls_cert_file, config.tls_key_file)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    return server
