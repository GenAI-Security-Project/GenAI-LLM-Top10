#!/usr/bin/env python3
"""Build a scoped edition bundle and deposit it to Zenodo.

    zenodo_release.py --check                     # validate config + CITATION.cff
    zenodo_release.py --edition 2026 --dry-run    # print the bundle contents
    zenodo_release.py --edition 2026 --sandbox    # deposit a draft to sandbox
    zenodo_release.py --edition 2026 --publish    # deposit and publish for real

File selection comes from .github/zenodo.config.json, citation metadata from
CITATION.cff. Neither names an edition, so a new edition needs no code change.

Each entry under `deposits` is a separate Zenodo record. Editions of one deposit
become versions of that record.

Environment:
    ZENODO_TOKEN    API token with `deposit:write`, plus `deposit:actions` to
                    publish.
    <concept_env>   Concept record id for one deposit, named by that deposit's
                    `concept_env` key. Set it after the first publish, otherwise
                    later releases create unrelated records.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / ".github" / "zenodo.config.json"
CITATION_PATH = REPO_ROOT / "CITATION.cff"
EDITION_RE = re.compile(r"(\d{4})")
TIMEOUT = 120


# --------------------------------------------------------------------------- #
# edition + config
# --------------------------------------------------------------------------- #

def discover_editions() -> list[str]:
    """Every NNNN/ directory in the repo that has a final/ subdirectory."""
    return sorted(
        p.name
        for p in REPO_ROOT.iterdir()
        if p.is_dir() and re.fullmatch(r"\d{4}", p.name) and (p / "final").is_dir()
    )


def resolve_edition(requested: str | None) -> str:
    """Read the edition from the argument (a tag like `v2026` works), or fall
    back to the newest edition in the repo."""
    editions = discover_editions()
    if not editions:
        sys.exit("error: no NNNN/final/ directory found in the repository")
    if not requested:
        print(f"no edition given, using the newest in the repo: {editions[-1]}")
        return editions[-1]
    match = EDITION_RE.search(requested)
    if not match:
        sys.exit(f"error: cannot read an edition year from {requested!r}")
    edition = match.group(1)
    if edition not in editions:
        sys.exit(f"error: {edition}/final/ does not exist (found: {', '.join(editions)})")
    return edition


def load_config() -> dict:
    if not CONFIG_PATH.is_file():
        sys.exit(f"error: missing {CONFIG_PATH.relative_to(REPO_ROOT)}")
    config = json.loads(CONFIG_PATH.read_text())
    if not config.get("deposits"):
        sys.exit("error: config has no `deposits`")
    return config


def select_deposits(config: dict, requested: str | None) -> dict:
    """All deposits, or just the one named."""
    deposits = config["deposits"]
    if not requested:
        return deposits
    if requested not in deposits:
        sys.exit(f"error: unknown deposit {requested!r} (have: {', '.join(deposits)})")
    return {requested: deposits[requested]}


def load_citation() -> dict:
    try:
        import yaml
    except ImportError:
        sys.exit("error: PyYAML is required (pip install pyyaml)")
    if not CITATION_PATH.is_file():
        sys.exit("error: missing CITATION.cff")
    return yaml.safe_load(CITATION_PATH.read_text())


# --------------------------------------------------------------------------- #
# CITATION.cff -> Zenodo metadata
# --------------------------------------------------------------------------- #

def as_zenodo_person(entry: dict) -> dict:
    """Convert a CFF author to a Zenodo creator. Entities keep their `name`."""
    if "name" in entry:
        person = {"name": entry["name"]}
    else:
        family = entry.get("family-names", "").strip()
        given = entry.get("given-names", "").strip()
        person = {"name": f"{family}, {given}".strip(", ")}
    if entry.get("affiliation"):
        person["affiliation"] = entry["affiliation"]
    if entry.get("orcid"):
        person["orcid"] = entry["orcid"].rsplit("/", 1)[-1]
    return person


def build_metadata(cff: dict, deposit: dict, edition: str, publication_date: str | None) -> dict:
    # `$`-prefixed keys are comments for maintainers, not Zenodo fields.
    configured = {
        k: v for k, v in deposit.get("metadata", {}).items() if not k.startswith("$")
    }
    people = cff.get("authors", [])
    creators = [as_zenodo_person(a) for a in people if "name" not in a]
    entities = [as_zenodo_person(a) for a in people if "name" in a]

    abstract = " ".join(cff.get("abstract", cff["title"]).split())
    url = cff.get("url")

    metadata: dict = {
        **configured,
        "title": cff["title"],
        "description": f"<p>{abstract}</p>"
        + (f'<p>Project site: <a href="{url}">{url}</a></p>' if url else ""),
        "version": edition,
        "creators": creators,
        "keywords": cff.get("keywords", []),
    }
    if cff.get("license"):
        metadata["license"] = cff["license"].lower()
    if publication_date:
        metadata["publication_date"] = publication_date
    elif cff.get("date-released"):
        metadata["publication_date"] = str(cff["date-released"])
    # Contributors listed in the config come first, then organisations named as
    # authors in CITATION.cff.
    contributors = list(configured.get("contributors", []))
    contributors += [{**e, "type": "HostingInstitution"} for e in entities]
    if contributors:
        metadata["contributors"] = contributors
    if url:
        metadata.setdefault("related_identifiers", []).append(
            {"identifier": url, "relation": "isSupplementTo", "scheme": "url"}
        )
    return metadata


# --------------------------------------------------------------------------- #
# bundle
# --------------------------------------------------------------------------- #

def collect_files(deposit: dict, edition: str) -> list[Path]:
    bundle = deposit["bundle"]
    includes = [p.format(edition=edition) for p in bundle["include"]]
    excludes = [p.format(edition=edition) for p in bundle.get("exclude", [])]

    selected: list[Path] = []
    for entry in includes:
        target = REPO_ROOT / entry
        if target.is_file():
            selected.append(target)
        elif target.is_dir():
            selected.extend(sorted(p for p in target.rglob("*") if p.is_file()))
        else:
            sys.exit(f"error: include path not found: {entry}")

    kept = []
    for path in selected:
        rel = path.relative_to(REPO_ROOT).as_posix()
        if any(fnmatch.fnmatch(rel, pattern) for pattern in excludes):
            continue
        kept.append(path)
    if not kept:
        sys.exit("error: bundle is empty, check `include`/`exclude` in the config")
    return kept


def write_bundle(files: list[Path], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(REPO_ROOT).as_posix())
    return destination


def report_bundle(files: list[Path], stream=sys.stdout) -> None:
    total = sum(f.stat().st_size for f in files)
    print(f"{len(files)} files, {total / 1024:.0f} KiB", file=stream)
    for path in files:
        print(f"  {path.relative_to(REPO_ROOT).as_posix()}", file=stream)


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #

def check(config: dict, cff: dict) -> int:
    problems = []

    for field in ("title", "authors", "license"):
        if not cff.get(field):
            problems.append(f"CITATION.cff is missing `{field}`")

    # preferred-citation repeats the person list, and drift there produces a
    # citation that disagrees with the deposit. Entity authors map to Zenodo
    # contributors instead, so they appear in only one of the two lists.
    def people(entries):
        return [e for e in (entries or []) if "name" not in e]

    preferred = (cff.get("preferred-citation") or {}).get("authors")
    if preferred is not None and people(preferred) != people(cff.get("authors")):
        problems.append("CITATION.cff: `authors` and `preferred-citation.authors` differ")

    editions = discover_editions()
    if not editions:
        problems.append("no NNNN/final/ directory found")

    for name, deposit in config["deposits"].items():
        if not deposit.get("concept_env"):
            problems.append(f"deposit {name!r}: missing `concept_env`")
        for edition in editions:
            try:
                collect_files(deposit, edition)
            except SystemExit as exc:
                problems.append(f"deposit {name!r}, edition {edition}: {exc}")

    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    if problems:
        return 1
    print(
        f"OK. deposits: {', '.join(config['deposits'])}. "
        f"editions: {', '.join(editions)}"
    )
    return 0


# --------------------------------------------------------------------------- #
# Zenodo API
# --------------------------------------------------------------------------- #

def api_call(response, what: str) -> dict:
    if not response.ok:
        sys.exit(f"error: {what} failed ({response.status_code}): {response.text}")
    return response.json() if response.content else {}


def upload_url(draft: dict, base: str, filename: str) -> str:
    """The upload target for the bundle, once its host has been checked.

    Zenodo names the bucket in its own response. The token is about to be
    attached to that URL, so anything able to shape the response could otherwise
    redirect a `deposit:write` credential to a host of its choosing. Fail closed
    when the bucket does not sit on the API host the script chose.
    """
    bucket = (draft.get("links") or {}).get("bucket")
    if not bucket:
        sys.exit("error: Zenodo returned no bucket link for the draft")
    expected = urlparse(base).netloc
    found = urlparse(bucket).netloc
    if found != expected:
        sys.exit(f"error: bucket host {found!r} does not match the API host {expected!r}")
    return f"{bucket}/{filename}"


def deposit(
    bundle: Path,
    metadata: dict,
    concept_env: str,
    sandbox: bool,
    publish: bool,
) -> None:
    import requests

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        sys.exit("error: ZENODO_TOKEN is not set")
    base = "https://sandbox.zenodo.org/api" if sandbox else "https://zenodo.org/api"
    # A header rather than an `access_token` query parameter: query strings are
    # recorded by access logs, egress proxies and Referer headers.
    headers = {"Authorization": f"Bearer {token}"}
    concept = os.environ.get(concept_env)

    if concept:
        print(f"creating a new version of concept record {concept}")
        latest = api_call(
            requests.get(f"{base}/records/{concept}", headers=headers, timeout=TIMEOUT),
            "resolving concept record",
        )
        versioned = api_call(
            requests.post(
                f"{base}/deposit/depositions/{latest['id']}/actions/newversion",
                headers=headers,
                timeout=TIMEOUT,
            ),
            "creating new version",
        )
        draft_id = urlparse(versioned["links"]["latest_draft"]).path.rstrip("/").rsplit("/", 1)[-1]
        draft = api_call(
            requests.get(
                f"{base}/deposit/depositions/{draft_id}", headers=headers, timeout=TIMEOUT
            ),
            "fetching draft",
        )
        # Zenodo copies the previous version's files into a new version.
        for stale in draft.get("files", []):
            api_call(
                requests.delete(
                    f"{base}/deposit/depositions/{draft['id']}/files/{stale['id']}",
                    headers=headers,
                    timeout=TIMEOUT,
                ),
                f"removing inherited file {stale.get('filename')}",
            )
    else:
        print(f"{concept_env} is unset, creating the first deposition")
        draft = api_call(
            requests.post(
                f"{base}/deposit/depositions", headers=headers, json={}, timeout=TIMEOUT
            ),
            "creating deposition",
        )

    # Resolved before the file is opened, so a rejected host stops the run
    # without the token ever leaving the process.
    target = upload_url(draft, base, bundle.name)
    with bundle.open("rb") as handle:
        api_call(
            requests.put(target, data=handle, headers=headers, timeout=TIMEOUT),
            f"uploading {bundle.name}",
        )
    print(f"uploaded {bundle.name} ({bundle.stat().st_size} bytes)")

    draft = api_call(
        requests.put(
            f"{base}/deposit/depositions/{draft['id']}",
            headers=headers,
            json={"metadata": metadata},
            timeout=TIMEOUT,
        ),
        "updating metadata",
    )

    if not publish:
        print(f"draft ready for review: {draft['links'].get('html')}")
        return

    published = api_call(
        requests.post(
            f"{base}/deposit/depositions/{draft['id']}/actions/publish",
            headers=headers,
            timeout=TIMEOUT,
        ),
        "publishing",
    )
    print(f"version DOI: {published.get('doi')}")
    print(f"concept DOI (cite this): {published.get('conceptdoi')}")
    if not concept:
        print(f"Next step: set {concept_env}={published.get('conceptrecid')}")


# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edition", help="edition or tag, e.g. 2026 or v2026. default: newest")
    parser.add_argument("--deposit", help="deposit key from the config; default: all")
    parser.add_argument("--publication-date", help="ISO date; default: CITATION.cff")
    parser.add_argument("--out", default=Path("dist"), type=Path, help="bundle output directory")
    parser.add_argument("--check", action="store_true", help="validate config and exit")
    parser.add_argument("--dry-run", action="store_true", help="build and list, do not deposit")
    parser.add_argument("--sandbox", action="store_true", help="use sandbox.zenodo.org")
    parser.add_argument("--publish", action="store_true", help="publish instead of leaving a draft")
    args = parser.parse_args()

    config = load_config()
    cff = load_citation()

    if args.check:
        sys.exit(check(config, cff))

    edition = resolve_edition(args.edition)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")

    for name, spec in select_deposits(config, args.deposit).items():
        print(f"\n=== deposit {name!r}, edition {edition} ===")
        files = collect_files(spec, edition)
        report_bundle(files)

        if summary_path:
            with open(summary_path, "a") as handle:
                print(f"### {name}, edition {edition}\n\n```", file=handle)
                report_bundle(files, stream=handle)
                print("```", file=handle)

        bundle_name = spec["bundle"]["name"].format(edition=edition)
        bundle = write_bundle(files, args.out / f"{bundle_name}.zip")

        if args.dry_run:
            print(f"dry run: wrote {bundle}, nothing deposited")
            continue

        deposit(
            bundle,
            build_metadata(cff, spec, edition, args.publication_date),
            concept_env=spec["concept_env"],
            sandbox=args.sandbox,
            publish=args.publish,
        )


if __name__ == "__main__":
    main()
