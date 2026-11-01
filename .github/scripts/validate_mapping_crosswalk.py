#!/usr/bin/env python3
"""Check that Appendix A joins to mappings/*.json.

Every element id cited in a by-framework table must resolve to exactly one
element in the pinned JSON catalog. Coverage-matrix symbols must agree with
those tables: a primary mark requires a primary row, a supporting mark requires
rows and no primary, and an em dash requires no row.

AIVSS is the exception on id shape. The source assigns ordinals, so the JSON
id stays "1".."10". Appendix A labels the same risks AIVSS-1..AIVSS-10. The
join key is display_id, which must be AIVSS-<id>.

DSGAI07's short title in Appendix A is waived while open PR #153 replaces it
with the catalog title. Any other title drift fails.

    python .github/scripts/validate_mapping_crosswalk.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FINAL = REPO_ROOT / "2026" / "final"
MAPPINGS = FINAL / "mappings"
APPENDIX = FINAL / "Appendix_A_Related_Framework_Mappings.md"

# Appendix title that #153 corrects. Accept the short form or the catalog title.
DSGAI07_SHORT = "Data Governance, Lifecycle & Classification"

MATRIX_KEYS = ["ASI", "DSGAI", "ATLAS", "ATT&CK", "CWE", "600-1", "RMF", "AICM", "AIVSS"]

SPECS = [
    {
        "key": "ASI",
        "heading": "OWASP Top 10 for Agentic Applications (ASI)",
        "file": "asi-2026.json",
        "id_re": re.compile(r"ASI\d{2}"),
        "titles": "exact",
    },
    {
        "key": "DSGAI",
        "heading": "OWASP GenAI Data Security 2026 (DSGAI)",
        "file": "dsgai-v1.0.json",
        "id_re": re.compile(r"DSGAI\d{2}"),
        "titles": "exact",
    },
    {
        "key": "ATLAS",
        "heading": "MITRE ATLAS",
        "file": "mitre-atlas-2026.06.json",
        "id_re": re.compile(r"AML\.TA\d{4}"),
        "titles": "exact",
    },
    {
        "key": "ATT&CK",
        "heading": "MITRE ATT&CK",
        "file": "mitre-attack-v19.1.json",
        "id_re": re.compile(r"TA\d{4}"),
        "titles": "exact",
    },
    {
        "key": "CWE",
        "heading": "MITRE CWE",
        "file": "cwe-4.20.json",
        "id_re": re.compile(r"CWE-\d+"),
        "titles": "id-only",
    },
    {
        "key": "600-1",
        "heading": "NIST AI 600-1",
        "file": "nist-ai-600-1.json",
        "id_re": None,
        "titles": "name",
    },
    {
        "key": "RMF",
        "heading": "NIST AI RMF",
        "file": "nist-ai-rmf-1.0.json",
        "id_re": re.compile(r"(?:GOVERN|MAP|MEASURE|MANAGE) \d"),
        "titles": "id-only",
    },
    {
        "key": "AICM",
        "heading": "CSA AI Controls Matrix",
        "file": "csa-aicm-v1.1.json",
        "id_re": re.compile(r"\b(?:A&A|AIS|BCR|CCC|CEK|DCS|DSP|GRC|HRS|IAM|IPY|IVS|LOG|MDS|SEF|STA|TVM|UEM)\b"),
        "titles": "id-only",
    },
    {
        "key": "AIVSS",
        "heading": "OWASP AIVSS",
        "file": "owasp-aivss-v0.8.json",
        "id_re": re.compile(r"AIVSS-\d+"),
        "titles": "exact",
    },
]


def load_catalog(path: Path) -> tuple[dict, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    problems = []
    by_id = {}
    for element in data.get("elements") or []:
        element_id = element.get("id")
        title = element.get("title")
        if not element_id or not title:
            problems.append(f"{path.name}: element missing id or title")
            continue
        if element_id in by_id:
            problems.append(f"{path.name}: duplicate id {element_id}")
        by_id[element_id] = element
    return {"data": data, "by_id": by_id, "path": path}, problems


def section_body(appendix: str, heading: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(heading)}.*?\n(.*?)(?=^## |\Z)", appendix)
    return match.group(1) if match else ""


def parse_matrix(appendix: str) -> dict[str, dict[str, str]]:
    match = re.search(
        r"\| Risk \| ASI \| DSGAI \| ATLAS \| ATT&CK \| CWE \| 600-1 \| RMF \| AICM \| AIVSS \|\n"
        r"\|.*?\n((?:\|.*\n)+)",
        appendix,
    )
    matrix = {}
    if not match:
        return matrix
    for line in match.group(1).splitlines():
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        risk = re.search(r"LLM\d{2}", cols[0]) if cols else None
        if not risk or len(cols) < 10:
            continue
        matrix[risk.group(0)] = dict(zip(MATRIX_KEYS, cols[1:10]))
    return matrix


def symbol_of(cell: str) -> str:
    if "●" in cell:
        return "primary"
    if "○" in cell:
        return "supporting"
    if "—" in cell or "-" == cell:
        return "none"
    return "unknown"


def cell_title(cell: str, element_id: str) -> str:
    rest = cell.split(element_id, 1)[-1]
    return rest.strip(" ●○—–-")


def resolve_aivss(token: str, by_id: dict) -> dict | None:
    ordinal = token.split("-", 1)[-1]
    for element in by_id.values():
        if element.get("display_id") == token or element.get("id") == ordinal:
            if element.get("display_id") == token:
                return element
    # Fall back only when display_id is absent, so a wrong display_id still fails.
    for element in by_id.values():
        if element.get("id") == ordinal and not element.get("display_id"):
            return element
    return None


def parse_rows(body: str, id_re: re.Pattern | None) -> list[tuple[str, str, list[str], str]]:
    rows = []
    current = None
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        raw = line.strip().strip("|")
        if re.fullmatch(r"[:\-| ]+", raw):
            continue
        cols = [col.strip() for col in raw.split("|")]
        if len(cols) < 3 or cols[0].startswith("Risk") or cols[1].startswith("Element"):
            continue
        if cols[0]:
            risk = re.search(r"LLM\d{2}", cols[0])
            if risk:
                current = risk.group(0)
        cell = cols[1]
        ids = id_re.findall(cell) if id_re else []
        rows.append((current, symbol_of(cell), ids, cell))
    return rows


def check_aivss_catalog(catalog: dict) -> list[str]:
    problems = []
    for element_id, element in catalog["by_id"].items():
        expected = f"AIVSS-{element_id}"
        display = element.get("display_id")
        if display != expected:
            problems.append(
                f"owasp-aivss-v0.8.json: id {element_id} display_id {display!r} != {expected!r}"
            )
        if not re.fullmatch(r"\d+", element_id):
            problems.append(f"owasp-aivss-v0.8.json: id {element_id} is not the source ordinal")
    return problems


def title_ok(key: str, element_id: str, quoted: str, catalog_title: str) -> bool:
    if quoted == catalog_title:
        return True
    if key == "DSGAI" and element_id == "DSGAI07" and quoted == DSGAI07_SHORT:
        return True
    return False


def validate(root: Path | None = None) -> list[str]:
    root = root or REPO_ROOT
    final = root / "2026" / "final"
    mappings = final / "mappings"
    appendix_path = final / "Appendix_A_Related_Framework_Mappings.md"
    problems: list[str] = []
    if not appendix_path.is_file():
        return [f"missing {appendix_path}"]
    appendix = appendix_path.read_text(encoding="utf-8")
    matrix = parse_matrix(appendix)
    if len(matrix) != 10:
        problems.append(f"coverage matrix has {len(matrix)} risks, expected 10")

    for spec in SPECS:
        catalog, catalog_problems = load_catalog(mappings / spec["file"])
        problems.extend(catalog_problems)
        if spec["key"] == "AIVSS":
            problems.extend(check_aivss_catalog(catalog))
        body = section_body(appendix, spec["heading"])
        if not body:
            problems.append(f"missing section {spec['heading']}")
            continue
        rows = parse_rows(body, spec["id_re"])
        by_risk: dict[str, list] = {}
        for risk, strength, ids, cell in rows:
            by_risk.setdefault(risk, []).append((strength, ids, cell))
            if spec["titles"] == "name":
                if not any(element["title"] in cell for element in catalog["by_id"].values()):
                    problems.append(f"{spec['key']} {risk}: name not in catalog: {cell[:80]}")
                continue
            for element_id in ids:
                if spec["key"] == "AIVSS":
                    element = resolve_aivss(element_id, catalog["by_id"])
                else:
                    element = catalog["by_id"].get(element_id)
                if element is None:
                    problems.append(f"{spec['key']} {risk}: unresolved id {element_id}")
                    continue
                if spec["titles"] == "exact":
                    quoted = cell_title(cell, element_id)
                    if not title_ok(spec["key"], element_id, quoted, element["title"]):
                        problems.append(
                            f"{spec['key']} {element_id}: appendix title {quoted!r} != catalog {element['title']!r}"
                        )
        for risk in [f"LLM{i:02d}" for i in range(1, 11)]:
            cell = matrix.get(risk, {}).get(spec["key"], "")
            expected = symbol_of(cell)
            items = by_risk.get(risk, [])
            has_primary = any(strength == "primary" for strength, _, _ in items)
            actual = "primary" if has_primary else "supporting" if items else "none"
            if expected != actual:
                problems.append(
                    f"matrix {spec['key']} {risk}: matrix={expected} section={actual}"
                )
    return problems


def main() -> None:
    found = validate()
    for problem in found:
        print(f"FAIL: {problem}", file=sys.stderr)
    if found:
        sys.exit(1)
    print("OK. Appendix A joins to mappings/*.json")


if __name__ == "__main__":
    main()
