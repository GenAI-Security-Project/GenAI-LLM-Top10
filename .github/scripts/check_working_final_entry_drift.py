#!/usr/bin/env python3
"""Detect drift between which risk 2026/working/ and 2026/final/ assign to
each LLM## entry ID.

README.md states 2026/final/ is the canonical source for the published 2026
release, while 2026/working/ is retained as historical working files and
release-cycle tooling. But 2026/working/polling/scripts/sync_sprint2.py
still actively reads "existing entries" from 2026/working/, so if its
filenames/headings silently drift out of sync with 2026/final/'s numbering,
any tooling built on top of it attaches the wrong topic to the wrong ID
without warning (see issue #166).

This script is not a hard "the trees must match" check: the drift
documented in #166 is a known, historical condition that nobody has
committed to resolving yet. Instead, it pins the currently known mismatched
ID set as a baseline (KNOWN_DRIFT_IDS below) and fails CI only if the
*actual* set of mismatched IDs changes -- grows, shrinks, or shifts -- so
that any further edit to either directory's numbering is a deliberate,
reviewed decision (which should update this baseline, with a short note on
why) rather than a silent accident.

Usage:
    python check_working_final_entry_drift.py [--root PATH]

Exit status is non-zero if the observed drift no longer matches
KNOWN_DRIFT_IDS.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")

# Tracked in issue #166. If a future PR intentionally resolves (or widens)
# this drift, update this set in the same PR along with a note explaining
# the change; do not change it to silence an unexpected new mismatch.
KNOWN_DRIFT_IDS = frozenset({
    "LLM03", "LLM04", "LLM05", "LLM06", "LLM07", "LLM08", "LLM09", "LLM10",
})


def load_entry_map(entries_dir: Path) -> dict[str, tuple[str, str]]:
    """Map entry ID -> (filename, first markdown heading) for every
    LLM##_*.md file directly under entries_dir."""
    out: dict[str, tuple[str, str]] = {}
    if not entries_dir.is_dir():
        return out
    for path in sorted(entries_dir.glob("LLM[0-9][0-9]_*.md")):
        entry_id = path.name.split("_", 1)[0]
        text = path.read_text(encoding="utf-8")
        heading = ""
        for line in text.splitlines():
            m = HEADING_RE.match(line.strip())
            if m:
                heading = m.group(1).strip()
                break
        out[entry_id] = (path.name, heading)
    return out


def find_drift(working: dict[str, tuple[str, str]],
                final: dict[str, tuple[str, str]]) -> dict[str, tuple[str, str]]:
    """Return {entry_id: (working_filename, final_filename)} for every ID
    present in both maps whose filename differs between them."""
    drift = {}
    for entry_id in sorted(set(working) & set(final)):
        w_file = working[entry_id][0]
        f_file = final[entry_id][0]
        if w_file != f_file:
            drift[entry_id] = (w_file, f_file)
    return drift


def format_report(drift: dict[str, tuple[str, str]]) -> str:
    observed_ids = frozenset(drift)
    lines = ["ID     working/                        final/ (canonical)"]
    for entry_id, (w_file, f_file) in drift.items():
        lines.append(f"{entry_id:6s} {w_file:30s} {f_file}")
    if not drift:
        lines.append("(no entry-ID drift between 2026/working/ and 2026/final/)")

    lines.append("")
    if observed_ids == KNOWN_DRIFT_IDS:
        lines.append(f"OK: observed drift matches the tracked baseline ({len(observed_ids)} "
                      "IDs, see issue #166). No action needed.")
    else:
        new_ids = sorted(observed_ids - KNOWN_DRIFT_IDS)
        resolved_ids = sorted(KNOWN_DRIFT_IDS - observed_ids)
        lines.append("MISMATCH: observed drift no longer matches the tracked baseline "
                      "in KNOWN_DRIFT_IDS (issue #166).")
        if new_ids:
            lines.append(f"  newly drifted (not previously tracked): {new_ids}")
        if resolved_ids:
            lines.append(f"  no longer drifted (tracked but now resolved): {resolved_ids}")
        lines.append("  If this change was intentional, update KNOWN_DRIFT_IDS in this "
                      "script in the same PR, with a note on why.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "2026",
        help="Directory containing working/ and final/ (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    working = load_entry_map(args.root / "working")
    final = load_entry_map(args.root / "final")
    drift = find_drift(working, final)

    print(format_report(drift))

    return 0 if frozenset(drift) == KNOWN_DRIFT_IDS else 1


if __name__ == "__main__":
    raise SystemExit(main())
