#!/usr/bin/env python3
"""
Conformance checker for OWASP Top 10 for LLM Applications entries.

Validates files against the rules in:
- documentation/style/entries.md
- 2026/_template.md (the canonical scaffold)

Used by .github/workflows/entry-conformance.yml on pull_request events.
Can also be run locally before pushing:

    python .github/scripts/check-entry-conformance.py 2026/LLM01_PromptInjection.md

Exit code: 0 = pass, 1 = at least one error.

For each error, prints a GitHub Actions annotation:
    ::error file=<path>,line=<n>::<message>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "Description",
    "Common Examples of Risk",
    "Prevention and Mitigation Strategies",
    "Example Attack Scenarios",
    "Reference Links",
]

# Common British spellings to flag. Not exhaustive; add as needed.
BRITISH_WORDS = [
    "behaviour", "behaviours",
    "colour", "colours", "coloured", "colouring",
    "organisation", "organisations", "organisational",
    "authorise", "authorised", "authorising", "authorisation",
    "optimise", "optimised", "optimising", "optimisation",
    "recognise", "recognised", "recognising",
    "analyse", "analysed", "analysing",
    "realise", "realised", "realising",
    "centre", "centres", "centred",
    "favourite", "favourites",
    "licence",  # "license" is the US verb+noun
]


def annotate(path: Path, line: int, message: str) -> None:
    """Emit a GitHub Actions error annotation."""
    escaped = (
        message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    )
    print(f"::error file={path},line={line}::{escaped}")


def file_kind(path: Path) -> str:
    """Classify a file as 'track-b', 'track-a', 'template', or 'unknown'."""
    s = str(path).replace("\\", "/")
    if re.search(r"2026/LLM(0[1-9]|10)_[A-Za-z]+\.md$", s):
        return "track-b"
    if re.search(r"2026/new_entry_candidates/[^/]+\.md$", s):
        return "track-a"
    if s.endswith("2026/_template.md"):
        return "template"
    return "unknown"


def parse_headings(text: str) -> list[tuple[int, int, str]]:
    """Return [(line_no, level, title), ...] for ATX headings."""
    out: list[tuple[int, int, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if m:
            out.append((i, len(m.group(1)), m.group(2)))
    return out


def check_track_b(path: Path, text: str, errors: list) -> None:
    """Validate a Track B (LLMXX_*.md) entry."""
    headings = parse_headings(text)
    if not headings:
        errors.append((path, 1, "no headings found in file"))
        return

    line, level, title = headings[0]
    if level != 2:
        errors.append(
            (path, line, f"first heading must be level 2 (##); got level {level}")
        )
    if not re.match(r"^LLM\d{2}:\s*\S", title):
        errors.append(
            (
                path,
                line,
                "Track B entries require '## LLMXX: <Name>' top heading "
                f"(got: '{title}')",
            )
        )

    _check_required_sections(path, text, errors)
    _check_no_level_skips(path, text, errors)
    _check_references(path, text, errors)
    _check_us_english(path, text, errors)


def check_track_a(path: Path, text: str, errors: list) -> None:
    """Validate a Track A (new_entry_candidates/<slug>.md) entry."""
    if not re.match(r"^[a-z0-9][a-z0-9-]*\.md$", path.name):
        errors.append(
            (
                path,
                1,
                "Track A files must use lowercase-hyphenated slugs "
                f"(e.g. 'model-inversion.md'); got '{path.name}'",
            )
        )

    headings = parse_headings(text)
    if not headings:
        errors.append((path, 1, "no headings found in file"))
        return

    line, level, title = headings[0]
    if level != 2:
        errors.append(
            (path, line, f"first heading must be level 2 (##); got level {level}")
        )
    if re.match(r"^LLM\d{2}:", title):
        errors.append(
            (
                path,
                line,
                "Track A entries must NOT include 'LLMXX:' prefix in the heading; "
                "numbering is assigned at promotion",
            )
        )

    _check_required_sections(path, text, errors)
    _check_no_level_skips(path, text, errors)
    _check_references(path, text, errors)
    _check_us_english(path, text, errors)


def check_template(path: Path, text: str, errors: list) -> None:
    """Verify the canonical template hasn't been corrupted into a real entry."""
    if "## LLMXX: Risk Name" not in text:
        errors.append(
            (
                path,
                1,
                "_template.md must preserve the '## LLMXX: Risk Name' placeholder. "
                "Did you mean to create a new file in 2026/new_entry_candidates/ "
                "instead?",
            )
        )


def _check_required_sections(path: Path, text: str, errors: list) -> None:
    """Verify all five required level-3 sections appear in order."""
    h3 = [(line, title) for line, level, title in parse_headings(text) if level == 3]
    h3_titles = [t for _, t in h3]

    last_idx = -1
    for required in REQUIRED_SECTIONS:
        try:
            idx = h3_titles.index(required)
        except ValueError:
            errors.append((path, 1, f"missing required section '### {required}'"))
            continue
        if idx <= last_idx:
            line_no = h3[idx][0]
            errors.append(
                (
                    path,
                    line_no,
                    f"section '### {required}' appears out of order; "
                    f"required order: {', '.join(REQUIRED_SECTIONS)}",
                )
            )
        last_idx = idx


def _check_no_level_skips(path: Path, text: str, errors: list) -> None:
    """Flag heading-level skips (e.g. ## -> ####)."""
    headings = parse_headings(text)
    prev_level = 0
    for line, level, title in headings:
        if prev_level and level > prev_level + 1:
            errors.append(
                (
                    path,
                    line,
                    f"heading level skip: '{'#' * level} {title[:60]}' "
                    f"jumps from level {prev_level} to {level}",
                )
            )
        prev_level = level


def _check_references(path: Path, text: str, errors: list) -> None:
    """Verify reference list entries include a bolded publisher."""
    m = re.search(
        r"^### Reference Links\s*$\n+(.*?)(?=^\Z|^### )",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        return  # missing-section error already emitted by _check_required_sections
    section = m.group(1)
    section_start_offset = m.start(1)
    section_start_line = text[:section_start_offset].count("\n") + 1

    for offset, line in enumerate(section.splitlines()):
        line_no = section_start_line + offset
        if not re.match(r"^\d+\.\s+\[", line):
            continue  # blank or non-reference line
        # Bolded **publisher** must appear after the URL closing paren.
        if not re.search(r"\)\s*[: ]\s*.*?\*\*[^*]+\*\*", line):
            errors.append(
                (
                    path,
                    line_no,
                    f"reference missing bolded publisher: '{line[:100]}'",
                )
            )


def _check_us_english(path: Path, text: str, errors: list) -> None:
    """Flag common British spellings."""
    for i, line in enumerate(text.splitlines(), start=1):
        for word in BRITISH_WORDS:
            if re.search(rf"\b{word}\b", line, re.IGNORECASE):
                errors.append(
                    (
                        path,
                        i,
                        f"British spelling '{word}' detected; use US English "
                        "equivalent",
                    )
                )


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv]
    if not files:
        print(
            "usage: check-entry-conformance.py <file1.md> [<file2.md> ...]",
            file=sys.stderr,
        )
        return 0

    errors: list[tuple[Path, int, str]] = []
    for f in files:
        if not f.exists():
            continue
        kind = file_kind(f)
        if kind == "unknown":
            continue
        text = f.read_text(encoding="utf-8")
        if kind == "track-b":
            check_track_b(f, text, errors)
        elif kind == "track-a":
            check_track_a(f, text, errors)
        elif kind == "template":
            check_template(f, text, errors)

    for path, line, msg in errors:
        annotate(path, line, msg)

    if errors:
        print(
            f"\n{len(errors)} conformance error(s) found.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
