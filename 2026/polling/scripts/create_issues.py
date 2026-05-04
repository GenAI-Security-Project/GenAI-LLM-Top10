#!/usr/bin/env python3
"""
OWASP Top 10 for LLM Applications — 2026 Update
Sprint 2: Bulk-create the 18 feedback issues (10 Track A + 8 Track B).

Owner:    Rock Lambros (rock@rockcyber.ai)
Version:  1.0
Repo:     GenAI-Security-Project/GenAI-LLM-Top10

WHAT THIS DOES
  1. Ensures the 22 Sprint 2 labels exist in the repo (idempotent — creates
     missing, leaves existing alone, updates color/description on existing).
  2. Creates one feedback issue per existing entry (10) and per candidate (8).
  3. Substitutes the Track A and Track B Form URLs into each issue body.

USAGE
  export GH_TOKEN="ghp_..."          # PAT with `repo` scope
  python create_issues.py \\
      --form-url "https://docs.google.com/forms/d/e/1FAIpQLSebmFQyJPOMuw1IorHCJ2FdW98ZT2oLNBuVgYqpPoayW9v6ww/viewform" \\
      --dry-run                      # render without posting

  Run without --dry-run to fire for real. Issues post sequentially with a
  short pause to stay under GitHub's secondary rate limits.

  --form-url is a single Google Form URL covering both tracks. Sprint 2
  consolidated to one ballot so voters land on a single URL and roll from
  Track A into Track B in one captive session. The live URL is also
  recorded in issues.json under _meta.form.published_url.

EXIT CODES
  0  success
  1  configuration error (missing token, missing args, missing file)
  2  GitHub API error (after creating any issues, prints which ones succeeded)

DEPENDENCIES
  Python 3.9+ stdlib only. No third-party packages.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO = "GenAI-Security-Project/GenAI-LLM-Top10"
API_BASE = "https://api.github.com"
RATE_PAUSE_SEC = 1.0  # between issue creates
TIMEOUT_SEC = 30
SCRIPT_DIR = Path(__file__).resolve().parent
ISSUES_PATH = SCRIPT_DIR / "issues.json"

# ---------- HTTP ----------

def _request(method: str, path: str, token: str, body: dict | None = None) -> tuple[int, Any]:
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "owasp-llm-top10-2026-sprint2-issue-creator/1.0")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8") or "null")
        except Exception:
            err_body = {"message": str(e)}
        return e.code, err_body

# ---------- Labels ----------

def ensure_labels(labels: list[dict], token: str, dry_run: bool) -> None:
    print(f"[labels] ensuring {len(labels)} labels in {REPO}")
    for label in labels:
        name, color, desc = label["name"], label["color"], label["description"]
        if dry_run:
            print(f"  [dry-run] would upsert label {name!r} color={color}")
            continue

        # Try to create. If it exists, patch.
        status, body = _request("POST", f"/repos/{REPO}/labels", token, {
            "name": name, "color": color, "description": desc,
        })
        if status == 201:
            print(f"  + created label {name}")
        elif status == 422:  # already exists
            status_p, _ = _request(
                "PATCH",
                f"/repos/{REPO}/labels/{urllib.parse.quote(name)}",
                token,
                {"new_name": name, "color": color, "description": desc},
            )
            if status_p == 200:
                print(f"  ~ updated existing label {name}")
            else:
                print(f"  ! could not update label {name} (status {status_p})")
        else:
            print(f"  ! error creating label {name}: status {status} body {body}")
            sys.exit(2)

# ---------- Issue bodies ----------

TRACK_A_BODY = """## Sprint 2 Feedback — {entry_id} {entry_title}

This issue collects **qualitative feedback** on the refreshed **{entry_id} {entry_title}** entry. \
Submit your **Importance** and **Clarity** scores via the Sprint 2 Google Form (single ballot covering both tracks).

- **Vote**: {form_url} — page through to the **{entry_id}** section
- **Read the draft**: https://github.com/{repo}/blob/main/2026/{file}
- **Voting closes**: May 18, 2026 at 23:59 UTC
- **Code of Conduct**: https://owasp.org/www-policy/operational/code-of-conduct

### Scoring rubric

- **Importance** (1–5): How critical is this risk to LLM application security in 2026?
- **Clarity** (1–5): How clearly does the entry describe the risk and its mitigations?

### How to comment

Reply to this issue with feedback specific to **{entry_id}**. Use one comment per topic so the working group can triage cleanly. Format we like:

```
Section: <which section of the entry>
Issue: <what is wrong, missing, or unclear>
Proposed change: <your suggested fix or addition>
Evidence: <CVE, paper, incident, or research note ID if applicable>
```

### Out of scope here

- Cross-cutting comments → use [Discussions]({discussions_url})
- Questions about Track B candidates → comment on the relevant Track B issue
- Process or governance questions → comment in [Discussions]({discussions_url})

### Triage

Working group entry leads classify each comment within 48 hours as:
- **actionable** — feeds Sprint 3 revision
- **clarification** — requires reply, not action
- **out-of-scope** — closed with redirect

Sprint 3 begins May 18 with this issue's triage as input.
"""

TRACK_B_BODY = """## Sprint 2 Feedback — {entry_title}

This issue collects **qualitative feedback** on the **{entry_title}** new candidate entry. \
Submit your **Importance**, **Clarity**, and **Distinctness** scores via the Sprint 2 Google Form (single ballot covering both tracks).

- **Vote**: {form_url} — page through to the Track B section, then to **{entry_title}**
- **Read the draft**: https://github.com/{repo}/blob/main/2026/new_entry_candidates/{file}
- **Voting closes**: May 18, 2026 at 23:59 UTC
- **Code of Conduct**: https://owasp.org/www-policy/operational/code-of-conduct

### Scoring rubric

- **Importance** (1–5): How critical is this risk to LLM application security in 2026?
- **Clarity** (1–5): How clearly does the candidate describe the risk and mitigations?
- **Distinctness** (1–5): Is this materially different from existing entries (LLM01–LLM10), or could it be merged into one of them?

### Why Distinctness matters

Sprint 3 cuts 8 candidates down to 5. A high-Importance candidate that overlaps heavily with an existing entry is a merge target, not a standalone winner. Distinctness scores let the working group make defensible cut, keep, or merge calls.

### How to comment

Reply to this issue with feedback specific to **{entry_title}**. Use one comment per topic so the working group can triage cleanly. Format we like:

```
Section: <which section of the candidate>
Issue: <what is wrong, missing, unclear, or duplicative>
Proposed change: <your suggested fix, addition, or merge target>
Overlaps with: <existing entry LLM01–LLM10 if applicable>
Evidence: <CVE, paper, incident, or research note ID if applicable>
```

### Out of scope here

- Cross-cutting comments → use [Discussions]({discussions_url})
- Comments on existing entries (LLM01–LLM10) → comment on the relevant Track A issue
- Process or governance questions → comment in [Discussions]({discussions_url})

### Triage

Working group entry leads classify each comment within 48 hours as:
- **actionable** — feeds Sprint 3 revision or merge decision
- **clarification** — requires reply, not action
- **out-of-scope** — closed with redirect

Sprint 3 begins May 18 with this issue's triage as input.
"""

DISCUSSIONS_URL = f"https://github.com/{REPO}/discussions"

# ---------- Issue creation ----------

def render_track_a(entry: dict, form_url: str) -> tuple[str, str]:
    title = f"[Track A] Feedback: {entry['id']} — {entry['title']}"
    body = TRACK_A_BODY.format(
        entry_id=entry["id"],
        entry_title=entry["title"],
        file=entry["file"],
        repo=REPO,
        form_url=form_url,
        discussions_url=DISCUSSIONS_URL,
    )
    return title, body

def render_track_b(entry: dict, form_url: str) -> tuple[str, str]:
    title = f"[Track B] Feedback: {entry['title']}"
    body = TRACK_B_BODY.format(
        entry_title=entry["title"],
        file=entry["file"],
        repo=REPO,
        form_url=form_url,
        discussions_url=DISCUSSIONS_URL,
    )
    return title, body

def post_issue(title: str, body: str, labels: list[str], token: str, dry_run: bool) -> int | None:
    if dry_run:
        print(f"  [dry-run] would create issue: {title}")
        print(f"             labels: {labels}")
        return None
    status, response = _request("POST", f"/repos/{REPO}/issues", token, {
        "title": title, "body": body, "labels": labels,
    })
    if status == 201:
        num = response.get("number")
        url = response.get("html_url")
        print(f"  + #{num} {title}")
        print(f"     {url}")
        return num
    print(f"  ! failed to create {title!r}: status {status} body {response}")
    return None

# ---------- Main ----------

def main() -> int:
    parser = argparse.ArgumentParser(description="Create Sprint 2 feedback issues.")
    parser.add_argument("--form-url", required=True, help="Published URL for the Sprint 2 Google Form (single ballot, both tracks)")
    parser.add_argument("--dry-run", action="store_true", help="Render but do not post.")
    parser.add_argument("--issues-file", default=str(ISSUES_PATH), help="Path to issues.json")
    parser.add_argument("--skip-labels", action="store_true", help="Skip the label upsert step.")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token and not args.dry_run:
        print("ERROR: set GH_TOKEN or GITHUB_TOKEN before running.", file=sys.stderr)
        return 1

    issues_file = Path(args.issues_file)
    if not issues_file.exists():
        print(f"ERROR: issues file not found at {issues_file}", file=sys.stderr)
        return 1

    config = json.loads(issues_file.read_text())
    print(f"OWASP Top 10 LLM 2026 — Sprint 2 issue creator (dry_run={args.dry_run})")
    print(f"  repo:     {REPO}")
    print(f"  form url: {args.form_url}")
    print(f"  track A:  {len(config['track_a'])} issues")
    print(f"  track B:  {len(config['track_b'])} issues")

    if not args.skip_labels:
        ensure_labels(config["labels"], token or "", args.dry_run)

    print("[track-a] creating issues")
    for entry in config["track_a"]:
        title, body = render_track_a(entry, args.form_url)
        post_issue(title, body, ["sprint-2", "track-a", "feedback", entry["id"]],
                   token or "", args.dry_run)
        if not args.dry_run:
            time.sleep(RATE_PAUSE_SEC)

    print("[track-b] creating issues")
    for entry in config["track_b"]:
        title, body = render_track_b(entry, args.form_url)
        post_issue(title, body, ["sprint-2", "track-b", "feedback", entry["id"]],
                   token or "", args.dry_run)
        if not args.dry_run:
            time.sleep(RATE_PAUSE_SEC)

    print("done.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
