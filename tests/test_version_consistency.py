from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_project_version(path: Path) -> str:
    in_project = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            in_project = line == "[project]"
            continue
        if not in_project:
            continue
        match = re.fullmatch(r'version\s*=\s*"([^"]+)"', line)
        if match:
            return match.group(1)
    raise AssertionError(f"project.version not found in {path}")


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

        project_version = read_project_version(ROOT / "server/pyproject.toml")
        self.assertEqual(version, project_version)

        release_notes = ROOT / "docs/releases" / f"v{version}.md"
        self.assertTrue(release_notes.is_file(), release_notes)

        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## [{version}]", changelog)

    def test_api_uses_package_version(self) -> None:
        api_text = (ROOT / "server/hermes_rdp/api.py").read_text(encoding="utf-8")
        self.assertIn("from . import __version__", api_text)
        self.assertIn('"version": __version__', api_text)

    def test_release_workflow_tags_validated_head(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('RELEASE_SHA="$(git rev-parse HEAD)"', workflow)
        self.assertNotIn("git log -1 --format=%H -- VERSION", workflow)

    def test_release_notes_are_source_of_truth_and_existing_releases_sync(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('NOTES="docs/releases/$TAG.md"', workflow)
        self.assertIn('gh release edit "$TAG"', workflow)
        self.assertIn(
            "git diff --name-only \"$BEFORE_SHA\" HEAD -- 'docs/releases/v*.md'",
            workflow,
        )
        self.assertIn("Synchronize changed historical release notes", workflow)

    def test_release_history_protocol_exists(self) -> None:
        release_dir = ROOT / "docs/releases"
        for name in ("README.md", "UNRELEASED.md", "_TEMPLATE.md"):
            path = release_dir / name
            self.assertTrue(path.is_file(), path)
            self.assertGreater(len(path.read_text(encoding="utf-8").strip()), 100)

        protocol = (release_dir / "README.md").read_text(encoding="utf-8")
        self.assertIn("Do not wait until release day", protocol)
        self.assertIn("GitHub Release descriptions", protocol)


if __name__ == "__main__":
    unittest.main()
