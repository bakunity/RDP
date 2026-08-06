from __future__ import annotations

import subprocess

from .config import Config


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
