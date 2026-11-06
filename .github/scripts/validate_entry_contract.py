#!/usr/bin/env python3
"""Offline contract check for the published 2026 LLM01-LLM10 entries.

Confirms each canonical file still has its pinned title and the sections
required by documentation/style/entries.md. Also refuses raw script markup
in the release markdown, which must not be copied into an HTML deposit.

    python .github/scripts/validate_entry_contract.py
    python .github/scripts/test_validate_entry_contract.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FINAL_DIR = REPO_ROOT / "2026" / "final"

PINNED_TITLES = {
    "LLM01": ("LLM01_PromptInjection.md", "Prompt Injection"),
    "LLM02": ("LLM02_SensitiveInformationDisclosure.md", "Sensitive Information Disclosure"),
    "LLM03": ("LLM03_ExcessiveAgency.md", "Excessive Agency"),
    "LLM04": ("LLM04_SupplyChain.md", "Supply Chain"),
    "LLM05": ("LLM05_DataModelPoisoning.md", "Data and Model Poisoning"),
    "LLM06": ("LLM06_UnboundedConsumption.md", "Unbounded Consumption"),
    "LLM07": ("LLM07_Misinformation.md", "Misinformation"),
    "LLM08": ("LLM08_HiddenContextExposure.md", "Hidden Context Exposure"),
    "LLM09": ("LLM09_VectorAndEmbeddingWeaknesses.md", "Vector and Embedding Weaknesses"),
    "LLM10": ("LLM10_ImproperOutputHandling.md", "Improper Output Handling"),
}

REQUIRED_SECTIONS = (
    "Description",
    "Common Examples of Risk",
    "Prevention and Mitigation Strategies",
    "Example Attack Scenarios",
)

_H2_RE = re.compile(r"^## (LLM\d{2}):2026 (.+?)\s*$", re.MULTILINE)
_H3_RE = re.compile(r"^### (.+?)\s*$")
_SCRIPT_RE = re.compile(r"<\s*script", re.IGNORECASE)


def section_bodies(text: str) -> tuple[list[str], dict[str, str]]:
    """Return H2 lines and a map of H3 heading to the following body."""
    headings = _H2_RE.findall(text)
    bodies: dict[str, list[str]] = {}
    current: str | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf, current
        if current is not None:
            bodies.setdefault(current, [])
            bodies[current].append("\n".join(buf).strip())
        buf = []

    for line in text.splitlines():
        match = _H3_RE.match(line)
        if match:
            flush()
            current = match.group(1).strip()
            continue
        if line.startswith("## "):
            flush()
            current = None
            continue
        if current is not None:
            buf.append(line)
    flush()
    flattened = {name: "\n".join(parts).strip() for name, parts in bodies.items()}
    return [f"{risk_id}: {title}" for risk_id, title in headings], flattened


def validate_text(filename: str, text: str) -> list[str]:
    """Return contract errors for one entry. Empty means the text conforms."""
    errors: list[str] = []
    expected = next((item for item in PINNED_TITLES.items() if item[1][0] == filename), None)
    if expected is None:
        return [f"{filename}: not a pinned LLM01-LLM10 entry"]
    risk_id, (_name, title) = expected
    headings, sections = section_bodies(text)
    expected_heading = f"{risk_id}: {title}"
    if headings != [expected_heading]:
        errors.append(
            f"{filename}: expected a single heading '## {risk_id}:2026 {title}', found {headings!r}"
        )
    seen: dict[str, int] = {}
    for line in text.splitlines():
        match = _H3_RE.match(line)
        if not match:
            continue
        name = match.group(1).strip()
        if name in REQUIRED_SECTIONS:
            seen[name] = seen.get(name, 0) + 1
    for name, count in seen.items():
        if count != 1:
            errors.append(f"{filename}: section {name!r} appears {count} times")
    for name in REQUIRED_SECTIONS:
        body = sections.get(name, "")
        if name not in seen:
            errors.append(f"{filename}: missing required section {name!r}")
        elif not body:
            errors.append(f"{filename}: required section {name!r} is empty")
    if _SCRIPT_RE.search(text):
        errors.append(f"{filename}: release markdown contains a raw script tag")
    return errors


def validate_directory(final_dir: Path) -> list[str]:
    errors: list[str] = []
    if not final_dir.is_dir():
        return [f"missing directory {final_dir}"]
    for risk_id, (filename, _title) in PINNED_TITLES.items():
        path = final_dir / filename
        if not path.is_file():
            errors.append(f"{risk_id}: missing {filename}")
            continue
        if path.is_symlink():
            errors.append(f"{filename}: refusing to validate a symlink")
            continue
        errors.extend(validate_text(filename, path.read_text(encoding="utf-8")))
    return errors


def main() -> int:
    errors = validate_directory(FINAL_DIR)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"OK. {len(PINNED_TITLES)} published entries match the 2026 contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
