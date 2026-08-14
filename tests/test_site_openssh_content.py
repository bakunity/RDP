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
            "permitlisten",
            "Hermes Agent",
            "Trusted RDP certificate",
            "Stable v1.2.1",
            "current main ahead",
        ]:
            self.assertIn(required, text)

        for stale in [
            "v1.0.7",
            "FRPC",
            "FRPS",
            "FRP-сервер",
            "OpenSSH build 1.1.0",
            '"softwareVersion": "1.1.0"',
            "Следующая проверка: порт 53390",
        ]:
            self.assertNotIn(stale, text)

    def test_readme_separates_stable_release_from_current_main(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("stable release", text)
        self.assertIn("v1.2.1", text)
        self.assertIn("Trusted RDP certificate", text)
        self.assertIn("current `main`", text)
        self.assertIn("--trusted-rdp-cert", text)
        self.assertIn("immutable commit", text)

    def test_documentation_has_real_acceptance_path(self) -> None:
        testing = (ROOT / "docs/TESTING_A_TO_Z.md").read_text(
            encoding="utf-8"
        )
        validated = (ROOT / "docs/VALIDATED_SCENARIOS.md").read_text(
            encoding="utf-8"
        )
        security = (ROOT / "docs/SECURITY.md").read_text(encoding="utf-8")

        self.assertIn("внешнего RDP", testing)
        self.assertIn("несколько Windows-ПК", validated)
        self.assertIn("перезагрузки Windows", testing)
        self.assertIn("RDP boundary", security)
        self.assertIn("Trusted public-IP RDP certificate lifecycle", validated)

    def test_site_assets_are_linked(self) -> None:
        text = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('/assets/styles.css', text)
        self.assertIn('/assets/app.js', text)
        self.assertTrue((ROOT / "assets/styles.css").is_file())
        self.assertTrue((ROOT / "assets/app.js").is_file())


if __name__ == "__main__":
    unittest.main()
