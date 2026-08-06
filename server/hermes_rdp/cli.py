from __future__ import annotations

import argparse
import json
import os
import socket
import ssl
import sys
import time
import urllib.request

from .config import load_config
from .db import Registry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hermes-rdpctl")
    sub = parser.add_subparsers(dest="command", required=True)

    pair = sub.add_parser("pair", help="manage one-time pairing codes")
    pair_sub = pair.add_subparsers(dest="pair_command", required=True)
    pair_create = pair_sub.add_parser("create")
    pair_create.add_argument("--name")
    pair_create.add_argument("--port", type=int)
    pair_create.add_argument("--ttl", type=int, default=900)

    devices = sub.add_parser("devices")
    devices_sub = devices.add_subparsers(dest="devices_command", required=True)
    devices_sub.add_parser("list")
    device_delete = devices_sub.add_parser("delete")
    device_delete.add_argument("device_id")
    device_rename = devices_sub.add_parser("rename")
    device_rename.add_argument("device_id")
    device_rename.add_argument("name")

    dashboard = sub.add_parser("dashboard")
    dashboard_sub = dashboard.add_subparsers(dest="dashboard_command", required=True)
    dashboard_sub.add_parser("reset")

    sub.add_parser("doctor")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config()
    registry = Registry(config.db_path, config.port_start, config.port_end)

    if args.command == "pair" and args.pair_command == "create":
        code = registry.create_pair_code(
            display_name=args.name,
            preferred_port=args.port,
            ttl_seconds=args.ttl,
        )
        print(f"PAIR_CODE={code}")
        print(f"EXPIRES_IN={args.ttl}")
        print(f"SERVER={config.public_host}")
        print(f"FINGERPRINT={config.tls_fingerprint}")
        return

    if args.command == "devices" and args.devices_command == "list":
        for device in registry.list_devices():
            age = "never" if not device.get("last_seen") else str(int(time.time()) - int(device["last_seen"]))
            print(
                f"{device['id']}\t{device['display_name']}\t{device['machine_name']}\t"
                f"{device['rdp_port']}\tlast_seen={age}s"
            )
        return

    if args.command == "devices" and args.devices_command == "delete":
        registry.revoke_device(args.device_id)
        print("OK")
        return

    if args.command == "devices" and args.devices_command == "rename":
        registry.rename_device(args.device_id, args.name)
        print("OK")
        return

    if args.command == "dashboard" and args.dashboard_command == "reset":
        registry.set_setting("dashboard_message_id", "")
        registry.set_setting("screen", "home")
        registry.set_setting("selected_device", "")
        print("Dashboard state reset. Send /start to the bot.")
        return

    if args.command == "doctor":
        errors = 0
        print(f"config: OK ({config.public_host})")
        print(f"database: OK ({config.db_path})")
        try:
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(
                f"https://127.0.0.1:{config.api_port}/healthz",
                context=context,
                timeout=5,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
            print(f"api: OK ({payload.get('version')})")
        except Exception as exc:
            errors += 1
            print(f"api: FAIL ({exc})")
        for port, name in [
            (config.frp_bind_port, "frp-control"),
            (config.api_port, "api"),
        ]:
            sock = socket.socket()
            sock.settimeout(2)
            try:
                sock.connect(("127.0.0.1", port))
                print(f"{name}: LISTEN {port}")
            except OSError as exc:
                errors += 1
                print(f"{name}: FAIL {port} ({exc})")
            finally:
                sock.close()
        if errors:
            raise SystemExit(1)
        return


if __name__ == "__main__":
    main()
