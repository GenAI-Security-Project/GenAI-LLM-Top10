#!/usr/bin/env python3
"""Offline tests for the Appendix A / mappings join.

    python .github/scripts/test_validate_mapping_crosswalk.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_mapping_crosswalk as v  # noqa: E402


class CrosswalkTest(unittest.TestCase):
    def test_repository_joins(self) -> None:
        self.assertEqual(v.validate(), [])

    def test_duplicate_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(v.FINAL, root / "2026" / "final")
            path = root / "2026" / "final" / "mappings" / "asi-2026.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["elements"].append(dict(data["elements"][0]))
            path.write_text(json.dumps(data), encoding="utf-8")
            problems = v.validate(root)
            self.assertTrue(any("duplicate id" in item for item in problems), problems)

    def test_unresolved_aivss_label_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(v.FINAL, root / "2026" / "final")
            path = root / "2026" / "final" / "Appendix_A_Related_Framework_Mappings.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace("AIVSS-10", "AIVSS-99", 1)
            path.write_text(text, encoding="utf-8")
            problems = v.validate(root)
            self.assertTrue(any("AIVSS-99" in item for item in problems), problems)

    def test_matrix_symbol_drift_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(v.FINAL, root / "2026" / "final")
            path = root / "2026" / "final" / "Appendix_A_Related_Framework_Mappings.md"
            text = path.read_text(encoding="utf-8")
            # LLM10 / RMF is an em dash. Flip that one cell to a primary mark
            # without adding a section row.
            old = "| **LLM10** Improper Output Handling | ● | ● | ● | ● | ● | ● | — | ● | ○ |"
            new = "| **LLM10** Improper Output Handling | ● | ● | ● | ● | ● | ● | ● | ● | ○ |"
            self.assertIn(old, text)
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            problems = v.validate(root)
            self.assertTrue(any("matrix RMF LLM10" in item for item in problems), problems)

    def test_dsgai07_short_title_is_the_only_waiver(self) -> None:
        self.assertTrue(v.title_ok("DSGAI", "DSGAI07", v.DSGAI07_SHORT, "Data Governance, Lifecycle & Classification for AI Systems"))
        self.assertFalse(v.title_ok("DSGAI", "DSGAI01", "Sensitive Data Leak", "Sensitive Data Leakage"))


if __name__ == "__main__":
    unittest.main()
