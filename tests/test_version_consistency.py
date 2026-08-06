from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VersionConsistencyTests(unittest.TestCase):
    def test_version_is_consistent(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")

        init_text = (ROOT / "server/hermes_rdp/__init__.py").read_text(
            encoding="utf-8"
        )
        match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
        self.assertIsNotNone(match)
        self.assertEqual(version, match.group(1))

        with (ROOT / "server/pyproject.toml").open("rb") as handle:
            project_version = tomllib.load(handle)["project"]["version"]
        self.assertEqual(version, project_version)

        release_notes = ROOT / "docs/releases" / f"v{version}.md"
        self.assertTrue(release_notes.is_file(), release_notes)

        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## [{version}]", changelog)

    def test_api_uses_package_version(self) -> None:
        api_text = (ROOT / "server/hermes_rdp/api.py").read_text(encoding="utf-8")
        self.assertIn("from . import __version__", api_text)
        self.assertIn('"version": __version__', api_text)


if __name__ == "__main__":
    unittest.main()
