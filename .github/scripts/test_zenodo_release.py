#!/usr/bin/env python3
"""Tests for zenodo_release.py.

Runs the deposit flow against a stubbed Zenodo API, so it needs no token and
makes no network calls. This covers the request sequence, URLs and payloads.
It cannot prove that Zenodo accepts the metadata; only a sandbox run does that.

    python .github/scripts/test_zenodo_release.py
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zenodo_release as z  # noqa: E402

CALLS: list[tuple[str, str, dict]] = []
FAILURES: list[str] = []


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self._payload = payload
        self.status_code = status
        self.ok = status < 400
        self.content = json.dumps(payload).encode()
        self.text = json.dumps(payload)

    def json(self) -> dict:
        return self._payload


def draft_payload(
    deposit_id: int = 111,
    files: list | None = None,
    bucket_base: str = "https://zenodo.org/api",
) -> dict:
    # Zenodo returns the bucket on its own host. `bucket_base` lets a test hand
    # back a foreign host instead, which the script must refuse to upload to.
    return {
        "id": deposit_id,
        "files": files or [],
        "links": {
            "bucket": f"{bucket_base}/files/bucket-{deposit_id}",
            "html": f"https://example.invalid/deposit/{deposit_id}",
            "latest_draft": f"https://example.invalid/api/deposit/depositions/{deposit_id}",
        },
    }


def install_fake_requests(
    concept_exists: bool,
    inherited: list | None = None,
    bucket_base: str = "https://zenodo.org/api",
) -> None:
    """Swap in a `requests` module that records calls and returns canned data."""

    def record(method):
        def call(url, **kwargs):
            CALLS.append((method, url, kwargs))
            if method == "GET" and "/records/" in url:
                return FakeResponse({"id": 999})
            if method == "GET" and "/deposit/depositions/" in url:
                return FakeResponse(draft_payload(111, inherited, bucket_base))
            if method == "POST" and url.endswith("/actions/newversion"):
                return FakeResponse(draft_payload(111, inherited, bucket_base))
            if method == "POST" and url.endswith("/actions/publish"):
                return FakeResponse(
                    {
                        "doi": "10.5281/zenodo.222",
                        "conceptdoi": "10.5281/zenodo.221",
                        "conceptrecid": "221",
                    }
                )
            if method == "POST" and url.endswith("/deposit/depositions"):
                return FakeResponse(draft_payload(111, None, bucket_base))
            if method == "DELETE":
                return FakeResponse({})
            return FakeResponse(draft_payload(111, inherited, bucket_base))

        return call

    fake = types.ModuleType("requests")
    for verb in ("get", "post", "put", "delete"):
        setattr(fake, verb, record(verb.upper()))
    sys.modules["requests"] = fake


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label} {detail}")
        FAILURES.append(label)


def sequence() -> list[tuple[str, str]]:
    return [(m, u.split("/api", 1)[-1] if "/api" in u else u) for m, u, _ in CALLS]


def check_token(label: str) -> None:
    """Assert the token reached every call site of one run as a header.

    `CALLS` resets at the top of `run()`, so this has to be called after each
    run. The concept-record path carries four call sites the first run never
    reaches, and they went unasserted while this lived inline.
    """
    # The token belongs in a header. Query strings reach access logs, egress
    # proxies and Referer headers, all of which outlive the request.
    check(
        f"token sent as an Authorization Bearer header ({label})",
        all((k.get("headers") or {}).get("Authorization") == "Bearer fake-token" for _, _, k in CALLS),
    )
    check(
        f"token never reaches a query string ({label})",
        not any(
            "access_token" in u or "access_token" in (k.get("params") or {})
            for _, u, k in CALLS
        ),
    )


def build_inputs():
    """Bundle and metadata, rebuilt from the repository each time."""
    config = z.load_config()
    cff = z.load_citation()
    spec = config["deposits"]["top10"]
    files = z.collect_files(spec, "2026")
    bundle = z.write_bundle(files, Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp") / "t.zip")
    return bundle, z.build_metadata(cff, spec, "2026", "2026-06-15")


def set_env(concept: str | None) -> None:
    import os

    os.environ["ZENODO_TOKEN"] = "fake-token"
    if concept:
        os.environ["TEST_CONCEPT"] = concept
    else:
        os.environ.pop("TEST_CONCEPT", None)


def run(
    name: str,
    *,
    concept: str | None,
    publish: bool,
    sandbox: bool,
    inherited=None,
    bucket_base: str | None = None,
):
    global CALLS
    CALLS = []
    base = "https://sandbox.zenodo.org/api" if sandbox else "https://zenodo.org/api"
    install_fake_requests(bool(concept), inherited, bucket_base or base)
    set_env(concept)

    bundle, metadata = build_inputs()
    print(f"\n{name}")
    z.deposit(bundle, metadata, concept_env="TEST_CONCEPT", sandbox=sandbox, publish=publish)
    return metadata


# --------------------------------------------------------------------------- #

md = run("first deposit, publish, production", concept=None, publish=True, sandbox=False)
seq = sequence()
check("creates a deposition", ("POST", "/deposit/depositions") in seq)
check("does not call newversion", not any("newversion" in u for _, u in seq))
check("uploads to the bucket URL", any(m == "PUT" and "files/bucket" in u for m, u in seq))
check("publishes", any(u.endswith("/actions/publish") for _, u in seq))
# Every request now goes to the API host, the bucket upload included, so this
# covers the whole run. A foreign URL fails here rather than being filtered out.
urls = [u for _, u, _ in CALLS]
check("uses the production API base", urls and all(u.startswith("https://zenodo.org/api") for u in urls))
put_meta = [k for m, u, k in CALLS if m == "PUT" and "depositions" in u]
check("sends metadata under a `metadata` key", bool(put_meta) and "metadata" in put_meta[0]["json"])
sent = put_meta[0]["json"]["metadata"]
check("no $-prefixed comment keys reach Zenodo", not any(k.startswith("$") for k in sent))
check("license is the Zenodo vocabulary id", sent["license"] == "cc-by-sa-4.0", sent.get("license"))
check("upload_type/publication_type set", (sent["upload_type"], sent["publication_type"]) == ("publication", "report"))
check("publication_date is ISO8601", sent["publication_date"] == "2026-06-15")
check("creators are 'Family, Given'", sent["creators"][0]["name"] == "Wilson, Steve")
# Not a fixed number: the author list changes with each edition. What matters
# is that every person in CITATION.cff reaches Zenodo, and the order survives.
people = [a for a in z.load_citation()["authors"] if "name" not in a]
check("every author is deposited", len(sent["creators"]) == len(people), str(len(sent["creators"])))
check("author order survives", sent["creators"][-1]["name"] == "Klondike, Gavin")
check("contributor type is valid", sent["contributors"][0]["type"] == "HostingInstitution")
check_token("first deposit")

run(
    "new version with inherited files, sandbox, draft only",
    concept="221",
    publish=False,
    sandbox=True,
    inherited=[{"id": "f1", "filename": "old.zip"}],
)
seq = sequence()
check("resolves the concept record", any(m == "GET" and "/records/221" in u for m, u in seq))
check("creates a new version", any(u.endswith("/actions/newversion") for _, u in seq))
check("deletes the inherited file", any(m == "DELETE" and u.endswith("/files/f1") for m, u in seq))
check("uploads the new bundle", any(m == "PUT" and "files/bucket" in u for m, u in seq))
check("does NOT publish in draft mode", not any(u.endswith("/actions/publish") for _, u in seq))
urls = [u for _, u, _ in CALLS]
check("uses the sandbox API base", urls and all(u.startswith("https://sandbox.zenodo.org/api") for u in urls))
check("never touches production", not any(u.startswith("https://zenodo.org/api") for u in urls))
# The concept path adds four call sites the first run never reaches: the record
# GET, the newversion POST, the draft GET and the inherited-file DELETE.
check_token("new version")

# The bucket URL arrives in Zenodo's response. Attaching the token to whatever
# host it names would hand the credential to anyone who can shape that response.
def refuse(name: str, bucket_base: str) -> str:
    """Run a deposit that must fail closed, and return why it exited.

    The reason matters: a bare `except SystemExit` also catches the missing
    bucket link and every API error, so it would pass with the host check gone.
    """
    global CALLS
    CALLS = []
    install_fake_requests(False, None, bucket_base)
    set_env(None)
    bundle, metadata = build_inputs()
    print(f"\n{name}")
    try:
        z.deposit(bundle, metadata, concept_env="TEST_CONCEPT", sandbox=False, publish=True)
        return ""
    except SystemExit as exc:
        return str(exc)


why = refuse("bucket URL on a host the script did not verify", "https://evil.invalid/api")
check("refuses on a host mismatch", "does not match the API host" in why, why or "no SystemExit")
check("sends nothing to the foreign host", not any("evil.invalid" in u for _, u, _ in CALLS))
check("does not publish", not any(u.endswith("/actions/publish") for _, u, _ in CALLS))

# Right host, wrong scheme. Comparing netloc alone lets this through, and the
# token then crosses the network in cleartext.
why = refuse("bucket URL on the API host over http", "http://zenodo.org/api")
check("refuses on a plaintext bucket URL", "is not https" in why, why or "no SystemExit")
check("sends the token over no cleartext URL", not any(u.startswith("http://") for _, u, _ in CALLS))
check("does not publish over http", not any(u.endswith("/actions/publish") for _, u, _ in CALLS))

print()
if FAILURES:
    print(f"{len(FAILURES)} failed: {', '.join(FAILURES)}")
    sys.exit(1)
print("all checks passed")
