from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
import string
import time
import uuid
from pathlib import Path
from typing import Any


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS devices (
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

CREATE TABLE IF NOT EXISTS pair_codes (
    code_hash TEXT PRIMARY KEY,
    display_name TEXT,
    preferred_port INTEGER,
    expires_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    used_at INTEGER
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def now() -> int:
    return int(time.time())


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class Registry:
    def __init__(self, db_path: str | Path, port_start: int, port_end: int):
        self.db_path = Path(db_path)
        self.port_start = int(port_start)
        self.port_end = int(port_end)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return str(row["value"]) if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO settings(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def create_pair_code(
        self,
        *,
        display_name: str | None = None,
        preferred_port: int | None = None,
        ttl_seconds: int = 900,
    ) -> str:
        if preferred_port is not None:
            self._validate_port(preferred_port)
            if self.port_in_use(preferred_port):
                raise ValueError(f"port {preferred_port} is already assigned")
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        for _ in range(20):
            code = "".join(secrets.choice(alphabet) for _ in range(8))
            try:
                with self.connect() as conn:
                    conn.execute(
                        "INSERT INTO pair_codes(code_hash,display_name,preferred_port,expires_at,created_at) "
                        "VALUES(?,?,?,?,?)",
                        (
                            hash_secret(code),
                            display_name,
                            preferred_port,
                            now() + int(ttl_seconds),
                            now(),
                        ),
                    )
                return code
            except sqlite3.IntegrityError:
                continue
        raise RuntimeError("unable to allocate a unique pair code")

    def consume_pair_code(self, code: str) -> dict[str, Any]:
        code_hash = hash_secret(code.strip().upper())
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM pair_codes WHERE code_hash=?", (code_hash,)
            ).fetchone()
            if not row:
                raise ValueError("invalid pair code")
            if row["used_at"] is not None:
                raise ValueError("pair code was already used")
            if int(row["expires_at"]) < now():
                raise ValueError("pair code expired")
            conn.execute(
                "UPDATE pair_codes SET used_at=? WHERE code_hash=?", (now(), code_hash)
            )
        return dict(row)

    def _validate_port(self, port: int) -> None:
        if not self.port_start <= int(port) <= self.port_end:
            raise ValueError(
                f"port must be in range {self.port_start}-{self.port_end}"
            )

    def port_in_use(self, port: int) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM devices WHERE rdp_port=? AND revoked=0", (int(port),)
            ).fetchone()
        return bool(row)

    def allocate_port(self, preferred_port: int | None = None) -> int:
        if preferred_port is not None:
            self._validate_port(preferred_port)
            if self.port_in_use(preferred_port):
                raise ValueError(f"port {preferred_port} is already assigned")
            return int(preferred_port)
        with self.connect() as conn:
            used = {
                int(row["rdp_port"])
                for row in conn.execute(
                    "SELECT rdp_port FROM devices WHERE revoked=0"
                ).fetchall()
            }
        for port in range(self.port_start, self.port_end + 1):
            if port not in used:
                return port
        raise RuntimeError("no free RDP ports")

    def register_device(
        self,
        *,
        pair: dict[str, Any],
        display_name: str,
        machine_name: str,
        fingerprint: str,
    ) -> tuple[dict[str, Any], str]:
        device_id = uuid.uuid4().hex
        token = secrets.token_urlsafe(40)
        port = self.allocate_port(pair.get("preferred_port"))
        name = (pair.get("display_name") or display_name or machine_name).strip()
        name = name[:64] or machine_name[:64] or "Windows PC"
        machine_name = machine_name.strip()[:128] or "unknown"
        timestamp = now()
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO devices(id,display_name,machine_name,fingerprint,token_hash,rdp_port,"
                "created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                (
                    device_id,
                    name,
                    machine_name,
                    fingerprint[:256],
                    hash_secret(token),
                    port,
                    timestamp,
                    timestamp,
                ),
            )
        return self.get_device(device_id), token

    def authenticate(self, device_id: str, token: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM devices WHERE id=? AND revoked=0", (device_id,)
            ).fetchone()
        if not row or not secrets.compare_digest(str(row["token_hash"]), hash_secret(token)):
            return None
        return self._device_row(row)

    def _device_row(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key in ("enabled", "revoked"):
            data[key] = bool(data[key])
        if data.get("telemetry_json"):
            try:
                data["telemetry"] = json.loads(data["telemetry_json"])
            except json.JSONDecodeError:
                data["telemetry"] = None
        else:
            data["telemetry"] = None
        if data.get("last_result_json"):
            try:
                data["last_result"] = json.loads(data["last_result_json"])
            except json.JSONDecodeError:
                data["last_result"] = None
        else:
            data["last_result"] = None
        return data

    def list_devices(self, include_revoked: bool = False) -> list[dict[str, Any]]:
        where = "" if include_revoked else "WHERE revoked=0"
        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM devices {where} ORDER BY created_at, display_name"
            ).fetchall()
        return [self._device_row(row) for row in rows]

    def get_device(self, device_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM devices WHERE id=?", (device_id,)).fetchone()
        if not row:
            raise KeyError(device_id)
        return self._device_row(row)

    def update_telemetry(self, device_id: str, telemetry: dict[str, Any]) -> dict[str, Any]:
        timestamp = now()
        with self.connect() as conn:
            conn.execute(
                "UPDATE devices SET telemetry_json=?,last_seen=?,updated_at=? "
                "WHERE id=? AND revoked=0",
                (
                    json.dumps(telemetry, ensure_ascii=False, separators=(",", ":")),
                    timestamp,
                    timestamp,
                    device_id,
                ),
            )
        return self.pending_command(device_id)

    def queue_command(self, device_id: str, action: str) -> int:
        if action not in {"on", "off", "restart"}:
            raise ValueError("unsupported command")
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT command_seq FROM devices WHERE id=? AND revoked=0", (device_id,)
            ).fetchone()
            if not row:
                raise KeyError(device_id)
            seq = int(row["command_seq"]) + 1
            conn.execute(
                "UPDATE devices SET command_seq=?,pending_command=?,pending_created_at=?,updated_at=? "
                "WHERE id=?",
                (seq, action, now(), now(), device_id),
            )
        return seq

    def pending_command(self, device_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT command_seq,pending_command,pending_created_at FROM devices "
                "WHERE id=? AND revoked=0",
                (device_id,),
            ).fetchone()
        if not row or not row["pending_command"]:
            return None
        return {
            "seq": int(row["command_seq"]),
            "action": str(row["pending_command"]),
            "created_at": int(row["pending_created_at"] or 0),
        }

    def complete_command(
        self, device_id: str, seq: int, ok: bool, message: str
    ) -> None:
        result = {
            "seq": int(seq),
            "ok": bool(ok),
            "message": str(message)[:500],
            "completed_at": now(),
        }
        with self.connect() as conn:
            row = conn.execute(
                "SELECT command_seq FROM devices WHERE id=?", (device_id,)
            ).fetchone()
            if not row or int(row["command_seq"]) != int(seq):
                return
            conn.execute(
                "UPDATE devices SET pending_command=NULL,pending_created_at=NULL,"
                "last_result_json=?,updated_at=? WHERE id=?",
                (json.dumps(result, ensure_ascii=False), now(), device_id),
            )

    def rename_device(self, device_id: str, name: str) -> None:
        clean = name.strip()[:64]
        if not clean:
            raise ValueError("name is empty")
        with self.connect() as conn:
            conn.execute(
                "UPDATE devices SET display_name=?,updated_at=? WHERE id=? AND revoked=0",
                (clean, now(), device_id),
            )

    def revoke_device(self, device_id: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE devices SET revoked=1,pending_command=NULL,updated_at=? WHERE id=?",
                (now(), device_id),
            )

    def cleanup(self) -> None:
        cutoff = now() - 86400
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM pair_codes WHERE (expires_at<? OR used_at IS NOT NULL) AND created_at<?",
                (now(), cutoff),
            )
