from __future__ import annotations

import subprocess
from pathlib import Path

from .config import Config


def _proc_net_has_listener(text: str, port: int) -> bool:
    target_port = f"{int(port):04X}"
    lines = text.splitlines()
    for line in lines[1:]:
        fields = line.split()
        if len(fields) < 4:
            continue
        local_address = fields[1]
        state = fields[3].upper()
        if ":" not in local_address:
            continue
        local_port = local_address.rsplit(":", 1)[1].upper()
        if state == "0A" and local_port == target_port:
            return True
    return False


def endpoint_listener_state(port: int) -> bool | None:
    """Return authoritative Linux listener state for a Hermes RDP port.

    The Windows client must not probe its own public endpoint because VPN/TUN
    routing or transparent proxies can make a closed server port look open.
    /proc/net/tcp* is local to the Linux server and does not create a test
    connection through the reverse tunnel.
    """

    observed_socket_table = False
    for path in (Path("/proc/net/tcp"), Path("/proc/net/tcp6")):
        try:
            text = path.read_text(encoding="ascii")
        except OSError:
            continue
        observed_socket_table = True
        if _proc_net_has_listener(text, port):
            return True
    if observed_socket_table:
        return False
    return None


def close_tunnel(config: Config, port: int) -> None:
    completed = subprocess.run(
        [
            "/usr/bin/sudo",
            "-n",
            str(config.close_tunnel_helper),
            str(int(port)),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if completed.returncode not in {0, 3}:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(detail or f"close tunnel failed: {completed.returncode}")
