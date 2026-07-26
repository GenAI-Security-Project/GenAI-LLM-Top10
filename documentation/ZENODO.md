# Zenodo archival

The release workflow deposits each edition to Zenodo, which mints a DOI. Papers
cite that DOI, which lets us find them.

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
| [`.github/workflows/zenodo-release.yml`](../.github/workflows/zenodo-release.yml) | Runs the script on release, validates it on pull requests |

The script reads citation metadata from `CITATION.cff` at deposit time, so the
author list lives in one file.

## Adding an edition

`{edition}` in the config comes from the release tag. To publish the 2027
edition, add `2027/final/` and tag `v2027`. The config needs no change.

Update `CITATION.cff` with that edition's authors in the same release. The
workflow checks out the tag, so each version records the people who wrote that
edition, and the bundle carries a copy of `CITATION.cff` as it stood. Earlier
versions keep their own author lists, and the concept DOI shows the newest.

## Checking the bundle

```sh
pip install pyyaml requests
python .github/scripts/zenodo_release.py --check      # validate config and CITATION.cff
python .github/scripts/zenodo_release.py --dry-run    # list what would be deposited
python .github/scripts/test_zenodo_release.py         # deposit flow against a stubbed API
```

The workflow runs all three on pull requests that touch these files, and prints
the file listing to the run summary. The tests stub the Zenodo API, so they
check the request sequence and payloads but not whether Zenodo accepts the
metadata. A sandbox run is the only thing that proves that.

## Setup

1. Create a token with `deposit:write` and `deposit:actions` at
   <https://zenodo.org/account/settings/applications/tokens/new/>. Add it as the
   `ZENODO_TOKEN` repository secret.
2. Rehearse on sandbox: Actions > *Zenodo release* > **Run workflow**, with
   *sandbox* checked and *publish* unchecked. Zenodo cannot delete a published
   record, so get this right before the first real deposit.
3. After the first real publish, set the repository variable
   `ZENODO_CONCEPT_RECID` to the concept record id from the log. Without it,
   later releases create unrelated records and split the citation history.

## Releasing

Tag a GitHub release `v<edition>`, for example `v2026`. The workflow takes the
version from the tag and the date from the release, then deposits and publishes.

Afterwards, add the concept DOI to `CITATION.cff` (two commented `doi:` lines),
the README badge, and <https://genai.owasp.org/llm-top-10/>.
