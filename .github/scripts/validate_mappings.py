#!/usr/bin/env python3
"""Validate mapping catalogs against version-pinned primary datasets."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAPPING_DIR = ROOT / "2026" / "final" / "mappings"
DEFAULT_SOURCE_DIR = ROOT / ".cache" / "mapping-sources"
SUPPORTED_CATALOGS = {
    "cwe-4.20.json": "cwe",
    "mitre-atlas-2026.06.json": "atlas",
}
MAX_SOURCE_BYTES = 25 * 1024 * 1024


def sha256(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def parse_expected_sha(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError("source_sha must use the form sha256:<64 lowercase hex digits>")
    return value


def read_source(mapping: dict, source_dir: Path, download: bool) -> bytes:
    source_url = mapping.get("source_url")
    if not isinstance(source_url, str) or urlparse(source_url).scheme != "https":
        raise ValueError("source_url must be an HTTPS URL")

    filename = Path(urlparse(source_url).path).name
    if not filename:
        raise ValueError("source_url must identify a source file")

    source_path = source_dir / filename
    if not source_path.exists():
        if not download:
            raise ValueError(
                f"source file not found: {source_path} "
                "(use --download to populate the cache)"
            )
        source_dir.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(source_url, timeout=60) as response:
                data = response.read(MAX_SOURCE_BYTES + 1)
        except Exception as exc:
            raise ValueError(f"could not download {source_url}: {exc}") from exc
        if len(data) > MAX_SOURCE_BYTES:
            raise ValueError(
                f"source exceeds the {MAX_SOURCE_BYTES // (1024 * 1024)} MiB limit"
            )
        source_path.write_bytes(data)

    return source_path.read_bytes()


def validate_source_location(catalog: str, mapping: dict) -> list[str]:
    source_url = mapping.get("source_url")
    if not isinstance(source_url, str):
        return ["source_url must be an HTTPS URL"]

    if catalog == "cwe":
        expected = (
            "https://cwe.mitre.org/data/xml/"
            f"cwec_v{mapping.get('version', '')}.xml.zip"
        )
        if source_url != expected:
            return [f"CWE source_url must be the pinned source {expected}"]
        return []

    version_match = re.fullmatch(
        r"content v(\d{4}\.\d{2}) \(format-version ([^)]+)\)",
        str(mapping.get("version", "")),
    )
    if not version_match:
        return ["ATLAS version must be 'content vYYYY.MM (format-version X.Y.Z)'"]
    content_version = version_match.group(1)
    expected = (
        "https://raw.githubusercontent.com/mitre-atlas/atlas-data/"
        f"main/dist/v6/ATLAS-{content_version}.yaml"
    )
    if source_url != expected:
        return [
            "ATLAS source_url must use the pinned v6 source "
            f"{expected}"
        ]
    return []


def validate_common(mapping: dict) -> list[str]:
    errors: list[str] = []
    elements = mapping.get("elements")
    if not isinstance(elements, list):
        return ["elements must be an array"]

    seen: set[str] = set()
    for index, element in enumerate(elements):
        location = f"elements[{index}]"
        if not isinstance(element, dict):
            errors.append(f"{location} must be an object")
            continue
        element_id = element.get("id")
        title = element.get("title")
        if not isinstance(element_id, str) or not element_id:
            errors.append(f"{location}.id must be a non-empty string")
        elif element_id in seen:
            errors.append(f"duplicate element id: {element_id}")
        else:
            seen.add(element_id)
        if not isinstance(title, str) or not title:
            errors.append(f"{location}.title must be a non-empty string")
    return errors


def validate_cwe(mapping: dict, source: bytes) -> list[str]:
    errors: list[str] = []
    expected_version = str(mapping.get("version", ""))

    try:
        with zipfile.ZipFile(io.BytesIO(source)) as archive:
            expected_member = f"cwec_v{expected_version}.xml"
            if archive.namelist() != [expected_member]:
                errors.append(
                    f"CWE archive must contain only {expected_member}; "
                    f"found {archive.namelist()}"
                )
                return errors
            root = ET.fromstring(archive.read(expected_member))
    except (zipfile.BadZipFile, ET.ParseError, KeyError) as exc:
        return errors + [f"invalid CWE source archive: {exc}"]

    source_version = root.attrib.get("Version")
    if source_version != expected_version:
        errors.append(
            f"CWE source version mismatch: expected {expected_version}, "
            f"found {source_version or 'missing'}"
        )

    namespace = root.tag.partition("}")[0].lstrip("{")
    weaknesses = {}
    for weakness in root.findall(f".//{{{namespace}}}Weakness"):
        weakness_id = f"CWE-{weakness.attrib.get('ID', '')}"
        title = weakness.attrib.get("Name", "")
        abstraction = weakness.attrib.get("Abstraction", "")
        weaknesses[weakness_id] = f"{title} ({abstraction})"

    for element in mapping.get("elements", []):
        if not isinstance(element, dict):
            continue
        element_id = element.get("id")
        if element_id not in weaknesses:
            errors.append(f"{element_id}: identifier not found in CWE {expected_version}")
        elif element.get("title") != weaknesses[element_id]:
            errors.append(
                f"{element_id}: title mismatch; expected "
                f"{weaknesses[element_id]!r}, found {element.get('title')!r}"
            )
    return errors


def atlas_metadata(source: bytes) -> tuple[str | None, str | None, dict[str, str]]:
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"ATLAS source is not UTF-8: {exc}") from exc

    format_version = None
    content_version = None
    tactics: dict[str, str] = {}
    in_collection = False
    in_tactics = False
    current_tactic = None

    for line in text.splitlines():
        if line.startswith("format-version:"):
            format_version = line.split(":", 1)[1].strip().strip("'\"")
        elif line == "collection:":
            in_collection = True
            in_tactics = False
        elif line == "tactics:":
            in_collection = False
            in_tactics = True
        elif line and not line.startswith(" "):
            in_collection = False
            in_tactics = False
        elif in_collection and line.startswith("  version:"):
            content_version = line.split(":", 1)[1].strip().strip("'\"")
        elif in_tactics:
            tactic_match = re.fullmatch(r"  (AML\.TA\d{4}):", line)
            if tactic_match:
                current_tactic = tactic_match.group(1)
            elif current_tactic and line.startswith("    name:"):
                tactics[current_tactic] = line.split(":", 1)[1].strip().strip("'\"")
                current_tactic = None

    return format_version, content_version, tactics


def validate_atlas(mapping: dict, source: bytes) -> list[str]:
    errors: list[str] = []
    version_match = re.fullmatch(
        r"content v(\d{4}\.\d{2}) \(format-version ([^)]+)\)",
        str(mapping.get("version", "")),
    )
    if not version_match:
        return ["ATLAS version must be 'content vYYYY.MM (format-version X.Y.Z)'"]

    expected_content, expected_format = version_match.groups()

    try:
        source_format, source_content, tactics = atlas_metadata(source)
    except ValueError as exc:
        return errors + [str(exc)]

    if source_format != expected_format:
        errors.append(
            f"ATLAS format-version mismatch: expected {expected_format}, "
            f"found {source_format or 'missing'}"
        )
    if source_content != expected_content:
        errors.append(
            f"ATLAS content version mismatch: expected {expected_content}, "
            f"found {source_content or 'missing'}"
        )

    for element in mapping.get("elements", []):
        if not isinstance(element, dict):
            continue
        element_id = element.get("id")
        if element_id not in tactics:
            errors.append(
                f"{element_id}: identifier not found in ATLAS {expected_content} tactics"
            )
        elif element.get("title") != tactics[element_id]:
            errors.append(
                f"{element_id}: title mismatch; expected "
                f"{tactics[element_id]!r}, found {element.get('title')!r}"
            )
    return errors


def validate_catalog(path: Path, source_dir: Path, download: bool) -> list[str]:
    try:
        mapping = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"could not read mapping: {exc}"]
    if not isinstance(mapping, dict):
        return ["mapping root must be an object"]

    errors = validate_common(mapping)
    validator = SUPPORTED_CATALOGS[path.name]
    location_errors = validate_source_location(validator, mapping)
    if location_errors:
        return errors + location_errors
    try:
        expected_sha = parse_expected_sha(mapping.get("source_sha"))
        source = read_source(mapping, source_dir, download)
    except ValueError as exc:
        return errors + [str(exc)]

    actual_sha = sha256(source)
    if actual_sha != expected_sha:
        return errors + [
            f"source SHA-256 mismatch: expected {expected_sha}, found {actual_sha}"
        ]

    if validator == "cwe":
        errors.extend(validate_cwe(mapping, source))
    else:
        errors.extend(validate_atlas(mapping, source))
    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping-dir", type=Path, default=DEFAULT_MAPPING_DIR)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument(
        "--download",
        action="store_true",
        help="download a pinned source when it is absent from --source-dir",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    failed = False
    for filename in SUPPORTED_CATALOGS:
        path = args.mapping_dir / filename
        errors = validate_catalog(path, args.source_dir, args.download)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
