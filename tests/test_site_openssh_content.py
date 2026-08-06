from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebsiteOpenSshContentTests(unittest.TestCase):
    def test_public_site_describes_current_architecture(self) -> None:
        text = (ROOT / "index.html").read_text(encoding="utf-8")

        for required in [
            "OpenSSH",
            "REAL-WORLD VALIDATION",
            "мобильные данные",
            "permitlisten",
            "Hermes RDP Agent",
        ]:
            self.assertIn(required, text)

        for stale in ["v1.0.7", "FRPC", "FRPS", "FRP-сервер"]:
            self.assertNotIn(stale, text)

    def test_documentation_has_real_acceptance_path(self) -> None:
        testing = (ROOT / "docs/TESTING_A_TO_Z.md").read_text(
            encoding="utf-8"
        )
        validated = (ROOT / "docs/VALIDATED_SCENARIOS.md").read_text(
            encoding="utf-8"
        )
        security = (ROOT / "docs/SECURITY.md").read_text(encoding="utf-8")

        self.assertIn("внешнего RDP", testing)
        self.assertIn("второй Windows-ПК", validated)
        self.assertIn("перезагрузки Windows", testing)
        self.assertIn("RDP boundary", security)

    def test_site_assets_are_linked(self) -> None:
        text = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('/assets/styles.css', text)
        self.assertIn('/assets/app.js', text)
        self.assertTrue((ROOT / "assets/styles.css").is_file())
        self.assertTrue((ROOT / "assets/app.js").is_file())


if __name__ == "__main__":
    unittest.main()
