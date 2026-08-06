from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ServerUpdateBehaviorTests(unittest.TestCase):
    def test_install_server_restarts_active_services(self) -> None:
        text = (ROOT / "scripts/install-server.sh").read_text(encoding="utf-8")
        self.assertIn("systemctl enable frps.service hermes-rdp.service", text)
        self.assertIn("systemctl restart frps.service hermes-rdp.service", text)
        self.assertNotIn("systemctl enable --now frps.service hermes-rdp.service", text)

    def test_update_server_accepts_branch_or_tag_ref(self) -> None:
        text = (ROOT / "scripts/update-server.sh").read_text(encoding="utf-8")
        self.assertIn("https://codeload.github.com/$REPO/tar.gz/$REF", text)
        self.assertNotIn("archive/refs/heads/$REF.tar.gz", text)
        self.assertIn("systemctl restart hermes-rdp.service", text)


if __name__ == "__main__":
    unittest.main()
