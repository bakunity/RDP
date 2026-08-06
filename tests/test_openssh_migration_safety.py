from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from hermes_rdp.db import Registry


ROOT = Path(__file__).resolve().parents[1]


class OpenSshMigrationSafetyTests(unittest.TestCase):
    def test_legacy_database_adds_ssh_columns_before_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "state.sqlite3"
            with sqlite3.connect(database) as connection:
                connection.executescript(
                    """
                    CREATE TABLE devices (
                        id TEXT PRIMARY KEY,
                        display_name TEXT NOT NULL,
                        machine_name TEXT NOT NULL,
                        fingerprint TEXT NOT NULL,
                        token_hash TEXT NOT NULL,
                        rdp_port INTEGER NOT NULL UNIQUE,
                        enabled INTEGER NOT NULL DEFAULT 1,
                        revoked INTEGER NOT NULL DEFAULT 0,
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        last_seen INTEGER,
                        telemetry_json TEXT,
                        command_seq INTEGER NOT NULL DEFAULT 0,
                        pending_command TEXT,
                        pending_created_at INTEGER,
                        last_result_json TEXT
                    );
                    CREATE TABLE pair_codes (
                        code_hash TEXT PRIMARY KEY,
                        display_name TEXT,
                        preferred_port INTEGER,
                        expires_at INTEGER NOT NULL,
                        created_at INTEGER NOT NULL,
                        used_at INTEGER
                    );
                    CREATE TABLE settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                    """
                )
            registry = Registry(database, 53389, 53420)
            with registry.connect() as connection:
                columns = {
                    row["name"]
                    for row in connection.execute(
                        "PRAGMA table_info(devices)"
                    ).fetchall()
                }
                indexes = {
                    row["name"]
                    for row in connection.execute(
                        "PRAGMA index_list(devices)"
                    ).fetchall()
                }
            self.assertIn("ssh_key_type", columns)
            self.assertIn("ssh_public_key", columns)
            self.assertIn("idx_devices_active_ssh_key", indexes)

    def test_windows_key_generation_preserves_empty_passphrase_argument(self) -> None:
        installer = (ROOT / "scripts/install-client.ps1").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("Start-Process", installer)
        self.assertIn("'-N'", installer)
        self.assertIn("'\"\"'", installer)
        self.assertNotIn("-N ''", installer)

    def test_tunnel_close_helper_matches_sshd_executable(self) -> None:
        installer = (ROOT / "scripts/install-server.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn('readlink -f "/proc/$PID/exe"', installer)
        self.assertIn('"$EXE" == /usr/sbin/sshd', installer)
        self.assertNotIn('COMMAND="$(tr', installer)


if __name__ == "__main__":
    unittest.main()
