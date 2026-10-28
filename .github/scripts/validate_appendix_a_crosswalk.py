#!/usr/bin/env python3
"""Offline crosswalk and relative-asset validator for 2026/final/.

Verifies four deterministic invariants across `2026/final/` without network
access:
  1. Every cell in the 10x9 Coverage Matrix of
     `Appendix_A_Related_Framework_Mappings.md` (`●`, `○`, `—`) matches the
     primary/supporting rows present in the corresponding framework section.
  2. Every element ID and title cited across the nine framework tables in
     `Appendix_A_Related_Framework_Mappings.md` resolves to an entry in
     `2026/final/mappings/*.json`.
  3. Every row in the `Framework Sources & Versions` table matches
     `(framework, version, source_url)` in `2026/final/mappings/*.json`.
  4. Every relative Markdown link/image and HTML `<img src="...">` in
     `2026/final/*.md` resolves to an existing file on disk.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FINAL_DIR = REPO_ROOT / "2026" / "final"

MATRIX_COLUMNS = (
    "ASI",
    "DSGAI",
    "ATLAS",
    "ATT&CK",
    "CWE",
    "600-1",
    "RMF",
    "AICM",
    "AIVSS",
)

SECTIONS: tuple[tuple[str, str, str], ...] = (
    ("ASI", "asi-2026.json", "## OWASP Top 10 for Agentic Applications (ASI)"),
    ("DSGAI", "dsgai-v1.0.json", "## OWASP GenAI Data Security 2026 (DSGAI)"),
    ("ATLAS", "mitre-atlas-2026.06.json", "## MITRE ATLAS"),
    ("ATT&CK", "mitre-attack-v19.1.json", "## MITRE ATT&CK"),
    ("CWE", "cwe-4.20.json", "## MITRE CWE"),
    ("600-1", "nist-ai-600-1.json", "## NIST AI 600-1"),
    ("RMF", "nist-ai-rmf-1.0.json", "## NIST AI RMF"),
    ("AICM", "csa-aicm-v1.1.json", "## CSA AI Controls Matrix"),
    ("AIVSS", "owasp-aivss-v0.8.json", "## OWASP AIVSS"),
)

_CWE_SUFFIX_RE = re.compile(r"\s+\((?:Pillar|Class|Base)\)$")
_MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_HTML_IMG_RE = re.compile(r'<img\s+[^>]*src="([^"]+)"')


def _normalize_cwe_title(title: str) -> str:
    return _CWE_SUFFIX_RE.sub("", title.strip())


def _cwe_titles_match(table_title: str, json_title: str) -> bool:
    norm_json = _normalize_cwe_title(json_title)
    if table_title == json_title or table_title == norm_json:
        return True
    # Allow CWE-359 / CWE-79 canonical short forms used in Appendix A prose
    if norm_json.startswith(table_title):
        return True
    if table_title == "Cross-site Scripting (XSS)" and "Cross-site Scripting" in norm_json:
        return True
    return False


def validate_final_dir(final_dir: Path) -> list[str]:
    """Return a list of validation errors for ``final_dir`` (empty if valid)."""
    errors: list[str] = []
    app_a_path = final_dir / "Appendix_A_Related_Framework_Mappings.md"
    mappings_dir = final_dir / "mappings"

    if not app_a_path.is_file():
        return [f"missing {app_a_path}"]
    if not mappings_dir.is_dir():
        return [f"missing {mappings_dir}"]

    app_a = app_a_path.read_text(encoding="utf-8")

    # 1. Parse Coverage Matrix
    if "## Coverage matrix" not in app_a:
        return ["Appendix A is missing '## Coverage matrix' heading"]

    first_section_header = SECTIONS[0][2]
    matrix_block = app_a.split("## Coverage matrix", 1)[1].split(first_section_header, 1)[0]
    matrix: dict[str, dict[str, str]] = {}
    for line in matrix_block.splitlines():
        match = re.match(r"^\|\s*\*\*(LLM\d{2})\*\*[^|]*\|\s*(.+)\|\s*$", line)
        if not match:
            continue
        llm_id = match.group(1)
        cells = [c.strip() for c in match.group(2).split("|")]
        if len(cells) != len(MATRIX_COLUMNS):
            errors.append(
                f"coverage matrix row {llm_id} has {len(cells)} cells, expected {len(MATRIX_COLUMNS)}"
            )
            continue
        matrix[llm_id] = dict(zip(MATRIX_COLUMNS, cells, strict=True))

    expected_llms = [f"LLM{i:02d}" for i in range(1, 11)]
    for llm_id in expected_llms:
        if llm_id not in matrix:
            errors.append(f"coverage matrix is missing row for {llm_id}")

    # 2. Load JSON catalogs and validate each section + coverage matrix
    json_catalogs: dict[str, dict] = {}
    for idx, (col, json_filename, header) in enumerate(SECTIONS):
        json_path = mappings_dir / json_filename
        if not json_path.is_file():
            errors.append(f"missing mapping catalog: {json_filename}")
            continue
        catalog = json.loads(json_path.read_text(encoding="utf-8"))
        json_catalogs[json_filename] = catalog
        elements: dict[str, str] = {
            el["id"]: el["title"] for el in catalog.get("elements", [])
        }

        if header not in app_a:
            errors.append(f"Appendix A is missing section heading: {header}")
            continue

        next_header = (
            SECTIONS[idx + 1][2]
            if idx + 1 < len(SECTIONS)
            else "## Framework Sources & Versions"
        )
        sec_text = app_a.split(header, 1)[1].split(next_header, 1)[0]

        current_llm: str | None = None
        observed: dict[str, list[str]] = {llm_id: [] for llm_id in expected_llms}

        for line in sec_text.splitlines():
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) != 3 or parts[0] in ("Risk", "---"):
                continue
            if parts[0].startswith("**LLM"):
                m_llm = re.search(r"LLM\d{2}", parts[0])
                if m_llm:
                    current_llm = m_llm.group(0)
            if current_llm is None:
                errors.append(f"[{col}] row encountered before any **LLMxx** header: {line}")
                continue

            el_cell = parts[1]
            if not el_cell or el_cell[0] not in ("●", "○"):
                errors.append(f"[{col}] {current_llm}: invalid marker in element cell {el_cell!r}")
                continue
            marker = el_cell[0]
            rest = el_cell[1:].strip()
            observed[current_llm].append(marker)

            if col in ("ASI", "DSGAI"):
                if "—" not in rest:
                    errors.append(f"[{col}] {current_llm}: expected 'ID — Title' in {rest!r}")
                    continue
                eid, title = [x.strip() for x in rest.split("—", 1)]
                if eid not in elements:
                    errors.append(f"[{col}] {current_llm}: unknown element ID {eid!r}")
                else:
                    expected_title = elements[eid]
                    if title != expected_title and not (
                        col == "DSGAI"
                        and eid == "DSGAI07"
                        and expected_title.removesuffix(" for AI Systems") == title
                    ):
                        errors.append(
                            f"[{col}] {current_llm}: title mismatch for {eid}: "
                            f"table={title!r} vs json={expected_title!r}"
                        )
            elif col in ("ATLAS", "ATT&CK", "CWE", "AICM"):
                if " " not in rest:
                    errors.append(f"[{col}] {current_llm}: expected 'ID Title' in {rest!r}")
                    continue
                eid, title = rest.split(" ", 1)
                if eid not in elements:
                    errors.append(f"[{col}] {current_llm}: unknown element ID {eid!r}")
                elif col == "CWE":
                    if not _cwe_titles_match(title, elements[eid]):
                        errors.append(
                            f"[{col}] {current_llm}: title mismatch for {eid}: "
                            f"table={title!r} vs json={elements[eid]!r}"
                        )
                elif elements[eid] != title:
                    errors.append(
                        f"[{col}] {current_llm}: title mismatch for {eid}: "
                        f"table={title!r} vs json={elements[eid]!r}"
                    )
            elif col == "600-1":
                if rest not in elements:
                    errors.append(f"[{col}] {current_llm}: unknown category {rest!r}")
            elif col == "RMF":
                eid = rest.split("(", 1)[0].strip()
                if eid not in elements:
                    errors.append(f"[{col}] {current_llm}: unknown category ID {eid!r}")
            elif col == "AIVSS":
                if " " not in rest:
                    errors.append(f"[{col}] {current_llm}: expected 'AIVSS-N Title' in {rest!r}")
                    continue
                eid_tok, title = rest.split(" ", 1)
                eid = eid_tok.removeprefix("AIVSS-")
                if eid not in elements:
                    errors.append(f"[{col}] {current_llm}: unknown AIVSS ID {eid_tok!r}")
                elif elements[eid] != title:
                    errors.append(
                        f"[{col}] {current_llm}: title mismatch for {eid_tok}: "
                        f"table={title!r} vs json={elements[eid]!r}"
                    )

        for llm_id, markers in observed.items():
            if not markers:
                expected_sym = "—"
            elif "●" in markers:
                expected_sym = "●"
            else:
                expected_sym = "○"
            actual_sym = matrix.get(llm_id, {}).get(col)
            if actual_sym != expected_sym:
                errors.append(
                    f"[{col}] coverage matrix mismatch for {llm_id}: "
                    f"matrix={actual_sym!r} vs section={expected_sym!r}"
                )

    # 3. Validate Framework Sources & Versions table
    if "## Framework Sources & Versions" not in app_a:
        errors.append("Appendix A is missing '## Framework Sources & Versions'")
    else:
        sources_sec = app_a.split("## Framework Sources & Versions", 1)[1]
        source_rows: dict[str, tuple[str, str]] = {}
        for line in sources_sec.splitlines():
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) != 3 or parts[0] in ("Framework", "---"):
                continue
            source_rows[parts[0]] = (parts[1], parts[2])

        for json_filename, catalog in json_catalogs.items():
            fw = catalog.get("framework", "")
            ver = catalog.get("version", "")
            url = catalog.get("source_url", "")
            if fw not in source_rows:
                errors.append(
                    f"Framework Sources table is missing row for {fw!r} ({json_filename})"
                )
            else:
                row_ver, row_url = source_rows[fw]
                if row_ver != ver:
                    errors.append(
                        f"Framework Sources version mismatch for {fw!r}: "
                        f"table={row_ver!r} vs json={ver!r}"
                    )
                if row_url != url:
                    errors.append(
                        f"Framework Sources URL mismatch for {fw!r}: "
                        f"table={row_url!r} vs json={url!r}"
                    )

    # 4. Validate relative asset links in 2026/final/*.md
    for md_path in sorted(final_dir.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        targets = [m.group(1).strip() for m in _MD_LINK_RE.finditer(text)]
        targets.extend(m.group(1).strip() for m in _HTML_IMG_RE.finditer(text))
        for target in targets:
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            rel_part = urllib.parse.unquote(target.split("#", 1)[0])
            resolved = (md_path.parent / rel_part).resolve()
            if not resolved.exists():
                errors.append(f"{md_path.name}: broken relative path {target!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--final-dir",
        type=Path,
        default=DEFAULT_FINAL_DIR,
        help="Path to the edition final/ directory (default: 2026/final).",
    )
    args = parser.parse_args()
    errors = validate_final_dir(args.final_dir)
    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1
    print(f"OK: {args.final_dir} crosswalk, coverage matrix, sources, and relative assets verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
