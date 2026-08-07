from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WindowsNativeOpenSshTests(unittest.TestCase):
    def test_x86_powershell_uses_sysnative_probe(self) -> None:
        text = (ROOT / "scripts/install-client.ps1").read_text(encoding="utf-8-sig")
        for value in (
            "Is64BitOperatingSystem",
            "Is64BitProcess",
            "Sysnative",
            "$CanonicalSystem32",
            "$ProbeSshPath",
        ):
            self.assertIn(value, text)
        self.assertIn("ssh = $SshPath", text)
        self.assertIn("keygen = $KeygenPath", text)


if __name__ == "__main__":
    unittest.main()
