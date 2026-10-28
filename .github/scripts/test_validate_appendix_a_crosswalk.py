#!/usr/bin/env python3
"""Unit tests for validate_appendix_a_crosswalk.py."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_appendix_a_crosswalk as v  # noqa: E402


class TestValidateAppendixACrosswalk(unittest.TestCase):
    def test_live_2026_final_passes(self) -> None:
        errors = v.validate_final_dir(v.DEFAULT_FINAL_DIR)
        self.assertEqual(errors, [])

    def test_detects_coverage_matrix_and_element_and_asset_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy_dir = Path(tmp) / "final"
            shutil.copytree(v.DEFAULT_FINAL_DIR, copy_dir)

            app_a = copy_dir / "Appendix_A_Related_Framework_Mappings.md"
            original = app_a.read_text(encoding="utf-8")

            # 1. Flip LLM02 AIVSS coverage matrix cell from '—' to '●'
            mutated_matrix = original.replace(
                "| **LLM02** Sensitive Information Disclosure | ● | ● | ● | ● | ● | ● | ○ | ● | — |",
                "| **LLM02** Sensitive Information Disclosure | ● | ● | ● | ● | ● | ● | ○ | ● | ● |",
                1,
            )
            app_a.write_text(mutated_matrix, encoding="utf-8")
            errs = v.validate_final_dir(copy_dir)
            self.assertTrue(
                any("coverage matrix mismatch for LLM02" in e for e in errs),
                errs,
            )

            # 2. Introduce unknown element ID ASI99
            mutated_id = original.replace(
                "● ASI01 — Agent Goal Hijack",
                "● ASI99 — Invented Risk",
                1,
            )
            app_a.write_text(mutated_id, encoding="utf-8")
            errs = v.validate_final_dir(copy_dir)
            self.assertTrue(
                any("unknown element ID 'ASI99'" in e for e in errs),
                errs,
            )

            # 3. Introduce broken relative image path in LLM00_Preface.md
            app_a.write_text(original, encoding="utf-8")
            preface = copy_dir / "LLM00_Preface.md"
            preface.write_text(
                preface.read_text(encoding="utf-8")
                + "\n![Broken](report/images/does_not_exist.png)\n",
                encoding="utf-8",
            )
            errs = v.validate_final_dir(copy_dir)
            self.assertTrue(
                any("broken relative path 'report/images/does_not_exist.png'" in e for e in errs),
                errs,
            )


if __name__ == "__main__":
    unittest.main()
