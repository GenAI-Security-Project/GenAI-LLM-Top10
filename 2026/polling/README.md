# Sprint 2 Polling Infrastructure

OWASP Top 10 for LLM Applications — 2026 Update
Sprint 2: Community Review and Voting (May 4–18, 2026)

Owner: Rock Lambros (rock@rockcyber.ai)
Co-lead: Steve Wilson

This folder contains everything needed to run Sprint 2 community voting and feedback collection. Single combined Google Form covering both tracks (10 existing entries plus 8 new candidates), 18 GitHub issues for qualitative comments.

## Folder layout

```
polling/
├── README.md                              # this file
├── .gitignore
├── .github/
│   └── ISSUE_TEMPLATE/
│       ├── feedback-track-b.yml           # issue form for existing-entry feedback
│       ├── feedback-track-a.yml           # issue form for candidate-entry feedback
│       └── config.yml                     # disables blank issues, adds vote link
├── forms/
│   ├── create_form.gs                     # Apps Script: builds the Sprint 2 Google Form
│   └── blueprint.md                       # human-readable Form spec
└── scripts/
    ├── issues.json                        # 22 labels + 18 issue payloads
    └── create_issues.py                   # bulk issue creator (idempotent)
```

When this folder lands in the GenAI-LLM-Top10 repo, the `.github/ISSUE_TEMPLATE/` files move to the repo root's `.github/ISSUE_TEMPLATE/` (not under `polling/`). The rest stays where it is.

## Run order

This is the operating sequence. Each step gates the next.

### 1. Create the Form (Apps Script) — **DONE**

Form was generated on May 4, 2026 from `forms/create_form.gs` running under Rock's Google account.

- **Published URL** (used by GitHub issues): https://docs.google.com/forms/d/e/1FAIpQLSebmFQyJPOMuw1IorHCJ2FdW98ZT2oLNBuVgYqpPoayW9v6ww/viewform
- **Short URL** (use for LinkedIn, Slack, mailing list): https://forms.gle/jFmqZF1R6k9gCEfi6
- **Edit URL** (working group only): https://docs.google.com/forms/d/1lNZHaqUQC_A9DJeSy9JJ1FQkzE1T-lA92vbJLoE6K_k/edit
- **Form ID**: `1lNZHaqUQC_A9DJeSy9JJ1FQkzE1T-lA92vbJLoE6K_k`

The Form ID feeds the aggregation pipeline (it identifies the linked response Sheet). All values are stored in `scripts/issues.json` under `_meta.form` for traceability.

If the form ever needs to be regenerated, re-run `createSprintTwoForm()` in Apps Script and update both files plus the issue templates with the new URL/ID.

### 2. Land the issue templates — **DONE (URLs baked in)**

Copy `polling/.github/ISSUE_TEMPLATE/*.yml` to `.github/ISSUE_TEMPLATE/` in the repo root and commit. The Form URL is already baked into all three template files. No further substitution needed. Templates take effect immediately on `main`.

### 3. Create the 18 feedback issues — **DONE**

Issues fired May 4, 2026 via the Python script (`create_issues.py`) running under Rock's gh CLI auth. 22 labels upserted, 10 Track B issues, 8 Track A issues. Filter: https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/issues?q=is%3Aissue+label%3Asprint-2

If you ever need to re-run (e.g., to add a candidate mid-sprint):

```bash
export GH_TOKEN=$(gh auth token)
cd polling/scripts

python3 create_issues.py \
  --form-url "https://docs.google.com/forms/d/e/1FAIpQLSebmFQyJPOMuw1IorHCJ2FdW98ZT2oLNBuVgYqpPoayW9v6ww/viewform" \
  --dry-run

python3 create_issues.py \
  --form-url "https://docs.google.com/forms/d/e/1FAIpQLSebmFQyJPOMuw1IorHCJ2FdW98ZT2oLNBuVgYqpPoayW9v6ww/viewform"
```

The script is idempotent on labels (existing labels get patched, not duplicated) but **not** on issues. Re-running creates duplicates.

### 4. Pin the launch announcement — **DONE**

Pinned Discussion: https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/discussions/54

Body sourced from `comms/github_discussion_pinned.md`. The Discussion is the FAQ + cross-cutting comment venue for Sprint 2.

## Why one combined form

Single URL to promote, single captive audience. A voter who finishes the existing entries (Track B) rolls naturally into the new candidates (Track A) instead of needing to remember a second link. Track A participation rises. Comms simplify.

The cost is voter fatigue mid-form. All Likert questions are optional, so drop-off is graceful and tracked as a metric in aggregation. Per-entry response rate proxies completion. The aggregation pipeline distinguishes "completed Track B only" from "completed both" so partial ballots still count.

Tracks remain analytically separate. Question titles tag every score with its entry ID (`LLM01 — Importance`, `TA-MCPX — Distinctness`), so the aggregation pipeline splits the data cleanly.

## Voter integrity

A public OWASP vote is a brigading target. The integrity story:

- **Email collection** in the Form enforces dedup. Workspace-only `setLimitOneResponsePerUser` is best-effort; real dedup runs in the aggregation pipeline.
- **GitHub username** field is optional but cross-validated against repo activity (commenters, stargazers) as a soft signal.
- **Affiliation and self-rated familiarity** allow stratified analysis without disqualifying any voter.
- **Likert questions are optional** so unfamiliar voters skip rather than guess. Skip rate is a metric, not a failure.
- **Anomaly detection** in the aggregation pipeline: vote-velocity spikes, timestamp clustering, mismatch between affiliation and familiarity claims.

The aggregation pipeline (built separately in Sprint 2 week 2) consumes the Sheet and the 18 issue threads, deduplicates by email, runs the integrity checks, and emits the ranked tally for Sprint 3. Reports include median, mean, N, standard deviation, IQR, skip rate, distribution histograms, Importance × Clarity quadrant plots, bootstrap rank stability, stratified views, and brigading flags.

## What this folder does **not** include

- The aggregation notebook (separate deliverable, week 2 of Sprint 2)
- Communications copy (LinkedIn, Slack, mailing list)
- Comment triage templates (entry leads own these)
- The Sprint 3 selection playbook

These are scoped for follow-on work once the ballot is live.

## Editing the configuration

If a candidate is added or dropped before launch:

1. Edit the entry array in **both** `forms/create_form.gs` and `scripts/issues.json`
2. Re-run the Apps Script (creates a new Form; old Form can be deleted)
3. Re-run `create_issues.py` only for the new entries (delete duplicate old issues manually)

Adding entries mid-sprint resets voting baselines. Avoid if possible.

## Decisions baked into this design

| Decision | Rationale |
| --- | --- |
| Single combined Form (Track B then Track A) | One URL to promote. Captive audience rolls from familiar existing entries into new candidates. Higher Track A participation. |
| Track A includes Distinctness Likert | Sprint 3 cuts 8→5. High-Importance candidates that overlap heavily with existing entries are merge targets, not standalone winners. Distinctness gives a defensible cut/keep/merge signal. |
| All Likerts optional, none required | Forced votes from unqualified voters add noise. Skip rate is a deliberate metric. |
| Each entry on its own page | Progress visible. Voters can stop and resume. |
| GitHub for comments, Form for scores | Comments need durability and version history (GitHub). Structured numeric data needs clean export (Form → Sheet). Two systems, linked, each playing to its strength. |
| Email collection on, Workspace-only enforcement off | Public OWASP vote will not have Workspace. Dedup happens in aggregation. |
| Median + mean + 9 other diagnostics | Median is the headline ranking. Diagnostics defend the rank in Sprint 4. |

## Known limitations

- **Section deep-linking**: Google Forms always opens at page 1. Voters arriving from a specific entry's GitHub issue still see "About You" first and have to page through. The issue body explains the navigation.
- **Order bias**: Track B always precedes Track A. Each track lists entries in canonical order. Voters who fatigue mid-form score later entries less generously. Aggregation reports per-entry response rate to flag.
- **Drop-off mid-form**: 19 pages is long. Aggregation tracks completion per entry as the participation signal.
- **Workspace gating**: native one-response-per-user enforcement requires Workspace. Email dedup compensates.
- **Brigading risk**: a public Form is a brigading target. Anomaly detection compensates.
- **Comment-vote correlation is weak**: voters who comment may not vote. The integrity playbook tracks both populations and reports overlap.

## Contact

Working group questions: Rock Lambros (rock@rockcyber.ai) or Steve Wilson via the OWASP Slack channel.

Process or technical questions about this infrastructure: open a Discussion on the repo.
