from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG = Path("/etc/hermes-rdp/config.json")


@dataclass(frozen=True)
class Config:
    public_host: str
    api_port: int
    frp_bind_port: int
    port_start: int
    port_end: int
    data_dir: Path
    db_path: Path
    telegram_token_file: Path
    telegram_chat_id: str
    tls_cert_file: Path
    tls_key_file: Path
    tls_fingerprint_file: Path
    frp_token_file: Path
    frp_ca_file: Path
    client_installer_url: str
    online_after_seconds: int = 15
    pair_ttl_seconds: int = 900

    @property
    def api_base_url(self) -> str:
        return f"https://{self.public_host}:{self.api_port}"

    def read_secret(self, path: Path) -> str:
        return path.read_text(encoding="utf-8").strip()

    @property
    def telegram_token(self) -> str:
        return self.read_secret(self.telegram_token_file)

    @property
    def frp_token(self) -> str:
        return self.read_secret(self.frp_token_file)

    @property
    def tls_fingerprint(self) -> str:
        return self.read_secret(self.tls_fingerprint_file).upper()


def load_config(path: str | Path = DEFAULT_CONFIG) -> Config:
    config_path = Path(path)
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data_dir = Path(data.get("data_dir", "/var/lib/hermes-rdp"))
    return Config(
        public_host=str(data["public_host"]),
        api_port=int(data.get("api_port", 7443)),
        frp_bind_port=int(data.get("frp_bind_port", 7000)),
        port_start=int(data.get("port_start", 53389)),
        port_end=int(data.get("port_end", 53420)),
        data_dir=data_dir,
        db_path=Path(data.get("db_path", data_dir / "state.sqlite3")),
        telegram_token_file=Path(
            data.get("telegram_token_file", "/etc/hermes-rdp/telegram-token")
        ),
        telegram_chat_id=str(data["telegram_chat_id"]),
        tls_cert_file=Path(data.get("tls_cert_file", "/etc/hermes-rdp/tls/api.crt")),
        tls_key_file=Path(data.get("tls_key_file", "/etc/hermes-rdp/tls/api.key")),
        tls_fingerprint_file=Path(
            data.get("tls_fingerprint_file", "/etc/hermes-rdp/tls/api.sha256")
        ),
        frp_token_file=Path(data.get("frp_token_file", "/etc/hermes-rdp/frp-token")),
        frp_ca_file=Path(data.get("frp_ca_file", "/etc/hermes-rdp/frp-ca.crt")),
        client_installer_url=str(
            data.get(
                "client_installer_url",
                "https://raw.githubusercontent.com/bakunity/RDP/main/scripts/install-client.ps1",
            )
        ),
        online_after_seconds=int(data.get("online_after_seconds", 15)),
        pair_ttl_seconds=int(data.get("pair_ttl_seconds", 900)),
    )
