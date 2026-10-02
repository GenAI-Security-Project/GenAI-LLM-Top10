# Mapping Integrity Validation

The mapping integrity validator currently supports the CWE 4.20 and MITRE
ATLAS 2026.06 catalogs. It checks:

* Duplicate identifiers in a mapping catalog.
* Identifier existence in the corresponding primary dataset.
* Exact title and abstraction metadata for CWE entries.
* Exact tactic names for MITRE ATLAS entries.
* The self-reported source version and format version.
* The SHA-256 digest of every downloaded or cached primary dataset.
* Use of the pinned MITRE ATLAS v6 source instead of the deprecated default
  `dist/ATLAS.yaml` file.

Run the validator locally:

```bash
python .github/scripts/validate_mappings.py --download
```

The first run downloads the version-specific primary datasets into
`.cache/mapping-sources/`. Later runs can validate entirely offline by omitting
`--download`:

```bash
python .github/scripts/validate_mappings.py
```

Run the offline negative test cases separately:

```bash
python .github/scripts/test_validate_mappings.py
```

Each supported mapping records `source_url` and `source_sha`. When a framework
source is intentionally updated, review its contents and version metadata,
update the mapping, and replace `source_sha` with the SHA-256 digest of the
exact source bytes.
