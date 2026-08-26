# Zenodo archival

Each edition is deposited to Zenodo, which mints a DOI. Papers cite that DOI,
which lets us find them.

We deposit through the Zenodo API rather than Zenodo's GitHub integration,
because we publish a subset of the repository and expect more than one product
from it.

## How editions map to DOIs

Editions are versions of one Zenodo record. Each version gets its own DOI, and
Zenodo groups them under a concept DOI that resolves to the newest edition.

Cite the concept DOI. Readers who need a specific edition can use the version
DOI on that record's page. [DataCite's versioning
guidance](https://support.datacite.org/docs/versioning) describes the same
approach.

A separate publication from this repo would get its own entry under `deposits`
and its own concept DOI, rather than becoming a version of this one.

## Files

| File | Role |
| --- | --- |
| [`CITATION.cff`](../CITATION.cff) | Authors, title, licence, keywords |
| [`.github/zenodo.config.json`](../.github/zenodo.config.json) | Which files go into each deposit |
| [`.github/scripts/zenodo_release.py`](../.github/scripts/zenodo_release.py) | Builds the bundle and deposits it |

No workflow is wired to CI yet, so the script is run by hand. See
[Setup](#setup) and [Releasing](#releasing).

The script reads citation metadata from `CITATION.cff` at deposit time, so the
author list lives in one file.

## Adding an edition

`{edition}` is passed on the command line. To publish the 2027 edition, add
`2027/final/` and run the script with `--edition 2027`. The config needs no
change.

Update `CITATION.cff` with that edition's authors in the same release, and build
the bundle from a committed revision rather than a dirty working tree, so the
deposit matches something anyone can check out. Earlier versions keep their own
author lists, and the concept DOI shows the newest.

## Checking the bundle

```sh
pip install pyyaml requests
python .github/scripts/zenodo_release.py --check      # validate config and CITATION.cff
python .github/scripts/zenodo_release.py --dry-run    # list what would be deposited
python .github/scripts/test_zenodo_release.py         # deposit flow against a stubbed API
```

The tests stub the Zenodo API, so they check the request sequence and payloads
but not whether Zenodo accepts the metadata. A sandbox run is the only thing
that proves that.

## The 2026 record

The 2026 edition was deposited by hand on 26 August 2026.

| | |
| --- | --- |
| Record | <https://zenodo.org/records/22109015> |
| Concept DOI (cite this) | [10.5281/zenodo.22109014](https://doi.org/10.5281/zenodo.22109014) |
| Version DOI (2026 only) | [10.5281/zenodo.22109015](https://doi.org/10.5281/zenodo.22109015) |
| Files | the published PDF, and a source bundle built from `origin/main` |

Two things about that record are worth knowing before the next edition.

The author list and its order come from the Acknowledgements page of the
published PDF, not from this repository. That page is the authoritative credit
for an edition, and `CITATION.cff` is kept in step with it.

The published PDF is not in this repository, so the bundle in
`.github/zenodo.config.json` does not include it. It was uploaded by hand. An
automated release would deposit the source bundle alone unless the PDF is
committed under `<edition>/final/` first.

## Setup

The deposit runs from a laptop, not from CI. Automating it means putting a
Zenodo API token in a repository secret, and that token carries the identity of
whoever minted it: it can publish under their name, and any repository admin can
use it. Decide who owns the record before wiring that up.

1. Create a token with `deposit:write` and `deposit:actions` at
   <https://zenodo.org/account/settings/applications/tokens/new/>, and export it
   as `ZENODO_TOKEN`.
2. Rehearse against sandbox with `--sandbox` and without `--publish`. Zenodo
   cannot delete a published record, so get this right first.
3. Export `ZENODO_CONCEPT_RECID=22109014` so the deposit becomes a new version of
   the existing record. Without it the script creates an unrelated record and
   splits the citation history.

## Releasing

Add `<edition>/final/`, update `CITATION.cff` with that edition's authors, then:

```sh
export ZENODO_TOKEN=...
export ZENODO_CONCEPT_RECID=22109014
python .github/scripts/zenodo_release.py --edition 2027 --publish
```

The version DOI changes, the concept DOI does not. Afterwards, update the README
badge and <https://genai.owasp.org/llm-top-10/> if the citation text changed.
