#!/usr/bin/env python3
"""Offline tests for the cross-framework mapping validator."""

from __future__ import annotations

import copy
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_mappings as validator  # noqa: E402


def cwe_source(version: str = "4.20") -> bytes:
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Weakness_Catalog xmlns="http://cwe.mitre.org/cwe-7" Version="{version}">
  <Weaknesses>
    <Weakness ID="79" Name="Cross-site Scripting" Abstraction="Base" />
  </Weaknesses>
</Weakness_Catalog>
""".encode()
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w") as archive:
        archive.writestr(f"cwec_v{version}.xml", xml)
    return result.getvalue()


def atlas_source(
    content_version: str = "2026.06", format_version: str = "6.0.0"
) -> bytes:
    return f"""format-version: {format_version}
collection:
  name: ATLAS
  version: '{content_version}'
tactics:
  AML.TA0000:
    name: AI Model Access
    id: AML.TA0000
    object-type: tactic
techniques: {{}}
""".encode()


class MappingValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.mapping_dir = self.root / "mappings"
        self.source_dir = self.root / "sources"
        self.mapping_dir.mkdir()
        self.source_dir.mkdir()

        cwe_bytes = cwe_source()
        atlas_bytes = atlas_source()
        (self.source_dir / "cwec_v4.20.xml.zip").write_bytes(cwe_bytes)
        (self.source_dir / "ATLAS-2026.06.yaml").write_bytes(atlas_bytes)

        self.cwe_mapping = {
            "framework": "MITRE CWE (Common Weakness Enumeration)",
            "version": "4.20",
            "source_url": "https://cwe.mitre.org/data/xml/cwec_v4.20.xml.zip",
            "source_sha": validator.sha256(cwe_bytes),
            "elements": [{"id": "CWE-79", "title": "Cross-site Scripting (Base)"}],
        }
        self.atlas_mapping = {
            "framework": "MITRE ATLAS",
            "version": "content v2026.06 (format-version 6.0.0)",
            "source_url": (
                "https://raw.githubusercontent.com/mitre-atlas/atlas-data/"
                "main/dist/v6/ATLAS-2026.06.yaml"
            ),
            "source_sha": validator.sha256(atlas_bytes),
            "elements": [{"id": "AML.TA0000", "title": "AI Model Access"}],
        }
        self.write_catalogs()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_catalogs(self) -> None:
        (self.mapping_dir / "cwe-4.20.json").write_text(
            json.dumps(self.cwe_mapping), encoding="utf-8"
        )
        (self.mapping_dir / "mitre-atlas-2026.06.json").write_text(
            json.dumps(self.atlas_mapping), encoding="utf-8"
        )

    def errors_for(self, filename: str) -> list[str]:
        return validator.validate_catalog(
            self.mapping_dir / filename, self.source_dir, download=False
        )

    def test_valid_catalogs_pass_offline(self) -> None:
        self.assertEqual([], self.errors_for("cwe-4.20.json"))
        self.assertEqual([], self.errors_for("mitre-atlas-2026.06.json"))

    def test_nonexistent_identifier_fails(self) -> None:
        self.cwe_mapping["elements"][0]["id"] = "CWE-999999"
        self.write_catalogs()
        self.assertTrue(
            any("identifier not found" in error for error in self.errors_for("cwe-4.20.json"))
        )

    def test_duplicate_identifier_fails(self) -> None:
        self.cwe_mapping["elements"].append(
            copy.deepcopy(self.cwe_mapping["elements"][0])
        )
        self.write_catalogs()
        self.assertTrue(
            any("duplicate element id" in error for error in self.errors_for("cwe-4.20.json"))
        )

    def test_title_mismatch_fails(self) -> None:
        self.atlas_mapping["elements"][0]["title"] = "ML Model Access"
        self.write_catalogs()
        self.assertTrue(
            any("title mismatch" in error for error in self.errors_for("mitre-atlas-2026.06.json"))
        )

    def test_cwe_abstraction_mismatch_fails(self) -> None:
        self.cwe_mapping["elements"][0]["title"] = "Cross-site Scripting (Class)"
        self.write_catalogs()
        self.assertTrue(
            any("title mismatch" in error for error in self.errors_for("cwe-4.20.json"))
        )

    def test_source_version_mismatch_fails(self) -> None:
        mismatched = atlas_source(content_version="2025.10")
        (self.source_dir / "ATLAS-2026.06.yaml").write_bytes(mismatched)
        self.atlas_mapping["source_sha"] = validator.sha256(mismatched)
        self.write_catalogs()
        self.assertTrue(
            any(
                "content version mismatch" in error
                for error in self.errors_for("mitre-atlas-2026.06.json")
            )
        )

    def test_source_sha_mismatch_fails(self) -> None:
        self.cwe_mapping["source_sha"] = "sha256:" + ("0" * 64)
        self.write_catalogs()
        self.assertTrue(
            any("SHA-256 mismatch" in error for error in self.errors_for("cwe-4.20.json"))
        )

    def test_deprecated_atlas_path_fails(self) -> None:
        self.atlas_mapping["source_url"] = (
            "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.yaml"
        )
        self.write_catalogs()
        self.assertTrue(
            any(
                "pinned v6 source" in error
                for error in self.errors_for("mitre-atlas-2026.06.json")
            )
        )


if __name__ == "__main__":
    unittest.main()
