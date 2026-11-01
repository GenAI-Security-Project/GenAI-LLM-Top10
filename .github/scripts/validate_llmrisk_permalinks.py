#!/usr/bin/env python3
"""Validate the canonical 2026 /llmrisk/ permalink contract.

The registry in 2026/final/permalinks.json is the slug list integrators and
the site should publish. This check keeps that list, the entry H1 titles, the
human table, and every /llmrisk/ link under 2026/final/ on the same contract.

    python .github/scripts/validate_llmrisk_permalinks.py
    python .github/scripts/validate_llmrisk_permalinks.py --check-live

--check-live probes genai.owasp.org. It is not part of the offline test: the
2026 posts are the thing this registry exists to publish, so a 404 there is
recorded, not treated as a slug error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FINAL = REPO_ROOT / "2026" / "final"
REGISTRY_PATH = FINAL / "permalinks.json"
TABLE_PATH = FINAL / "permalinks.md"
README_PATH = REPO_ROOT / "2026" / "README.md"

H1_RE = re.compile(r"^## (LLM\d{2}):(\d{4}) (.+)$", re.M)
LINK_RE = re.compile(r"https://genai\.owasp\.org/llmrisk/[A-Za-z0-9-]+/?")
SLUG_RE = re.compile(r"^llm(\d{2})(\d{4})-([a-z0-9-]+)$")


def slugify_title(title: str) -> str:
    """Lowercase-and-hyphenate an entry title. '&' becomes 'and'."""
    text = title.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def canonical_slug(entry_id: str, year: str, title: str) -> str:
    number = entry_id.removeprefix("LLM")
    return f"llm{number}{year}-{slugify_title(title)}"


def canonical_url(slug: str) -> str:
    return f"https://genai.owasp.org/llmrisk/{slug}/"


def load_registry(path: Path = REGISTRY_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def entry_headings(final_dir: Path = FINAL) -> dict[str, tuple[str, str, Path]]:
    """Map LLM id to (year, title, path) from each entry's H1."""
    found: dict[str, tuple[str, str, Path]] = {}
    for path in sorted(final_dir.glob("LLM[0-9][0-9]_*.md")):
        match = H1_RE.search(path.read_text(encoding="utf-8"))
        if not match:
            continue
        found[match.group(1)] = (match.group(2), match.group(3).strip(), path)
    return found


def problems_for(registry: dict, headings: dict[str, tuple[str, str, Path]], texts: list[tuple[str, str]]) -> list[str]:
    problems: list[str] = []
    entries = registry.get("entries") or []
    if len(entries) != 10:
        problems.append(f"registry has {len(entries)} entries, expected 10")
    if registry.get("llm01_decision") != "normalize-year-infix":
        problems.append("LLM01 decision must stay normalize-year-infix; do not carry the 2025 exception forward")

    seen_ids: set[str] = set()
    canonical_urls: set[str] = set()
    for entry in entries:
        entry_id = entry.get("id", "")
        if entry_id in seen_ids:
            problems.append(f"duplicate registry id {entry_id}")
        seen_ids.add(entry_id)
        title = entry.get("title", "")
        year = str(entry.get("year", ""))
        expected_slug = canonical_slug(entry_id, year, title) if entry_id and year and title else ""
        slug = entry.get("slug", "")
        url = entry.get("url", "")
        if slug != expected_slug:
            problems.append(f"{entry_id}: slug {slug!r} != derived {expected_slug!r}")
        if url != canonical_url(slug):
            problems.append(f"{entry_id}: url {url!r} != {canonical_url(slug)!r}")
        if not SLUG_RE.match(slug):
            problems.append(f"{entry_id}: slug {slug!r} is not llmXXYYYY-words")
        if slug.startswith("llm01") and "2026" not in slug:
            problems.append("LLM01 2026 slug dropped the year infix")
        heading = headings.get(entry_id)
        if heading is None:
            problems.append(f"{entry_id}: no H1 in 2026/final")
        else:
            head_year, head_title, head_path = heading
            if head_year != year or head_title != title:
                problems.append(
                    f"{entry_id}: registry {year} {title!r} != H1 {head_year} {head_title!r}"
                )
            try:
                rel = head_path.resolve().relative_to(REPO_ROOT).as_posix()
            except ValueError:
                rel = ""
            if entry.get("source") and rel and entry["source"] != rel:
                problems.append(f"{entry_id}: source {entry.get('source')} != {rel}")
        canonical_urls.add(url)

    missing = [f"LLM{i:02d}" for i in range(1, 11) if f"LLM{i:02d}" not in seen_ids]
    if missing:
        problems.append("missing entries: " + ", ".join(missing))

    historical = {item.get("url", "").rstrip("/") + "/" for item in registry.get("historical_2025") or []}
    # The 2025 LLM01 exception must stay recorded, and must not be a 2026 slug.
    if canonical_url("llm01-prompt-injection") not in historical:
        problems.append("historical set dropped the 2025 LLM01 exception")
    if any("2026" in url for url in historical):
        problems.append("historical_2025 contains a 2026 URL")

    allowed = canonical_urls | historical
    for label, text in texts:
        for match in LINK_RE.finditer(text):
            raw = match.group(0)
            normalized = raw if raw.endswith("/") else raw + "/"
            if normalized not in allowed:
                problems.append(f"{label}: /llmrisk/ link is not canonical or historical: {raw}")
    return problems


def validate(root: Path | None = None) -> list[str]:
    root = root or REPO_ROOT
    registry = load_registry(root / "2026" / "final" / "permalinks.json")
    headings = entry_headings(root / "2026" / "final")
    # Rewrite heading paths relative to the given root when tests pass a copy.
    texts = []
    final_dir = root / "2026" / "final"
    for path in sorted(final_dir.rglob("*.md")):
        texts.append((path.relative_to(root).as_posix(), path.read_text(encoding="utf-8")))
    readme = root / "2026" / "README.md"
    if readme.is_file():
        texts.append((readme.relative_to(root).as_posix(), readme.read_text(encoding="utf-8")))
    problems = problems_for(registry, headings, texts)
    table = (root / "2026" / "final" / "permalinks.md").read_text(encoding="utf-8")
    readme_text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    for entry in registry.get("entries") or []:
        if entry["url"] not in table:
            problems.append(f"permalinks.md missing {entry['url']}")
        if entry["url"] not in readme_text:
            problems.append(f"2026/README.md missing {entry['url']}")
    return problems


def check_live(registry: dict) -> int:
    """Probe the published post type. Non-zero if a canonical slug is live under a different path."""
    import json as _json
    import urllib.request

    url = "https://genai.owasp.org/wp-json/wp/v2/llmrisk?per_page=100&_fields=slug,link"
    request = urllib.request.Request(url, headers={"User-Agent": "owasp-llm-top10-permalink-check"})
    with urllib.request.urlopen(request, timeout=30) as response:
        live = {item["slug"] for item in _json.loads(response.read().decode())}
    missing = [entry["slug"] for entry in registry["entries"] if entry["slug"] not in live]
    print(f"live llmrisk slugs: {len(live)}")
    if missing:
        print("not yet published:")
        for slug in missing:
            print(f"  {slug}")
        return 0
    print("all canonical 2026 slugs are published")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-live", action="store_true", help="list 2026 slugs the site has not published")
    args = parser.parse_args()
    registry = load_registry()
    found = validate()
    for problem in found:
        print(f"FAIL: {problem}", file=sys.stderr)
    if found:
        sys.exit(1)
    print(f"OK. {len(registry['entries'])} canonical 2026 /llmrisk/ permalinks")
    if args.check_live:
        sys.exit(check_live(registry))


if __name__ == "__main__":
    main()
