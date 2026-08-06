#!/usr/bin/env python3
"""Reject public network addresses accidentally committed as examples."""

from __future__ import annotations

import ipaddress
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".ps1",
    ".sh",
    ".toml",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
    ".ini",
    ".cfg",
    ".service",
}
SPECIAL_NAMES = {"VERSION", "LICENSE"}
IPV4_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?:\d{1,3}\.){3}\d{1,3}(?![A-Za-z0-9_])"
)
IPV6_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![A-Za-z0-9_])"
)
DOCUMENTATION_NETWORKS = (
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("2001:db8::/32"),
)


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in SPECIAL_NAMES


def is_allowed(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        address.is_loopback
        or address.is_private
        or address.is_link_local
        or address.is_unspecified
        or address.is_multicast
        or any(address in network for network in DOCUMENTATION_NETWORKS)
    )


def scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return []

    failures: list[str] = []
    for pattern in (IPV4_PATTERN, IPV6_PATTERN):
        for match in pattern.finditer(text):
            value = match.group(0)
            try:
                address = ipaddress.ip_address(value)
            except ValueError:
                continue
            if is_allowed(address):
                continue
            line = text.count("\n", 0, match.start()) + 1
            failures.append(f"{path.relative_to(ROOT)}:{line}: public address {value}")
    return failures


def main() -> int:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or not is_text_candidate(path):
            continue
        failures.extend(scan_file(path))

    if failures:
        print("Public example privacy scan failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        print(
            "Replace real addresses with SERVER_IP_OR_DOMAIN, CLIENT_IP_ADDRESS, "
            "or an RFC documentation network.",
            file=sys.stderr,
        )
        return 1

    print("public-address-privacy=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
