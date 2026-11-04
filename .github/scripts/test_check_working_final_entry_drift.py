#!/usr/bin/env python3
"""Unit tests for check_working_final_entry_drift.py.

Builds synthetic working/final/ fixture trees in an isolated temporary
directory so the matching, mismatch, and baseline-comparison logic is
exercised without depending on the real 2026/working/ vs 2026/final/
content (which could itself change as issue #166 is addressed).

Run directly:
    python .github/scripts/test_check_working_final_entry_drift.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_working_final_entry_drift as cwf  # noqa: E402


def _write_entry(entries_dir: Path, filename: str, heading: str) -> None:
    entries_dir.mkdir(parents=True, exist_ok=True)
    (entries_dir / filename).write_text(f"## {heading}\n\nbody text\n", encoding="utf-8")


class LoadEntryMapTests(unittest.TestCase):
    def test_reads_id_filename_and_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            entries_dir = Path(tmp)
            _write_entry(entries_dir, "LLM01_PromptInjection.md", "LLM01:2026 Prompt Injection")

            entries = cwf.load_entry_map(entries_dir)

            self.assertEqual(
                entries["LLM01"],
                ("LLM01_PromptInjection.md", "LLM01:2026 Prompt Injection"),
            )

    def test_missing_directory_returns_empty_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cwf.load_entry_map(Path(tmp) / "does-not-exist"), {})


class FindDriftTests(unittest.TestCase):
    def test_no_drift_when_filenames_match(self) -> None:
        working = {"LLM01": ("LLM01_PromptInjection.md", "Prompt Injection")}
        final = {"LLM01": ("LLM01_PromptInjection.md", "Prompt Injection")}

        self.assertEqual(cwf.find_drift(working, final), {})

    def test_detects_mismatched_filename_for_shared_id(self) -> None:
        working = {"LLM03": ("LLM03_SupplyChain.md", "Supply Chain")}
        final = {"LLM03": ("LLM03_ExcessiveAgency.md", "Excessive Agency")}

        drift = cwf.find_drift(working, final)

        self.assertEqual(
            drift,
            {"LLM03": ("LLM03_SupplyChain.md", "LLM03_ExcessiveAgency.md")},
        )

    def test_ignores_ids_only_present_on_one_side(self) -> None:
        working = {"LLM11": ("LLM11_Extra.md", "Extra")}
        final: dict = {}

        self.assertEqual(cwf.find_drift(working, final), {})


class BaselineComparisonTests(unittest.TestCase):
    def _build_tree(self, root: Path, working_map: dict[str, str], final_map: dict[str, str]) -> None:
        for entry_id, filename in working_map.items():
            _write_entry(root / "working", filename, f"{entry_id}:2026 {filename}")
        for entry_id, filename in final_map.items():
            _write_entry(root / "final", filename, f"{entry_id}:2026 {filename}")

    def test_main_returns_zero_when_drift_matches_known_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            working_map = {eid: f"{eid}_working_{eid}.md" for eid in cwf.KNOWN_DRIFT_IDS}
            final_map = {eid: f"{eid}_final_{eid}.md" for eid in cwf.KNOWN_DRIFT_IDS}
            self._build_tree(root, working_map, final_map)

            self.assertEqual(cwf.main(["--root", str(root)]), 0)

    def test_main_returns_nonzero_when_an_id_matches_outside_the_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # LLM01 is not in KNOWN_DRIFT_IDS, so a newly drifted LLM01
            # must be reported as a failure, not silently accepted.
            working_map = {"LLM01": "LLM01_working.md"}
            final_map = {"LLM01": "LLM01_final.md"}
            self._build_tree(root, working_map, final_map)

            self.assertEqual(cwf.main(["--root", str(root)]), 1)

    def test_main_returns_nonzero_when_a_known_drift_id_is_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            some_known_id = sorted(cwf.KNOWN_DRIFT_IDS)[0]
            # Resolve the drift for one tracked ID without updating the
            # baseline: the script must flag that the set changed.
            working_map = {some_known_id: f"{some_known_id}_same.md"}
            final_map = {some_known_id: f"{some_known_id}_same.md"}
            self._build_tree(root, working_map, final_map)

            self.assertEqual(cwf.main(["--root", str(root)]), 1)

    def test_report_mentions_issue_166(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            working_map = {eid: f"{eid}_working_{eid}.md" for eid in cwf.KNOWN_DRIFT_IDS}
            final_map = {eid: f"{eid}_final_{eid}.md" for eid in cwf.KNOWN_DRIFT_IDS}
            self._build_tree(root, working_map, final_map)

            working = cwf.load_entry_map(root / "working")
            final = cwf.load_entry_map(root / "final")
            report = cwf.format_report(cwf.find_drift(working, final))

            self.assertIn("166", report)


if __name__ == "__main__":
    unittest.main()
