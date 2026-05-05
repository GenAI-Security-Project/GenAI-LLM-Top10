# Tomorrow Morning Runbook: Sync, Refresh, Launch

Owner: Rock Lambros
When: Morning of May 5, 2026, before any LinkedIn or Slack posts go out.
Total time: about 30 minutes start to finish.

This is your runbook. It assumes you'll let Claude Code do anything against GitHub via the gh CLI it already has. Phases that need a browser (Apps Script, posting to LinkedIn) are flagged explicitly.

Each phase has a clear checkpoint. Stop between phases if anything looks wrong.

## How to use this document

1. Open one terminal window.
2. Open one Chrome/browser tab (you'll need it for Apps Script and posting comms).
3. For each phase below, copy the **command** or **prompt** in the code block and paste it where indicated.
4. Read the output carefully before moving to the next phase.

When the doc says "**Claude Code prompt**", paste the entire code block into a Claude Code session. Claude Code uses your existing gh CLI auth — no token paste required.

When the doc says "**Browser**", switch to your browser tab and do exactly what's described.

## Files and locations referenced in this runbook

| Thing | Where |
| --- | --- |
| Local repo | `/Users/klambros/github_projects/GenAI-LLM-Top10` |
| Sync script | `2026/polling/scripts/sync_sprint2.py` |
| Issue creation script (fallback) | `2026/polling/scripts/create_issues.py` |
| Form Apps Script source | `2026/polling/forms/create_form.gs` |
| Live registry (write target) | `2026/polling/scripts/issues.json` |
| Pinned Discussion | https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/discussions/54 |
| Form Edit URL | https://docs.google.com/forms/d/1lNZHaqUQC_A9DJeSy9JJ1FQkzE1T-lA92vbJLoE6K_k/edit |
| Form Published URL | https://docs.google.com/forms/d/e/1FAIpQLSebmFQyJPOMuw1IorHCJ2FdW98ZT2oLNBuVgYqpPoayW9v6ww/viewform |
| Form Short URL | https://forms.gle/jFmqZF1R6k9gCEfi6 |
| Apps Script editor | https://script.google.com |

# Phase 0: Open Claude Code

**Terminal:**

```bash
cd /Users/klambros/github_projects/GenAI-LLM-Top10
claude
```

You should now be in a Claude Code session with the working directory set to the repo root.

# Phase 1: Pre-flight

Verifies gh CLI auth, pulls latest main so the eventual `git push` doesn't conflict, and shows the current registry baseline so you know what state you're starting from.

**Claude Code prompt:**

```
Pre-flight check for the OWASP Sprint 2 sync. Do all of these and STOP. Do NOT run the sync yet.

1. Verify gh CLI is authenticated:
   gh auth status

   Tell me what you see. If "not logged in", stop and tell me to run `gh auth login`.

2. Switch to main and pull:
   git checkout main
   git pull origin main

   Tell me if the pull succeeded and whether anything came down.

3. Show the current Track B and Track A entry counts in the LOCAL registry:
   python3 -c "
   import json
   d = json.load(open('2026/polling/scripts/issues.json'))
   print('Track B:', len(d['track_b']))
   print('Track A:', len(d['track_a']))
   for e in d['track_b']: print(' ', e['id'], e['title'])
   for e in d['track_a']: print(' ', e['id'], e['title'])
   "

4. Print 'PHASE 1 COMPLETE — READY FOR PHASE 2'.

STOP. Do not proceed to any sync action.
```

**Checkpoint:** You should see gh auth status as logged in, a clean `git pull`, and a list of the current 18 entries. If anything errors out, fix that before moving on.

# Phase 2: Preview the diff

Reads everything from remote main at run time. Shows you exactly what would change. Writes nothing, fires nothing.

**Claude Code prompt:**

```
Run a dry-run sync against the OWASP Sprint 2 repo. Show me the full output. Do NOT apply.

Steps:
1. Set GH_TOKEN from gh CLI:
   export GH_TOKEN=$(gh auth token)

2. Run the sync in dry-run mode:
   python3 2026/polling/scripts/sync_sprint2.py --dry-run

3. After it finishes, summarize for me:
   - How many entries are NEW in Track B and Track A (from the [+] NEW sections)
   - How many entries CHANGED (file rename or title edit, from the [~] CHANGED sections)
   - How many entries REMOVED (warnings only, from the [-] REMOVED section)
   - Total new GitHub issues that would fire
   - Total existing GitHub issues that would be PATCHed

4. Print 'PHASE 2 COMPLETE — REVIEW THE DIFF, THEN GIVE ME GO TO PROCEED'.

STOP. Do not apply. Wait for my explicit "go".
```

**Checkpoint:** Read Claude Code's summary carefully.

Things to check:

- New candidate IDs look reasonable (auto-generated as initials of the filename slug)
- Changed entries match what the team told you they were updating
- No removals you weren't expecting
- Issue counts make sense

**If anything is off**, stop here and either fix the underlying repo state or tell me what's weird. Do not proceed.

**If everything is right**, type "go" or "proceed" in Claude Code and continue to Phase 3.

# Phase 3: Apply the sync

Updates `issues.json`, PATCHes existing GitHub issues, creates new ones, commits, pushes.

**Claude Code prompt:**

```
Apply the OWASP Sprint 2 sync. Run the same script without --dry-run. Then commit and push the registry. Walk me through the output.

Steps:
1. Make sure GH_TOKEN is still exported (re-run if needed):
   export GH_TOKEN=$(gh auth token)

2. Run the sync for real:
   python3 2026/polling/scripts/sync_sprint2.py

3. Show me the output, especially the SUMMARY block at the end. Tell me:
   - How many existing issues were updated (PATCHed)
   - How many new issues were created
   - The list of entry IDs in each category

4. Show the git diff of issues.json (just the file list and stat, not the full contents):
   git diff --stat 2026/polling/scripts/issues.json

5. Commit and push the registry:
   git add 2026/polling/scripts/issues.json
   git commit -m "Sprint 2: sync entry registry against remote state"
   git push origin main

6. Tell me the commit SHA and confirm the push succeeded.

7. Print 'PHASE 3 COMPLETE — REGISTRY ON MAIN, ISSUES UPDATED, READY FOR FORM REFRESH'.

STOP after the push. Do not touch the form yet.
```

**Checkpoint:** You should see:

- Sync summary showing the right number of updates and creates
- git diff stat showing `issues.json` modified
- Commit succeeded
- Push succeeded

**If the push is rejected** (someone else pushed first), Claude Code will tell you. The fix is `git pull --rebase`, resolve any conflicts on `issues.json` (yours wins; the script regenerated it), then push again.

# Phase 4: Refresh the Google Form (browser)

This is the only phase that requires the browser. About 3 minutes.

**Browser:**

### 4.1 — Open Apps Script

Go to https://script.google.com.

You should see your existing project (probably named "OWASP LLM Top 10 — Sprint 2 Voting Form" or similar). Click it.

### 4.2 — Make sure the script is current

Open `2026/polling/forms/create_form.gs` from your local repo in any text editor (or open it in the GitHub web view). Compare against what's in Apps Script's `Code.gs`.

Quick check: scroll to the bottom of `Code.gs` in Apps Script. Look for a function named `rebuildSprintTwoFormDynamic`.

- If it's there, your Apps Script is current. Skip to step 4.3.
- If it's NOT there, your Apps Script is stale. Copy the entire contents of `2026/polling/forms/create_form.gs` from your local repo and paste it into `Code.gs`, replacing everything. Save (Ctrl/Cmd + S).

### 4.3 — Run the dynamic rebuild

In Apps Script:

1. In the toolbar, find the function-selector dropdown.
2. Click it. Select `rebuildSprintTwoFormDynamic`.
3. Click the Run button (▶).
4. Watch the Execution log at the bottom.

Expected output:

```
Fetched registry from remote:
  Track B: 10 entries
  Track A: 10 entries (or whatever the current count is)
Existing items in form: ...
Items wiped. Rebuilding...
=== SPRINT 2 FORM REBUILT ===
Items before:   ...
Items after:    ...
Form ID:        1lNZHaqUQC_A9DJeSy9JJ1FQkzE1T-lA92vbJLoE6K_k  (unchanged)
Published URL:  https://docs.google.com/forms/d/e/.../viewform  (unchanged)
==============================
```

**If you see "WARNING: form has responses already"** — stop. Real votes are in. Don't proceed without checking the response Sheet first.

**If you see "ERROR: failed to fetch registry from GitHub"** — your Phase 3 push hasn't propagated to the raw URL yet. Wait 30 seconds, re-run.

### 4.4 — Spot-check the form

Click the eye/preview icon (top right of the Forms editor) to see the voter view.

Page through. Confirm:

- "About You" page is intact (affiliation, familiarity, GitHub handle, single-ballot pledge).
- Track B entries are LLM01 through LLM10.
- Specifically: any entries that were renamed (e.g., LLM07 if today) show the new title.
- Track A section appears with the correct number of candidates.
- New candidates are present.

If anything looks wrong, stop. Don't post comms yet.

**Checkpoint:** Form is live, URL unchanged, content reflects latest state.

# Phase 5: Validate GitHub state

Quick programmatic spot-check via Claude Code so you can confirm Phase 3 landed properly without clicking through the GitHub UI.

**Claude Code prompt:**

```
Validate the OWASP Sprint 2 GitHub state after the sync.

Steps:
1. Count current Sprint 2 issues:
   gh issue list --repo GenAI-Security-Project/GenAI-LLM-Top10 --label sprint-2 --state all --limit 100 --json number,title,labels | python3 -c "
   import json, sys
   issues = json.load(sys.stdin)
   print(f'Total sprint-2 issues: {len(issues)}')
   for i in issues:
       labels = [l['name'] for l in i['labels']]
       entry_id = next((l for l in labels if l.startswith('LLM') or l.startswith('TB-')), '?')
       print(f'  #{i[\"number\"]:4d}  [{entry_id:8s}]  {i[\"title\"]}')
   "

2. Tell me:
   - Total count (should equal 10 Track B + N Track A candidates)
   - Any titles that look wrong or stale
   - Specifically: confirm LLM07's title reflects the current entry name (not the old one if it was renamed)

3. Print the live registry's entry counts from main:
   curl -s https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/polling/scripts/issues.json | python3 -c "
   import json, sys
   d = json.load(sys.stdin)
   print('Registry on main:')
   print(f'  Track B: {len(d[\"track_b\"])}')
   print(f'  Track A: {len(d[\"track_a\"])}')
   "

4. Confirm: total issues count == Track B count + Track A count from the registry. Tell me if there's a mismatch.

5. Print 'PHASE 5 COMPLETE — GITHUB STATE VALIDATED' or describe any mismatches.
```

**Checkpoint:** Issue count matches registry count. Renamed entry titles look correct. No stale issues.

# Phase 6: Validate (and maybe update) the pinned Discussion

The pinned Discussion (https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/discussions/54) has hard-coded counts ("8 new candidate entries", "Sprint 3 cuts the 8 candidates to 5"). If the candidate count changed, update those.

**Claude Code prompt:**

```
Check whether the pinned Sprint 2 Discussion (#54) needs updating to match the current Track A candidate count.

Steps:
1. Fetch the Discussion #54 body:
   gh api graphql -f query='query {
     repository(owner: "GenAI-Security-Project", name: "GenAI-LLM-Top10") {
       discussion(number: 54) {
         id
         body
       }
     }
   }' | python3 -c "
   import json, sys
   d = json.load(sys.stdin)
   disc = d['data']['repository']['discussion']
   print('DISCUSSION_ID:', disc['id'])
   print('---BODY---')
   print(disc['body'])
   "

2. Fetch the live Track A candidate count from main:
   curl -s https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/polling/scripts/issues.json | python3 -c "
   import json, sys
   d = json.load(sys.stdin)
   print(f'Live Track A count: {len(d[\"track_a\"])}')
   "

3. Compare:
   - Does the Discussion body still say "8 new candidate entries"?
   - Does it still say "Sprint 3 cuts the 8 candidates to 5"?
   - Does the live Track A count match what the Discussion claims?

4. If the count mismatches, propose the find-and-replace edits I need (e.g., "8 new candidate entries" -> "10 new candidate entries", "cuts the 8 candidates" -> "cuts the 10 candidates"). Do NOT apply them yet. Wait for my "go" before patching.

5. If the count already matches, print 'DISCUSSION ALREADY MATCHES — NO UPDATE NEEDED' and stop.
```

**Checkpoint:** Either no update needed, or Claude Code has staged the find-and-replace.

**If updates are needed**, paste this follow-up prompt:

```
Apply the Discussion update you proposed.

Steps:
1. Take the current Discussion body (from the previous step) and apply ONLY these find-and-replaces:
   - "8 new candidate entries" -> "<new_count> new candidate entries"
   - "Sprint 3 cuts the 8 candidates" -> "Sprint 3 cuts the <new_count> candidates"
   (where <new_count> matches the live Track A count from issues.json)

2. PATCH the Discussion via GraphQL using the discussion ID from the previous step.
   Use a temp file for the body to avoid shell escaping issues.

   gh api graphql -F discussionId="<DISCUSSION_ID>" -F "body=@/tmp/disc_body.md" -f query='mutation($discussionId:ID!, $body:String!) {
     updateDiscussion(input: {discussionId: $discussionId, body: $body}) {
       discussion { url number }
     }
   }'

3. Confirm the response shows the Discussion was updated. Print the URL.

4. Print 'PHASE 6 COMPLETE — DISCUSSION SYNCED'.
```

# Phase 7: Final spot-check (browser)

Three quick visual checks before posting comms.

**Browser, three tabs:**

1. Open the Form's published URL: https://forms.gle/jFmqZF1R6k9gCEfi6
   - Page through. Confirm Track B and Track A sections are correct.

2. Open the issues filter: https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/issues?q=is%3Aissue+label%3Asprint-2
   - Eyeball the count and titles. Click into any renamed issue (e.g., LLM07) to confirm the body links to the new file path.

3. Open the pinned Discussion: https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/discussions/54
   - Confirm candidate count is correct in the body text.

If everything looks right, you're cleared to post comms.

# Phase 8: Post the launch comms

The drafts are in `2026/polling/comms/`. Order matters. About 5 minutes total.

### 8.1 — Slack working group

**Browser:** Open Slack, navigate to the OWASP Top 10 LLM working group channel.

Open `2026/polling/comms/slack_workgroup.md` in your editor. Copy the body (everything after the `---` divider). Paste into the Slack channel. Send.

### 8.2 — Steve's LinkedIn draft

**Browser:** Email or DM Steve with the contents of `2026/polling/comms/linkedin_post_steve.md`.

Tell him: "Draft for review. Post when ready, ideally 12-24 hours offset from mine for stagger." He'll rewrite to his voice.

### 8.3 — Your LinkedIn

**Browser:** Open LinkedIn, click "Start a post."

Open `2026/polling/comms/linkedin_post_rock.md`. Copy the body (everything after the `---` divider, NOT including the Notes section at the bottom).

Paste into LinkedIn. Add hashtags at the bottom of the post:

```
#OWASP #LLMSecurity #AISecurity #AIGovernance #AppSec
```

Tag Steve Wilson (`@Steve Wilson`) and any working group leads you want to amplify.

Click Post.

### 8.4 — Broader OWASP Slack

**Browser:** Open Slack, navigate to broader OWASP project channels (`#project-llm-top10`, `#ai-security`, etc.).

Open `2026/polling/comms/slack_broader.md`. Copy the body. Cross-post to each relevant channel.

### 8.5 — Mailing list

**Email:** Open `2026/polling/comms/mailing_list_launch.md`.

Copy the subject line and body. Send to whoever owns the OWASP Top 10 LLM mailing list. Or, if you have access, send directly via the mailing list platform.

# Phase 9: Final confirmation (Claude Code)

Quick sanity check that everything is consistent post-launch.

**Claude Code prompt:**

```
Final post-launch sanity check for OWASP Sprint 2.

Steps:
1. Print the live registry counts from main:
   curl -s https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/polling/scripts/issues.json | python3 -c "
   import json, sys
   d = json.load(sys.stdin)
   print(f'Track B: {len(d[\"track_b\"])}')
   print(f'Track A: {len(d[\"track_a\"])}')
   print(f'Form URL: {d[\"_meta\"][\"form\"][\"published_url\"]}')
   print(f'Discussion: {d[\"_meta\"][\"discussion\"][\"url\"]}')
   "

2. Count live Sprint 2 issues:
   gh issue list --repo GenAI-Security-Project/GenAI-LLM-Top10 --label sprint-2 --state all --limit 100 --json number | python3 -c "
   import json, sys
   issues = json.load(sys.stdin)
   print(f'Live issues with sprint-2 label: {len(issues)}')
   "

3. Confirm:
   - Track B + Track A from registry == live issue count
   - Form URL is reachable (HEAD request)
   - Discussion URL is reachable

4. Print 'SPRINT 2 LAUNCH COMPLETE — VOTING IS LIVE'.
```

# If something goes wrong

| Symptom | Where | Fix |
| --- | --- | --- |
| `gh auth status` says "not logged in" | Claude Code | Run `gh auth login`, pick web browser, HTTPS |
| `git push` rejected (non-fast-forward) | Claude Code | `git pull --rebase`, resolve conflicts in `issues.json` (yours wins), `git push` |
| Sync says "WARNING: no GH_TOKEN" | Claude Code | Re-run `export GH_TOKEN=$(gh auth token)` and retry |
| Sync errors on remote read | Claude Code | GitHub API hiccup. Wait 30 sec, retry. |
| Apps Script "ERROR: failed to fetch registry" | Browser | GitHub raw URL cache miss. Wait 30 sec, re-run `rebuildSprintTwoFormDynamic`. |
| Apps Script "WARNING: form has responses already" | Browser | Real votes are in. Stop. Don't rebuild. Talk to me. |
| Form section shows wrong title | Browser | Sync didn't write registry correctly. Re-run Phase 2 to inspect. |
| LLM07 issue still has old title | Anywhere | PATCH didn't apply. Manually edit via GitHub UI, or paste the sync output to me. |
| Discussion update fails | Claude Code | GraphQL permission issue. Update via GitHub UI: open #54, click pencil, find-and-replace. |

For anything else, paste the output to me.

# After tomorrow

Sprint 2 voting runs through May 18, 23:59 UTC. Comment triage is daily. Mid-sprint turnout push is May 11. Aggregation pipeline build starts week 2. Separate runbooks will exist for each.
