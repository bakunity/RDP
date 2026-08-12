from __future__ import annotations

import base64
import json
import socket
import ssl
import struct
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path

from hermes_rdp.api import create_api_server
from hermes_rdp.config import Config
from hermes_rdp.db import Registry, now


ROOT = Path(__file__).resolve().parents[1]


def ed25519_key(seed: int = 41) -> str:
    algorithm = b"ssh-ed25519"
    key = bytes([seed]) * 32
    blob = (
        struct.pack(">I", len(algorithm))
        + algorithm
        + struct.pack(">I", len(key))
        + key
    )
    return "ssh-ed25519 " + base64.b64encode(blob).decode("ascii")


class SoakStabilizationTests(unittest.TestCase):
    def test_slow_tls_client_cannot_block_api_accept_loop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            cert = temp / "api.crt"
            key = temp / "api.key"
            fingerprint = temp / "api.sha256"
            telegram_token = temp / "telegram-token"
            ssh_host_key = temp / "ssh-host-key.pub"

            subprocess.run(
                [
                    "openssl",
                    "req",
                    "-x509",
                    "-newkey",
                    "rsa:2048",
                    "-nodes",
                    "-days",
                    "1",
                    "-subj",
                    "/CN=localhost",
                    "-keyout",
                    str(key),
                    "-out",
                    str(cert),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
            )
            fingerprint.write_text("AA" * 32, encoding="utf-8")
            telegram_token.write_text("test", encoding="utf-8")
            ssh_host_key.write_text("ssh-ed25519 TEST\n", encoding="utf-8")

            config = Config(
                public_host="127.0.0.1",
                api_port=0,
                ssh_bind_port=7000,
                ssh_user="hermes-tunnel",
                port_start=53389,
                port_end=53420,
                data_dir=temp,
                db_path=temp / "state.sqlite3",
                telegram_token_file=telegram_token,
                telegram_chat_id="1",
                tls_cert_file=cert,
                tls_key_file=key,
                tls_fingerprint_file=fingerprint,
                ssh_host_key_file=ssh_host_key,
                client_installer_url="https://example.invalid/install-client.ps1",
                repository_ref="test",
                close_tunnel_helper=temp / "close-tunnel",
            )
            registry = Registry(
                config.db_path,
                config.port_start,
                config.port_end,
                config.command_timeout_seconds,
            )
            server = create_api_server(config, registry)
            server.tls_handshake_timeout_seconds = 0.5
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            port = int(server.server_address[1])

            slow = socket.create_connection(("127.0.0.1", port), timeout=1)
            try:
                # Leave the first TCP client silent in the TLS handshake. The
                # second client must still be accepted and served immediately.
                time.sleep(0.1)
                context = ssl._create_unverified_context()
                with urllib.request.urlopen(
                    f"https://127.0.0.1:{port}/healthz",
                    context=context,
                    timeout=2,
                ) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["service"], "hermes-rdp")
            finally:
                slow.close()
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_command_timeout_preserves_desired_state_and_clears_pending(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            registry = Registry(
                Path(temp_name) / "state.sqlite3",
                53389,
                53391,
                command_timeout_seconds=60,
            )
            code = registry.create_pair_code()
            device, _ = registry.pair_device(
                code=code,
                display_name="PC",
                machine_name="PC",
                fingerprint="machine",
                ssh_public_key=ed25519_key(),
            )
            device_id = device["id"]
            seq = registry.queue_command(device_id, "off")

            with registry.connect() as conn:
                conn.execute(
                    "UPDATE devices SET pending_created_at=? WHERE id=?",
                    (now() - 120, device_id),
                )

            expired = registry.expire_stale_commands(60, device_id=device_id)
            self.assertEqual(expired, 1)
            after = registry.get_device(device_id)
            self.assertFalse(after["enabled"])
            self.assertIsNone(after["pending_command"])
            self.assertEqual(after["command_seq"], seq)
            self.assertFalse(after["last_result"]["ok"])
            self.assertEqual(after["last_result"]["status"], "timeout")
            self.assertEqual(after["last_result"]["action"], "off")
            self.assertIn("целевое состояние сохранено", after["last_result"]["message"])

            # A timed-out execution slot must not lock the device forever.
            next_seq = registry.queue_command(device_id, "on")
            self.assertGreater(next_seq, seq)
            self.assertTrue(registry.get_device(device_id)["enabled"])

    def test_agent_polls_control_before_attempting_transport_recovery(self) -> None:
        text = (ROOT / "client/HermesRdpAgent.ps1").read_text(encoding="utf-8-sig")
        loop = text[text.index("while ($true)") :]
        post_index = loop.index("$Response = Invoke-ApiPost")
        transport_index = loop.index(
            "if ($State.enabled -and $SshProcesses.Count -eq 0)"
        )
        self.assertLess(post_index, transport_index)
        self.assertIn("desired_enabled", loop)
        self.assertIn("Control poll error:", loop)
        self.assertIn("Transport reconcile error:", loop)

        startup = text[text.index("$Config = Read-JsonFile") : text.index("while ($true)")]
        self.assertNotIn("[void](Start-SshTunnel)", startup)

    def test_command_state_is_persisted_before_transport_action(self) -> None:
        text = (ROOT / "client/HermesRdpAgent.ps1").read_text(encoding="utf-8-sig")
        start = text.index("function Invoke-CommandAction")
        end = text.index("if (-not (Test-Path -LiteralPath $ConfigPath))", start)
        block = text[start:end]
        persist_index = block.index("Write-JsonFile -Path $StatePath -Value $State")
        start_index = block.index("$Message = Start-SshTunnel")
        stop_index = block.index("$Message = Stop-SshTunnel")
        restart_index = block.index("$Message = Restart-SshTunnel")
        self.assertLess(persist_index, start_index)
        self.assertLess(persist_index, stop_index)
        self.assertLess(persist_index, restart_index)

    def test_api_returns_durable_desired_state(self) -> None:
        text = (ROOT / "server/hermes_rdp/api.py").read_text(encoding="utf-8")
        self.assertIn('"desired_enabled": bool(current["enabled"])', text)
        self.assertNotIn(
            "server.socket = context.wrap_socket(server.socket, server_side=True)",
            text,
        )
        self.assertIn("process_request_thread", text)
        self.assertIn("tls_handshake_timeout_seconds", text)


if __name__ == "__main__":
    unittest.main()
