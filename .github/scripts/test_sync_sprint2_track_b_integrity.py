#!/usr/bin/env python3
"""Regression test for issue #164: sync_sprint2.py scanned 2026/ instead of
2026/working/ and silently rewrote issues.json with an empty Track B.

This reproduces the bug exactly the way the issue does: it points
sync_sprint2's remote readers at the local checkout (the "remote" is this
repo's own working tree on whatever ref is checked out) instead of the
network, then runs load_existing_from_remote() / reconcile() /
build_updated_config() and asserts that the real ten LLM01..LLM10 entries
are discovered and that none of them are dropped from the rebuilt registry.

On origin/main @ 9253e38 (EXISTING_DIR_PATH = "2026") this fails both
assertions: load_existing_from_remote() finds 0 entries (2026/ no longer
contains loose LLMxx_*.md files after the working/final split), and the
rebuilt registry's track_b is then empty. With the fix
(EXISTING_DIR_PATH = "2026/working", plus build_updated_config() preserving
any track_b entry missing from this run's discovery unless
allow_track_b_removal=True) both assertions pass.

Run directly:
    python .github/scripts/test_sync_sprint2_track_b_integrity.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYNC_SCRIPTS_DIR = REPO_ROOT / "2026" / "working" / "polling" / "scripts"

sys.path.insert(0, str(SYNC_SCRIPTS_DIR))
import sync_sprint2 as ss  # noqa: E402

EXPECTED_ENTRY_IDS = [f"LLM{i:02d}" for i in range(1, 11)]


def _local_list_directory(path: str, branch: str, token):
    """Stand-in for sync_sprint2.list_directory() that lists the local
    checkout instead of calling the GitHub Contents API."""
    target = REPO_ROOT / path
    if not target.is_dir():
        return []
    return [
        {"type": "dir" if p.is_dir() else "file", "name": p.name}
        for p in target.iterdir()
    ]


def _local_fetch_markdown(path: str, branch: str, token) -> str:
    """Stand-in for sync_sprint2.fetch_markdown() that reads the local
    checkout instead of raw.githubusercontent.com."""
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _registry_with_ten_track_b_entries() -> dict:
    return {
        "_meta": {},
        "labels": [],
        "track_a": [],
        "track_b": [
            {"id": entry_id, "title": entry_id, "file": f"{entry_id}_Whatever.md"}
            for entry_id in EXPECTED_ENTRY_IDS
        ],
    }


class SyncSprint2TrackBIntegrityTests(unittest.TestCase):
    """Reproduces GitHub issue #164 against the real repo tree."""

    def setUp(self) -> None:
        self._orig_list_directory = ss.list_directory
        self._orig_fetch_markdown = ss.fetch_markdown
        ss.list_directory = _local_list_directory
        ss.fetch_markdown = _local_fetch_markdown
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        ss.list_directory = self._orig_list_directory
        ss.fetch_markdown = self._orig_fetch_markdown

    def test_existing_dir_path_targets_working_subdirectory(self) -> None:
        # The module docstring has always said the source is 2026/working/;
        # EXISTING_DIR_PATH must actually point there.
        self.assertEqual(ss.EXISTING_DIR_PATH, "2026/working")

    def test_load_existing_from_remote_finds_all_ten_entries(self) -> None:
        local_b = ss.load_existing_from_remote("main", None)
        self.assertEqual(
            sorted(e["id"] for e in local_b),
            EXPECTED_ENTRY_IDS,
            "load_existing_from_remote() must discover LLM01..LLM10 from "
            "2026/working/, not an empty 2026/ listing.",
        )

    def test_full_pipeline_does_not_wipe_track_b(self) -> None:
        config = _registry_with_ten_track_b_entries()
        local_b = ss.load_existing_from_remote("main", None)
        diff = ss.reconcile(local_b, [], config)
        new_config = ss.build_updated_config(local_b, [], config)

        self.assertEqual(
            len(new_config["track_b"]),
            10,
            "rebuilt registry must still carry all 10 Track B entries; "
            f"reconcile() flagged {len(diff['removed_b'])} as removed",
        )

    def test_build_updated_config_preserves_entries_missing_from_discovery(self) -> None:
        # Isolates the safety net itself: even if discovery legitimately
        # (or transiently) returns nothing, build_updated_config() must not
        # silently drop existing Track B entries unless explicitly told to.
        config = _registry_with_ten_track_b_entries()

        new_config = ss.build_updated_config([], [], config)

        self.assertEqual(
            sorted(e["id"] for e in new_config["track_b"]),
            EXPECTED_ENTRY_IDS,
            "build_updated_config() must preserve existing track_b entries "
            "when discovery returns none, unless allow_track_b_removal=True",
        )


if __name__ == "__main__":
    unittest.main()
