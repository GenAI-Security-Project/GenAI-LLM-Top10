# Sprint 2 Voting Form — Blueprint

Owner: Rock Lambros (rock@rockcyber.ai)
Version: 2.1 (form generated and live)
Last Updated: May 4, 2026

This document specifies the single Google Form used for Sprint 2 voting. The Apps Script `create_form.gs` builds it programmatically. This blueprint is the source of truth if the script ever drifts.

## Live form references

- **Published URL** (canonical, for GitHub issues and durable references): https://docs.google.com/forms/d/e/1FAIpQLSebmFQyJPOMuw1IorHCJ2FdW98ZT2oLNBuVgYqpPoayW9v6ww/viewform
- **Short URL** (for human-shared comms — LinkedIn, Slack, mailing list): https://forms.gle/jFmqZF1R6k9gCEfi6
- **Edit URL** (working group only): https://docs.google.com/forms/d/1lNZHaqUQC_A9DJeSy9JJ1FQkzE1T-lA92vbJLoE6K_k/edit
- **Form ID**: `1lNZHaqUQC_A9DJeSy9JJ1FQkzE1T-lA92vbJLoE6K_k`
- **Generated**: May 4, 2026 from `create_form.gs`
- **Owner account**: Rock Lambros' Google account
- **Response destination**: Linked Google Sheet (created via the Forms UI; aggregation pipeline reads via Form ID)

## Single ballot, both tracks

One form covers Track B (10 existing entries) and Track A (8 new candidates). Voters land on a single URL, fill what they know, skip what they don't. The "captive audience" design boosts Track A participation by routing voters there after they finish the more familiar Track B entries.

Tracks remain analytically separate. Question titles tag every score with its entry ID (`LLM01 — Importance`, `TA-MCPX — Distinctness`), so the aggregation pipeline splits the data cleanly. Sprint plan still evaluates the tracks independently.

## Voting close

Form closes May 18, 2026 at 23:59 UTC. The aggregation pipeline runs on May 19.

## Form-level settings

| Setting | Value | Why |
| --- | --- | --- |
| Collect email addresses | On | Dedup key for the analysis pipeline |
| Limit to one response | On (Workspace only) | Soft control; real dedup runs in analysis |
| Allow response edits | On | Voters can refine without resubmitting |
| Show "Submit another response" link | Off | Mild dedup signal |
| Progress bar | On | Critical for retention on a 19-page form |
| Confirmation message | Custom (see script) | Sets expectation about Sprint 3 |

## Form structure (page-by-page)

| Page | Content | Required fields |
| --- | --- | --- |
| 1 | About You — voter metadata | Affiliation, familiarity, single-ballot pledge |
| 2 | Track B intro + LLM01 (Prompt Injection) scoring | None (all Likerts optional) |
| 3 | LLM02 Sensitive Information Disclosure | None |
| 4 | LLM03 Supply Chain | None |
| 5 | LLM04 Data and Model Poisoning | None |
| 6 | LLM05 Improper Output Handling | None |
| 7 | LLM06 Excessive Agency | None |
| 8 | LLM07 System Prompt Leakage | None |
| 9 | LLM08 Vector and Embedding Weaknesses | None |
| 10 | LLM09 Misinformation | None |
| 11 | LLM10 Unbounded Consumption | None |
| 12 | Track A intro + TA-CFAS (Compositional Fine-Tuning Alignment Subversion) | None |
| 13 | TA-CMSB Cross-Modal Safety Bypass | None |
| 14 | TA-ITSC Inference-Time Side-Channel Disclosure | None |
| 15 | TA-MCPX MCP Tool Interface Exploitation | None |
| 16 | TA-MMIS Model Misalignment | None |
| 17 | TA-MSDA Model Scheming and Deceptive Alignment | None |
| 18 | TA-SICG Systemic Insecure Code Generation | None |
| 19 | TA-WLLA Weaponized LLM Abuse | None |

Total: 19 pages. Estimated completion time 10 minutes if voter scores everything, 1–2 minutes if voter scores one entry.

## Voter metadata page (page 1)

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| Email | Auto-collected by Forms | Yes | Dedup key |
| Affiliation | Dropdown (8 options) | Yes | Stratification, transparency reporting |
| Self-rated familiarity | Dropdown (Novice / Practitioner / Expert) | Yes | Stratification |
| GitHub username | Text | No | Optional cross-validation against repo activity |
| Single-ballot pledge | Multiple choice (I confirm) | Yes | Reminder, not enforcement |

Affiliation options: Industry — security or engineering; Industry — leadership; Academia or research; Consultancy or professional services; Independent practitioner; Government or regulator; Student; Prefer not to say.

## Per-entry section

Each entry is on its own page. The section header at the top of every entry page contains:

- Entry ID and title
- Direct link to the draft markdown on GitHub
- Direct link to the entry's GitHub feedback issue (filtered by label)

### Track B: 2 Likert questions per entry

| Question | Scale | Required |
| --- | --- | --- |
| Importance | 1–5 (1 Not important, 5 Critical) | No |
| Clarity | 1–5 (1 Confusing, 5 Crystal clear) | No |
| Brief comment | Paragraph text | No |

### Track A: 3 Likert questions per entry

| Question | Scale | Required |
| --- | --- | --- |
| Importance | 1–5 (1 Not important, 5 Critical) | No |
| Clarity | 1–5 (1 Confusing, 5 Crystal clear) | No |
| Distinctness | 1–5 (1 Already covered, 5 Clearly distinct) | No |
| Brief comment | Paragraph text | No |

Distinctness is Track A only. It tells Sprint 3 whether a high-Importance candidate is a standalone entry or a merge into an existing one. Cuts the risk of Sprint 4 churn over duplicative entries.

### Why all Likerts are optional

Skipping is a deliberate signal. Voters who do not feel qualified to score an entry should leave it blank. Skip rate per entry feeds the analysis. Forcing a vote produces noise.

## Track B entries (10)

| ID | Title | Draft file |
| --- | --- | --- |
| LLM01 | Prompt Injection | LLM01_PromptInjection.md |
| LLM02 | Sensitive Information Disclosure | LLM02_SensitiveInformationDisclosure.md |
| LLM03 | Supply Chain | LLM03_SupplyChain.md |
| LLM04 | Data and Model Poisoning | LLM04_DataModelPoisoning.md |
| LLM05 | Improper Output Handling | LLM05_ImproperOutputHandling.md |
| LLM06 | Excessive Agency | LLM06_ExcessiveAgency.md |
| LLM07 | System Prompt Leakage | LLM07_SystemPromptLeakage.md |
| LLM08 | Vector and Embedding Weaknesses | LLM08_VectorAndEmbeddingWeaknesses.md |
| LLM09 | Misinformation | LLM09_Misinformation.md |
| LLM10 | Unbounded Consumption | LLM10_UnboundedConsumption.md |

## Track A candidates (8)

| ID | Title | Draft file |
| --- | --- | --- |
| TA-CFAS | Compositional Fine-Tuning Alignment Subversion | compositional-finetuning-alignment-subversion.md |
| TA-CMSB | Cross-Modal Safety Bypass | cross-modal-safety-bypass.md |
| TA-ITSC | Inference-Time Side-Channel Disclosure | inference-time-side-channel-disclosure.md |
| TA-MCPX | MCP Tool Interface Exploitation | mcp-tool-interface-exploitation.md |
| TA-MMIS | Model Misalignment | model-misalignment.md |
| TA-MSDA | Model Scheming and Deceptive Alignment | model-scheming-and-deceptive-alignment.md |
| TA-SICG | Systemic Insecure Code Generation | systemic-insecure-code-generation.md |
| TA-WLLA | Weaponized LLM Abuse | weaponized-llm-abuse.md |

The TA-XXXX IDs are GitHub label values. They keep issue filter URLs short and stable even if the candidate title changes.

## Known limitations

**Section deep-linking**: Google Forms always opens at page 1. Issues for specific entries link to the same Form URL. The issue body explains how to navigate. Voters who land on the form from an LLM05 issue still see "About You" first and have to page through to LLM05. Acceptable cost for the captive-audience benefit.

**Order bias**: Track B always comes before Track A. Track B always lists LLM01 → LLM10 in canonical order. Voters who fatigue mid-form score later entries less generously. Aggregation reports completion rate per entry to flag this.

**Drop-off mid-form**: 19 pages. Some voters will abandon partway through. The aggregation pipeline tracks "completed Track B only" vs "completed both" as a participation segmentation, and reports per-entry response rate as a completion proxy.

**Workspace gating**: `setLimitOneResponsePerUser` only enforces inside Google Workspace. Public OWASP voting will not have it. Email dedup in aggregation compensates.

**Brigading risk**: a public form is a brigading target. Anomaly detection in aggregation looks at vote velocity, timestamp clustering, and new-account signals via the optional GitHub handle.

## How to run

1. Open https://script.google.com and create a new project.
2. Paste `create_form.gs` into Code.gs.
3. Run `createSprintTwoForm()`.
4. Authorize when prompted (FormApp + Drive scopes).
5. Copy the **Published URL** from the execution log.
6. Pass that URL to `../scripts/create_issues.py --form-url ...` to create the 18 GitHub feedback issues.

The Form auto-routes responses to a Google Sheet. The aggregation pipeline (separate deliverable) reads that Sheet by Form ID.
