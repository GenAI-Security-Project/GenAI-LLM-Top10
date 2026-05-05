# Mid-Sprint Form Update Guide

Owner: Rock Lambros
Use case: Edits to existing entries, new candidate entries, or both, while keeping the live Form URL stable.

## Recommended workflow: dynamic sync

The team pushes entry changes (text edits, file renames, new candidates) directly to `main`. Run one Python command and one Apps Script function. No manual array editing. No manual issue firing.

```bash
cd /Users/klambros/github_projects/GenAI-LLM-Top10
git pull                                 # not strictly required (script reads remote)
export GH_TOKEN=$(gh auth token)

# Preview what would change
python3 2026/polling/scripts/sync_sprint2.py --dry-run

# Apply: updates issues.json, fires only missing GitHub issues
python3 2026/polling/scripts/sync_sprint2.py

# Push the updated registry so Apps Script can fetch it
git add 2026/polling/scripts/issues.json
git commit -m "Sprint 2: sync entry registry"
git push
```

Then in Apps Script:

1. Open the existing project (the one tied to the live Form).
2. Run `rebuildSprintTwoFormDynamic()`. It fetches the updated `issues.json` from raw.githubusercontent.com and rebuilds the form against it.
3. Form URL stays the same. Voters keep using the same link.

That's it. Two commands, one click in Apps Script.

## What the sync script does

Reads from the **remote repo on `main`** (not your local clone, which may be stale):

1. Lists `2026/` and detects existing entries (LLM01 through LLM10). Excludes `LLM00_Preface.md`.
2. Lists `2026/new_entry_candidates/` and detects Track A candidates.
3. Pulls each markdown file's first heading and parses out the human title.
4. For new candidates, auto-generates a stable `TA-XXXX` ID from the filename slug (first letter of up to 4 words). For renamed candidates, reuses the existing ID from the registry.
5. Diffs against the local `issues.json` registry. Reports what's new, changed (file rename or title edit), or removed.
6. Updates `issues.json` with the reconciled state. Adds labels for any new candidate IDs.
7. Fetches existing GitHub issues with `label:sprint-2`. For any entry without an issue, fires a new one (using the existing issue body templates).

Source of truth: the remote repo. Local `issues.json` is a derived registry that gets committed for traceability and to feed Apps Script.

## Flags

| Flag | Effect |
| --- | --- |
| `--dry-run` | Show diff and proposed actions without writing or firing |
| `--no-fire` | Update `issues.json` but skip creating new GitHub issues |
| `--no-write` | Read-only — don't update `issues.json`. Useful with `--no-fire` to inspect remote |
| `--branch BRANCH` | Read from a branch other than `main` |
| `--form-url URL` | Override the form URL for new issues (defaults to `_meta.form.published_url` in `issues.json`) |

## Removals: handled with care

If a file disappears from the remote (e.g., a candidate dropped from consideration), the sync script:

- Reports it under `[-] REMOVED` with a warning.
- Does NOT auto-delete the entry from `issues.json`.
- Does NOT close the corresponding GitHub issue.

This is intentional. Auto-removing entries mid-sprint loses the votes already collected for them. If you genuinely want to drop an entry:

1. Manually edit `issues.json` to remove the entry from `track_b` or `track_a`.
2. Comment on the corresponding GitHub issue explaining the working group decision and close it.
3. Re-run `sync_sprint2.py` to verify clean state.

## When NOT to run sync

| Voting state | Safe to sync? |
| --- | --- |
| Just launched, single-digit responses | Yes |
| Active turnout, 10 to 25 responses | Mostly safe. Form rebuild changes question IDs, but new responses still flow into the Sheet's right-hand columns. Aggregation handles the merge. |
| 25+ responses | Run only if the team genuinely needs the change. Coordinate with the working group. |

The form rebuild changes question IDs every time. Old responses keep their old column data; new responses get fresh columns. Aggregation reconciles by entry ID, so this is workable. But every rebuild adds reconciliation overhead.

## Manual fallback paths

If the sync script breaks for any reason, you have two manual paths:

### Surgical path (most conservative)

Open the form via the Edit URL. Click into individual sections to update titles or links. Append new sections at the end of Track A. No script needed. Slow but lossless.

### Static rebuild path

Edit `TRACK_B_ENTRIES` and `TRACK_A_ENTRIES` in `create_form.gs` by hand. Paste the script into Apps Script. Run `rebuildSprintTwoForm()` (the static version). Then manually update `issues.json` and run `create_issues.py --only-ids "TA-NEWX"` for new candidates.

This is the path the static `rebuildSprintTwoForm()` and `create_issues.py --only-ids` were originally built for. They still work. The sync script is just a higher-level wrapper.

## Verification after sync

After running sync and the Apps Script rebuild, sanity-check:

1. Open the form's published URL. Page through. Confirm the new candidates appear and the renames look right.
2. Check the GitHub issue list filtered by `label:sprint-2`. Count should match the entry count in the new `issues.json`.
3. Check the Discussion. Pinned content shouldn't need updating unless category descriptions changed.

If anything looks off, re-run `sync_sprint2.py --dry-run` to see what the script thinks the current state is. The diff is your debugger.

## What the rebuild changes vs preserves

| Asset | Preserved | Notes |
| --- | --- | --- |
| Form URL (Published, Short, Edit) | Yes | Same Form ID, same URLs |
| Form title and description | Refreshed from script | If you changed `FORM_TITLE` or `buildDescription()`, those update |
| Voter metadata page (About You) | Wiped and rebuilt | Question IDs change; affects column mapping |
| Per-entry sections | Wiped and rebuilt | Same |
| Submitted responses | Stay in Sheet | Old responses sit in old columns; new ones go to fresh columns |
| Linked response Sheet | Stays linked | Aggregation pipeline handles column reconciliation by entry ID |
| Form ID | Unchanged | Aggregation pipeline still finds the Sheet via Form ID |
