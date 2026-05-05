#!/usr/bin/env python3
"""
OWASP Top 10 for LLM Applications — 2026 Update
sync_sprint2.py — Reconcile Sprint 2 state with the REMOTE GitHub repo.

Owner:   Rock Lambros (rock@rockcyber.ai)
Version: 1.0
Repo:    GenAI-Security-Project/GenAI-LLM-Top10

WHAT THIS DOES
  Reads everything from the REMOTE repo at run time:
    - 2026/                          (existing entries: LLM01_*.md ... LLM10_*.md)
    - 2026/new_entry_candidates/     (Track A candidates: *.md)
    - 2026/polling/scripts/issues.json  (the registry baseline)

  Computes a fresh registry from the markdown source-of-truth, diffs it
  against the remote registry, and produces a new local issues.json plus
  the GitHub issue mutations needed to bring the live world in sync.

  Auto-generates stable TA-XXXX IDs for new candidates (preserving any
  IDs already in the registry). Updates existing GitHub issues for
  renamed/edited entries (PATCH title and body). Creates new GitHub
  issues for newly added candidates. Skips unchanged entries.

  Source of truth: REMOTE main, every run.
  Local registry:  polling/scripts/issues.json — write-only output.

WHY FULLY REMOTE
  Multiple team members can push entry edits to main concurrently. Your
  local clone may be stale even if you just pulled. Reading the registry
  from REMOTE ensures the diff reflects whatever main looks like at the
  exact moment the script runs, not whatever your local cache last saw.

USAGE
  export GH_TOKEN=$(gh auth token)

  # Preview what would change without modifying anything:
  python3 sync_sprint2.py --dry-run

  # Apply the reconciliation:
  python3 sync_sprint2.py

  # After applying, commit issues.json and push so Apps Script can fetch:
  git add 2026/polling/scripts/issues.json
  git commit -m "Sprint 2: sync entry registry"
  git push

  # Then in Apps Script, run rebuildSprintTwoFormDynamic() to refresh
  # the form. URL stays the same.

OPTIONS
  --dry-run         Show diff and proposed changes without writing or firing
  --no-fire         Update issues.json but skip firing new GitHub issues
  --branch BRANCH   Read from a branch other than main (default: main)
  --no-write        Skip writing to issues.json (useful with --no-fire to
                    just see what's on remote)

EXIT CODES
  0  success
  1  configuration error (no token, can't reach API, etc.)
  2  GitHub API error during reconciliation or firing

DEPENDENCIES
  Python 3.9+ stdlib only. No third-party packages.
  Imports issue-firing helpers from create_issues.py (same directory).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

# Reuse helpers from create_issues so the issue body templates and label
# upsert logic stay in one place.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import create_issues  # type: ignore  # noqa: E402

# ---------- Configuration ----------

REPO = "GenAI-Security-Project/GenAI-LLM-Top10"
API_BASE = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
TIMEOUT_SEC = 30
RATE_PAUSE_SEC = 1.0

ISSUES_PATH = SCRIPT_DIR / "issues.json"

EXISTING_DIR_PATH = "2026"
CANDIDATE_DIR_PATH = "2026/new_entry_candidates"
REGISTRY_REPO_PATH = "2026/polling/scripts/issues.json"

# Existing entries are LLM01..LLM10. LLM00_Preface and similar non-votable
# files are excluded.
EXISTING_FILE_RE = re.compile(r"^(LLM(?:0[1-9]|10))_.*\.md$")

# Filenames in the candidate directory we should ignore (templates, hidden, etc.)
CANDIDATE_IGNORE = {"_template.md", ".gitkeep"}

# Label color for new auto-created TB candidate labels.
TB_LABEL_COLOR = "D4C5F9"

# ---------- HTTP ----------

def _request(method: str, url: str, token: str | None,
             body: dict | None = None) -> tuple[int, Any, dict]:
    """Returns (status, parsed_body, headers_dict)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "owasp-llm-top10-sprint2-sync/1.0")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw) if raw and resp.headers.get("Content-Type", "").startswith("application/json") else raw
            return resp.status, parsed, dict(resp.headers)
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8") or "null")
        except Exception:
            err_body = {"message": str(e)}
        return e.code, err_body, dict(e.headers or {})


def _raw_fetch(url: str, token: str | None) -> str:
    """Fetch a raw URL (e.g. raw.githubusercontent.com). Returns text body."""
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "owasp-llm-top10-sprint2-sync/1.0")
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        return resp.read().decode("utf-8")


# ---------- Remote repo readers ----------

def list_directory(path: str, branch: str, token: str | None) -> list[dict]:
    """List files in a repo directory via the GitHub Contents API."""
    url = f"{API_BASE}/repos/{REPO}/contents/{urllib.parse.quote(path)}?ref={urllib.parse.quote(branch)}"
    status, body, _ = _request("GET", url, token)
    if status != 200:
        print(f"ERROR listing {path} on {branch}: status {status} body {body}", file=sys.stderr)
        sys.exit(2)
    return [item for item in body if isinstance(item, dict)]


def fetch_markdown(path: str, branch: str, token: str | None) -> str:
    """Fetch the raw text of a markdown file from the repo."""
    url = f"{RAW_BASE}/{REPO}/{branch}/{urllib.parse.quote(path)}"
    return _raw_fetch(url, token)


def fetch_remote_registry(branch: str, token: str | None) -> dict | None:
    """Fetch issues.json from the remote repo. Returns None if missing or
    invalid (e.g., first run before registry was committed)."""
    try:
        url = f"{RAW_BASE}/{REPO}/{branch}/{urllib.parse.quote(REGISTRY_REPO_PATH)}"
        text = _raw_fetch(url, token)
        return json.loads(text)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except json.JSONDecodeError as e:
        print(f"WARNING: remote {REGISTRY_REPO_PATH} is invalid JSON: {e}", file=sys.stderr)
        return None


# ---------- Entry parsing ----------

_HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")


def parse_first_heading(text: str) -> str:
    """Extract the first markdown heading at any level (#, ##, ### etc).
    Returns empty string if no heading found."""
    for line in text.splitlines():
        m = _HEADING_RE.match(line.strip())
        if m:
            return m.group(1).strip()
    return ""


def humanize_existing_title(filename: str, heading: str, entry_id: str) -> str:
    """Extract the human title from an existing-entry heading.
    Handles formats:
      'LLM01:2026 Prompt Injection'  -> 'Prompt Injection'
      'LLM01: 2026 Prompt Injection' -> 'Prompt Injection'
      'LLM01: Misinformation'        -> 'Misinformation'
      'LLM01 Prompt Injection'       -> 'Prompt Injection'
      'Prompt Injection'             -> 'Prompt Injection'
    """
    if not heading:
        return filename.replace(".md", "").split("_", 1)[-1]
    # Strip optional 'LLMXX' prefix, optional ':', optional 'YYYY ' year tag.
    # Capture the rest as the title.
    m = re.match(rf"^{entry_id}\s*:?\s*(?:\d{{4}}\s+)?(.+)$", heading)
    if m:
        return m.group(1).strip()
    return heading.strip()


def filename_to_humanized(filename: str) -> str:
    """Fallback title from a candidate slug: kebab-case to Title Case."""
    base = filename.replace(".md", "")
    words = base.replace("_", "-").split("-")
    return " ".join(w.capitalize() for w in words if w)


def slug_to_ta_id_base(slug: str) -> str:
    """Generate a base TA-XXXX ID from a candidate filename slug.
    First letter of up to 4 words. May collide; caller resolves."""
    words = [w for w in re.split(r"[-_]", slug) if w]
    initials = "".join(w[0] for w in words[:4]).upper()
    if len(initials) < 2:
        initials = (slug[:4] or "X").upper()
    return f"TA-{initials}"


def assign_candidate_id(filename: str, known: dict[str, str], used: set[str]) -> str:
    """Use the existing ID if known, otherwise auto-generate with collision resolution."""
    if filename in known:
        return known[filename]
    base = slug_to_ta_id_base(filename.replace(".md", ""))
    eid = base
    suffix = 2
    while eid in used:
        eid = f"{base}{suffix}"
        suffix += 1
    return eid


# ---------- Remote -> registry ----------

def load_existing_from_remote(branch: str, token: str | None) -> list[dict]:
    """Read existing entries (LLM01..LLM10) from remote 2026/.
    Excludes LLM00_Preface.md and any non-LLMXX files."""
    items = list_directory(EXISTING_DIR_PATH, branch, token)
    entries: list[dict] = []
    for item in items:
        if item.get("type") != "file":
            continue
        name = item["name"]
        m = EXISTING_FILE_RE.match(name)
        if not m:
            continue
        eid = m.group(1)
        text = fetch_markdown(f"{EXISTING_DIR_PATH}/{name}", branch, token)
        heading = parse_first_heading(text)
        title = humanize_existing_title(name, heading, eid)
        entries.append({"id": eid, "title": title, "file": name})
    entries.sort(key=lambda e: e["id"])
    return entries


def load_candidates_from_remote(branch: str, token: str | None,
                                known: dict[str, str]) -> tuple[list[dict], list[str]]:
    """Read Track A candidates from remote 2026/new_entry_candidates/.
    Returns (entries, warnings)."""
    items = list_directory(CANDIDATE_DIR_PATH, branch, token)
    entries: list[dict] = []
    warnings: list[str] = []
    used_ids = set(known.values())

    for item in items:
        if item.get("type") != "file":
            continue
        name = item["name"]
        if name in CANDIDATE_IGNORE or name.startswith("."):
            continue
        if not name.endswith(".md"):
            continue

        text = fetch_markdown(f"{CANDIDATE_DIR_PATH}/{name}", branch, token)
        heading = parse_first_heading(text)
        title = heading or filename_to_humanized(name)

        eid = assign_candidate_id(name, known, used_ids)
        used_ids.add(eid)
        if name not in known:
            warnings.append(f"NEW candidate: {name} -> {eid} ({title})")

        entries.append({"id": eid, "title": title, "file": name})
    entries.sort(key=lambda e: e["id"])
    return entries, warnings


# ---------- Reconciliation ----------

def _diff_track(local: list[dict], current: list[dict]) -> tuple[list[dict], list[tuple[dict, dict]], list[dict]]:
    """Diff one track. Keys by entry ID (stable) so file renames register
    as a 'changed' rather than add+remove. Returns (new, changed, removed)."""
    cur_by_id = {e["id"]: e for e in current}
    local_by_id = {e["id"]: e for e in local}

    new = [e for e in local if e["id"] not in cur_by_id]

    changed: list[tuple[dict, dict]] = []
    for e in local:
        if e["id"] in cur_by_id:
            old = cur_by_id[e["id"]]
            if (old.get("file") != e["file"]
                    or old.get("title") != e["title"]):
                changed.append((old, e))

    removed = [e for e in current if e["id"] not in local_by_id]

    return new, changed, removed


def reconcile(local_b: list[dict], local_a: list[dict], config: dict) -> dict:
    """Compute the diff between remote-derived state and the current registry."""
    new_b, changed_b, removed_b = _diff_track(local_b, config.get("track_b", []))
    new_a, changed_a, removed_a = _diff_track(local_a, config.get("track_a", []))
    return {
        "new_b": new_b, "new_a": new_a,
        "changed_b": changed_b, "changed_a": changed_a,
        "removed_b": removed_b, "removed_a": removed_a,
    }


# ---------- GitHub issue lookup ----------

def fetch_issues_with_label(label: str, token: str) -> list[dict]:
    """Page through issues with given label (open + closed)."""
    issues: list[dict] = []
    page = 1
    while True:
        url = (f"{API_BASE}/repos/{REPO}/issues?"
               f"labels={urllib.parse.quote(label)}&state=all&per_page=100&page={page}")
        status, body, _ = _request("GET", url, token)
        if status != 200:
            print(f"ERROR fetching issues with label {label}: {status} {body}", file=sys.stderr)
            sys.exit(2)
        if not isinstance(body, list) or not body:
            break
        issues.extend(body)
        if len(body) < 100:
            break
        page += 1
    # GitHub /issues returns PRs too; filter them out
    return [i for i in issues if "pull_request" not in i]


def covered_entry_ids(issues: list[dict]) -> set[str]:
    """Extract entry-ID labels (LLM01-10 or TA-XXXX) from a list of issues."""
    covered: set[str] = set()
    for issue in issues:
        for label in issue.get("labels", []):
            name = label["name"] if isinstance(label, dict) else label
            if re.match(r"^(LLM\d{2}|TA-[A-Z0-9]+)$", name):
                covered.add(name)
    return covered


def issues_by_entry_id(issues: list[dict]) -> dict[str, dict]:
    """Map entry ID -> issue dict. If multiple issues share the same entry
    label, the first one wins (lowest ID, since GitHub returns newest first
    by default we explicitly sort)."""
    issues_sorted = sorted(issues, key=lambda i: i.get("number", 0))
    by_id: dict[str, dict] = {}
    for issue in issues_sorted:
        for label in issue.get("labels", []):
            name = label["name"] if isinstance(label, dict) else label
            if re.match(r"^(LLM\d{2}|TA-[A-Z0-9]+)$", name) and name not in by_id:
                by_id[name] = issue
    return by_id


def patch_issue(number: int, title: str, body: str, token: str) -> bool:
    """PATCH an existing issue's title and body. Returns True on success."""
    url = f"{API_BASE}/repos/{REPO}/issues/{number}"
    status, resp, _ = _request("PATCH", url, token, {"title": title, "body": body})
    if status != 200:
        print(f"    ! patch #{number} failed: status {status} body {resp}", file=sys.stderr)
        return False
    return True


# ---------- Output ----------

def print_diff(diff: dict, warnings: list[str]) -> bool:
    """Print the diff. Returns True if there are changes to apply."""
    has_changes = any([diff["new_b"], diff["new_a"],
                       diff["changed_b"], diff["changed_a"],
                       diff["removed_b"], diff["removed_a"]])

    print("=" * 60)
    print("RECONCILIATION DIFF")
    print("=" * 60)

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    def show_added(label, lst):
        if lst:
            print(f"\n[+] NEW in {label}:")
            for e in lst:
                print(f"      {e['id']:8s} {e['title']}  ({e['file']})")

    def show_changed(label, lst):
        if lst:
            print(f"\n[~] CHANGED in {label}:")
            for old, new in lst:
                print(f"      {new['id']}:")
                if old.get("file") != new["file"]:
                    print(f"        file:  {old.get('file','?')} -> {new['file']}")
                if old.get("title") != new["title"]:
                    print(f"        title: {old.get('title','?')!r}")
                    print(f"            -> {new['title']!r}")

    def show_removed(label, lst):
        if lst:
            print(f"\n[-] REMOVED from {label} (file no longer in remote):")
            for e in lst:
                print(f"      {e['id']:8s} {e['title']}  ({e['file']})")
            print(f"      WARNING: removals are NOT auto-applied. Verify manually.")

    show_added("Track B", diff["new_b"])
    show_added("Track A", diff["new_a"])
    show_changed("Track B", diff["changed_b"])
    show_changed("Track A", diff["changed_a"])
    show_removed("Track B", diff["removed_b"])
    show_removed("Track A", diff["removed_a"])

    if not has_changes and not warnings:
        print("\nNo changes. Remote state matches local registry.")

    print("=" * 60)
    return has_changes


# ---------- Apply changes ----------

def build_updated_config(local_b: list[dict], local_a: list[dict], config: dict) -> dict:
    """Build a new config dict with updated track_b and track_a, plus any new labels."""
    new_config = dict(config)
    new_config["track_b"] = local_b
    new_config["track_a"] = local_a

    # Ensure each entry ID has a corresponding label entry
    existing_label_names = {l["name"] for l in config.get("labels", [])}
    new_labels = list(config.get("labels", []))
    for e in local_a:
        if e["id"] not in existing_label_names:
            new_labels.append({
                "name": e["id"],
                "color": TB_LABEL_COLOR,
                "description": e["title"],
            })
            existing_label_names.add(e["id"])
    # Update label descriptions if title changed
    name_to_label = {l["name"]: l for l in new_labels}
    for e in local_a:
        if e["id"] in name_to_label:
            name_to_label[e["id"]]["description"] = e["title"]

    new_config["labels"] = new_labels
    return new_config


def write_config(config: dict) -> None:
    ISSUES_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def sync_github_issues(config: dict, diff: dict, form_url: str, token: str,
                       dry_run: bool, existing_issues: list[dict]) -> dict:
    """Two-phase sync against GitHub issues:
       1. UPDATE existing issues for entries that changed (rename, title edit)
       2. CREATE issues for entries that don't have one yet
    Returns a summary dict.
    """
    summary: dict[str, list[str]] = {
        "updated": [],
        "created": [],
        "skipped_unchanged": [],
        "missing_after_rename": [],
    }

    if not dry_run:
        # Idempotent label upsert
        create_issues.ensure_labels(config["labels"], token, dry_run=False)

    issue_by_id = issues_by_entry_id(existing_issues)

    # ---- Phase 1: UPDATE changed entries ----
    changed_entries: list[tuple[str, dict, dict]] = []
    for old, new in diff.get("changed_b", []):
        changed_entries.append(("a", old, new))
    for old, new in diff.get("changed_a", []):
        changed_entries.append(("b", old, new))

    if changed_entries:
        print("\n[issues] updating existing issues for changed entries...")
        for track, old, new in changed_entries:
            issue = issue_by_id.get(new["id"])
            if not issue:
                summary["missing_after_rename"].append(new["id"])
                print(f"    ! {new['id']} marked changed but no existing issue with that label found. Will create below.")
                continue
            renderer = create_issues.render_track_b if track == "a" else create_issues.render_track_a
            new_title, new_body = renderer(new, form_url)
            issue_num = issue["number"]
            if dry_run:
                print(f"    [dry-run] would update #{issue_num}:")
                print(f"        title: {issue.get('title','?')!r}")
                print(f"            -> {new_title!r}")
            else:
                if patch_issue(issue_num, new_title, new_body, token):
                    print(f"    ~ updated #{issue_num}: {new_title}")
                    time.sleep(RATE_PAUSE_SEC)
            summary["updated"].append(new["id"])

    # ---- Phase 2: CREATE issues for entries with no coverage ----
    covered = set(issue_by_id.keys())
    print("\n[issues] firing for entries missing a GitHub issue...")
    for entry in config["track_b"]:
        if entry["id"] in covered:
            if entry["id"] not in summary["updated"]:
                summary["skipped_unchanged"].append(entry["id"])
            continue
        title, body = create_issues.render_track_b(entry, form_url)
        labels = ["sprint-2", "track-b", "feedback", entry["id"]]
        if dry_run:
            print(f"    [dry-run] would create: {title}")
        else:
            create_issues.post_issue(title, body, labels, token, dry_run=False)
            time.sleep(RATE_PAUSE_SEC)
        summary["created"].append(entry["id"])

    for entry in config["track_a"]:
        if entry["id"] in covered:
            if entry["id"] not in summary["updated"]:
                summary["skipped_unchanged"].append(entry["id"])
            continue
        title, body = create_issues.render_track_a(entry, form_url)
        labels = ["sprint-2", "track-a", "feedback", entry["id"]]
        if dry_run:
            print(f"    [dry-run] would create: {title}")
        else:
            create_issues.post_issue(title, body, labels, token, dry_run=False)
            time.sleep(RATE_PAUSE_SEC)
        summary["created"].append(entry["id"])

    return summary


# ---------- Main ----------

def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile Sprint 2 with the remote repo.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show diff and proposed actions without writing or firing.")
    parser.add_argument("--no-fire", action="store_true",
                        help="Update issues.json but skip firing new GitHub issues.")
    parser.add_argument("--no-write", action="store_true",
                        help="Do not write to issues.json (useful with --no-fire to inspect remote).")
    parser.add_argument("--branch", default="main",
                        help="Read from a branch other than main (default: main).")
    parser.add_argument("--form-url", default=None,
                        help="Override Form URL for new issues. Defaults to "
                             "issues.json _meta.form.published_url.")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("WARNING: no GH_TOKEN or GITHUB_TOKEN set. "
              "Anonymous reads work for public repos but rate limits will apply, "
              "and writes will fail.", file=sys.stderr)

    print(f"Sprint 2 sync (branch={args.branch}, dry_run={args.dry_run})")
    print(f"  repo:     {REPO}")
    print(f"  registry: {ISSUES_PATH}  (write target)")
    print()

    # Phase 1: read remote state — both the markdown source-of-truth AND the registry
    print(f"[remote] fetching registry from {REGISTRY_REPO_PATH} on {args.branch}...")
    config = fetch_remote_registry(args.branch, token)
    if config is None:
        # First run, or registry not yet committed. Fall back to a minimal
        # config so the rest of the pipeline can still run.
        if ISSUES_PATH.exists():
            print(f"         remote registry missing; falling back to local {ISSUES_PATH}")
            config = json.loads(ISSUES_PATH.read_text(encoding="utf-8"))
        else:
            print(f"         remote registry missing AND no local fallback. Bootstrapping empty.")
            config = {"_meta": {}, "labels": [], "track_b": [], "track_a": []}
    else:
        print(f"         pulled remote registry: "
              f"{len(config.get('track_b', []))} Track B, "
              f"{len(config.get('track_a', []))} Track A")

    print("[remote] listing existing entries...")
    local_b = load_existing_from_remote(args.branch, token)
    print(f"         found {len(local_b)} entries in {EXISTING_DIR_PATH}/")

    print("[remote] listing candidates...")
    known_ids = {e["file"]: e["id"] for e in config.get("track_a", [])}
    local_a, warnings = load_candidates_from_remote(args.branch, token, known_ids)
    print(f"         found {len(local_a)} entries in {CANDIDATE_DIR_PATH}/")

    # Phase 2: diff
    diff = reconcile(local_b, local_a, config)
    has_changes = print_diff(diff, warnings)

    # Phase 3: build updated config
    new_config = build_updated_config(local_b, local_a, config)

    # Phase 4: write registry
    if not has_changes:
        print("\nRegistry already in sync. No write needed.")
    elif args.no_write:
        print("\n[--no-write] skipping registry update.")
    elif args.dry_run:
        print("\n[--dry-run] would write updated registry to issues.json.")
    else:
        write_config(new_config)
        print(f"\n[write] updated {ISSUES_PATH}")

    # Phase 5: fire missing issues
    if args.no_fire:
        print("\n[--no-fire] skipping issue creation.")
        return 0

    if not token and not args.dry_run:
        print("\nERROR: cannot fire issues without GH_TOKEN. "
              "Run with --no-fire or set GH_TOKEN.", file=sys.stderr)
        return 1

    form_url = args.form_url or new_config.get("_meta", {}).get("form", {}).get("published_url")
    if not form_url:
        print("\nERROR: no form URL available. Pass --form-url or "
              "ensure _meta.form.published_url is set in issues.json.", file=sys.stderr)
        return 1

    print(f"\n[issues] checking which entries already have a GitHub issue...")
    if token:
        existing = fetch_issues_with_label("sprint-2", token)
        print(f"         {len(existing)} sprint-2 issues found")
    else:
        existing = []
        print(f"         no token, can't enumerate existing issues "
              f"(use --dry-run to preview without writes)")

    summary = sync_github_issues(new_config, diff, form_url,
                                  token or "", args.dry_run, existing)

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Updated existing issues: {len(summary['updated'])} {summary['updated']}")
    print(f"  Created new issues:      {len(summary['created'])} {summary['created']}")
    print(f"  Unchanged (skipped):     {len(summary['skipped_unchanged'])}")
    if summary["missing_after_rename"]:
        print(f"  WARNING — IDs marked as changed but no existing issue: "
              f"{summary['missing_after_rename']}")
        print(f"  These were re-created above (look for '[create]' lines).")
    print()

    if not args.dry_run and (has_changes or summary["created"] or summary["updated"]):
        print("NEXT STEPS:")
        print("  1. git add 2026/polling/scripts/issues.json")
        print("  2. git commit -m 'Sprint 2: sync entry registry'")
        print("  3. git push")
        print("  4. In Apps Script, run rebuildSprintTwoFormDynamic() to refresh the form.")
        print("     URL stays unchanged.")
        print("  5. Spot-check the live form, the GitHub issues filter, and the pinned Discussion.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
