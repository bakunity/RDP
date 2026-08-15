from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AptDuplicateCleanupTests(unittest.TestCase):
    def test_bootstrap_repairs_only_exact_duplicate_deb_lines(self) -> None:
        bootstrap = (ROOT / "scripts/install.sh").read_text(encoding="utf-8")
        self.assertIn("dedupe_exact_entries_in_file", bootstrap)
        self.assertIn("repair_duplicate_apt_warnings", bootstrap)
        self.assertIn("is configured multiple times", bootstrap)
        self.assertIn("cmp -s", bootstrap)
        self.assertIn("apt-sources-dedupe-", bootstrap)
        self.assertIn("source-файлы восстановлены", bootstrap)
        self.assertIn("key ~ /^(deb|deb-src)[[:space:]]+/", bootstrap)
        self.assertIn('dedupe_exact_entries_in_file "$file" || true', bootstrap)


if __name__ == "__main__":
    unittest.main()
