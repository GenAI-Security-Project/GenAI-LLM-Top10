# Contributing to the 2026 Cycle

Thank you for helping build the **OWASP Top 10 for Large Language Model Applications — 2026** release. This document is the step-by-step guide for contributing to this folder (`2026/`). It covers two distinct tracks:

1. **[Track A — Propose a new entry](#track-a--propose-a-new-entry)** — community members who want to write up a vulnerability or risk that is not currently in the list.
2. **[Track B — Upgrade an existing entry](#track-b--upgrade-an-existing-entry)** — existing entry owners (and their sub-teams) who are iterating on an `LLM01`–`LLM10` entry already in the repo.

Both tracks share the same pull-request workflow, style guide, and review rules. Those shared rules live in [Shared workflow](#shared-workflow) — read that section once; you will use it for every PR.

> [!IMPORTANT]
> **All changes to this repository must be made through a pull request.** There are no exceptions for contributors — direct pushes to `main` are blocked by branch protection. This applies to every change: new entries, entry upgrades, typo fixes, link repairs, artifact additions, style-guide edits, and README tweaks. If you are unsure whether your change qualifies, open a PR.

For the broader project-level contributor overview, see the repository-root [`README.md`](../README.md). The style guide lives in [`documentation/style/`](../documentation/style/README.md) and is required reading before submitting any prose.

---

## Who this is for

| You are... | Use this track |
|---|---|
| Writing a brand-new risk/vulnerability proposal for the 2026 list | [Track A](#track-a--propose-a-new-entry) |
| Named in [`CODEOWNERS`](../.github/CODEOWNERS) or on an entry sub-team and improving `LLM01`–`LLM10` content | [Track B](#track-b--upgrade-an-existing-entry) |
| Fixing a typo, broken link, or small style nit in any 2026 file | [Track B](#track-b--upgrade-an-existing-entry) (treat it as a small upgrade) |
| Adding glossary terms, diagrams, or style updates | Open a PR against [`documentation/`](../documentation/) — outside the scope of this file |

---

## Before you start

Complete these once, before your first PR:

1. **GitHub account.** **Every change lands on `main` through a pull request — no exceptions.** Direct pushes to `main` are blocked by branch protection and will be rejected by the server. You work on a feature branch (in your fork or the upstream repo), open a PR, and merge only after it satisfies every rule in [Branch protection and what reviewers will check](#branch-protection-and-what-reviewers-will-check).
2. **Read the style guide.** Every entry must follow:
   - [`documentation/style/README.md`](../documentation/style/README.md) — overview
   - [`documentation/style/general.md`](../documentation/style/general.md) — Markdown, headings, tone, US English
   - [`documentation/style/entries.md`](../documentation/style/entries.md) — required sections and structure for `LLMXX` entries
   - [`documentation/style/branding.md`](../documentation/style/branding.md) — if you reuse project assets
3. **Skim the template.** Every entry (new or upgraded) conforms to [`2026/_template.md`](./_template.md). It defines the five required sections: *Description*, *Common Examples of Risk*, *Prevention and Mitigation Strategies*, *Example Attack Scenarios*, *Reference Links*.
4. **Enable signed commits.** Required by branch protection on `main`. See [Signing your commits](#signing-your-commits).
5. **Review existing entries** in [`2026/`](./) so you understand tone, depth, and scope before you write.

---

## Repository layout (2026 cycle)

```
2026/
├── CONTRIBUTING.md             # this file
├── _template.md                # entry template — copy this for new entries
├── LLM00_Preface.md            # preface (non-numbered)
├── LLM01_PromptInjection.md    # existing numbered entries LLM01..LLM10
├── ...
├── LLM10_UnboundedConsumption.md
├── new_entry_candidates/       # staging area for proposed (Track A) entries
└── artifacts/                  # diagrams, PDFs, supporting images
```

Other directories you may touch indirectly:

- [`.github/CODEOWNERS`](../.github/CODEOWNERS) — required reviewers (see [Review process](#review-process)).
- [`documentation/style/`](../documentation/style/README.md) — style guide.

---

## Track A — Propose a new entry

Use this track when you want to nominate a **new** risk/vulnerability for inclusion in the 2026 list. Your proposal lives in [`2026/new_entry_candidates/`](./new_entry_candidates/) until the core team evaluates it for inclusion; if accepted, it is later promoted to a numbered `LLMXX_*.md` slot.

### Step 1 — Open a discussion issue (recommended)

Before writing a full entry, open a GitHub issue describing the proposed risk in a sentence or two. This lets the core team flag overlaps with existing entries (`LLM01`–`LLM10`) early and saves you writing work.

The issue is optional but strongly recommended. Skip it only if the risk is clearly novel.

### Step 2 — Fork and clone

1. Fork this repository to your GitHub account.
2. Clone your fork locally:
   ```bash
   git clone git@github.com:<your-username>/GenAI-LLM-Top10.git
   cd GenAI-LLM-Top10
   ```
3. Add the upstream remote so you can stay in sync:
   ```bash
   git remote add upstream git@github.com:GenAI-Security-Project/GenAI-LLM-Top10.git
   git fetch upstream
   ```

### Step 3 — Create a feature branch

Branch from the latest `main`. Use the naming convention `new-entry/<short-slug>`:

```bash
git checkout -b new-entry/model-inversion upstream/main
```

### Step 4 — Copy the template

Copy [`2026/_template.md`](./_template.md) into [`2026/new_entry_candidates/`](./new_entry_candidates/) and rename it using a descriptive slug (lowercase, hyphenated, no `LLMXX` prefix — numbering is assigned by the core team during promotion):

```bash
cp 2026/_template.md 2026/new_entry_candidates/model-inversion.md
```

### Step 5 — Fill in every template section

Your entry **must** include all five sections defined in [`2026/_template.md`](./_template.md), in the same order, at the same heading levels:

1. `## <Risk Name>` — level-2 heading. Omit the `LLMXX:` prefix for Track A; numbering is assigned at promotion.
2. `### Description` — what the risk is, at a high level. Follow the paragraph style in [`documentation/style/entries.md`](../documentation/style/entries.md#description).
3. `### Common Examples of Risk` — at least one numbered example. High-level categorization, not attack code. See [the *Example of Risk vs. Attack Scenario* guidance](../documentation/style/entries.md#technical-guidance).
4. `### Prevention and Mitigation Strategies` — at least one actionable mitigation. Numbered list.
5. `### Example Attack Scenarios` — at least one concrete scenario, including sample prompts, code, or request flows where applicable. This is where technical specifics belong.
6. `### Reference Links` — numbered list of citations. For arXiv papers, follow the arXiv-provided citation guidance. Format: `[Title](URL): **Publisher/Outlet**`.

Follow the project-wide Markdown and tone rules in [`documentation/style/general.md`](../documentation/style/general.md): ATX-style headings, US English spellings, no idioms, define jargon on first use, never skip heading levels.

### Step 6 — Commit using signed commits

See [Signing your commits](#signing-your-commits). Keep commits small and focused; one logical change per commit.

```bash
git add 2026/new_entry_candidates/model-inversion.md
git commit -S -m "Propose new entry: Model Inversion"
```

### Step 7 — Push and open a pull request

```bash
git push -u origin new-entry/model-inversion
```

Open the PR against `GenAI-Security-Project/GenAI-LLM-Top10:main`. Use a clear title in the form `New entry: <Risk Name>`. Fill out the PR description with:

- A one-paragraph summary of the proposed risk.
- Why it is distinct from existing `LLM01`–`LLM10` entries.
- Any open questions you want reviewers to weigh in on.
- A link to the discussion issue from Step 1, if you opened one.

### Step 8 — Respond to review

See [Review process](#review-process). New-entry PRs typically go through several rounds of revision; expect scope, wording, and scenario feedback from CODEOWNERS.

### Step 9 — After acceptance

If the core team accepts the proposal, a CODEOWNER (not you) will:

1. Rename your file from `2026/new_entry_candidates/<slug>.md` to the next available `2026/LLMXX_<PascalCaseName>.md`.
2. Add the `LLMXX:` prefix to the level-2 heading.
3. Assign a sub-team owner in [`CODEOWNERS`](../.github/CODEOWNERS) for ongoing maintenance (which moves the entry into [Track B](#track-b--upgrade-an-existing-entry)).

---

## Track B — Upgrade an existing entry

Use this track if you own, or are on the sub-team for, one of the numbered entries already present in [`2026/`](./) (`LLM01_PromptInjection.md` through `LLM10_UnboundedConsumption.md`), or if you are making a small fix (typo, link repair, style alignment) to any 2026 file.

### Step 1 — Confirm ownership

Check [`CODEOWNERS`](../.github/CODEOWNERS) to confirm you (or your sub-team) are the owner for the file you plan to edit. If you are not listed and the change is non-trivial, coordinate with the listed owner first — they control merge approval.

### Step 2 — Clone or pull

If you already have a fork from previous work, sync it:

```bash
git checkout main
git fetch upstream
git merge --ff-only upstream/main
```

Otherwise, follow Track A [Step 2 — Fork and clone](#step-2--fork-and-clone).

### Step 3 — Create a feature branch

Branch from the latest `main`. Use one of these naming conventions:

- `upgrade/LLM0X-<short-slug>` — substantive upgrades. Example: `upgrade/LLM01-prompt-injection-multimodal`.
- `fix/<short-slug>` — typos, broken links, small style corrections. Example: `fix/llm03-dead-reference-link`.

```bash
git checkout -b upgrade/LLM01-prompt-injection-multimodal upstream/main
```

### Step 4 — Edit the entry in place

Edit the existing file directly — do **not** copy it into `new_entry_candidates/`. Preserve the structure required by [`2026/_template.md`](./_template.md) and [`documentation/style/entries.md`](../documentation/style/entries.md): the same five sections, the same heading levels, the `LLMXX:` prefix on the level-2 heading.

Scope guidance for sub-teams:

- **Prefer small, incremental PRs** over one large rewrite. Each PR should address one coherent topic (e.g., "add multimodal attack scenarios", "refresh references", "clarify mitigation #3"). Large PRs slow reviews and invite merge conflicts.
- **Coordinate cross-entry changes.** If your upgrade touches terminology, examples, or mitigations referenced by other `LLMXX` entries, notify the affected CODEOWNERS in your PR description.
- **Artifacts go in [`2026/artifacts/`](./artifacts/).** Diagrams and images live there; reference them with relative links (e.g., `![Architecture](./artifacts/architecture.png)`).
- **Do not renumber entries.** Numbering is owned by the core team; propose renumbering in a separate issue.

### Step 5 — Run the style checks yourself

Before opening the PR, reread [`documentation/style/general.md`](../documentation/style/general.md) and [`documentation/style/entries.md`](../documentation/style/entries.md) and confirm:

- Heading levels are sequential (no jumps from `##` to `####`).
- Bullet lists use `*`; numbered lists use explicit numbers (`1.`, `2.`, `3.`).
- US English spellings throughout.
- No undefined jargon or acronyms.
- All internal links resolve (click through each one).
- Reference entries follow the `[Title](URL): **Publisher**` format.

### Step 6 — Commit using signed commits

See [Signing your commits](#signing-your-commits). Group related changes into one commit; keep unrelated changes in separate commits to ease review.

```bash
git add 2026/LLM01_PromptInjection.md 2026/artifacts/llm01-multimodal.png
git commit -S -m "LLM01: add multimodal prompt-injection attack scenario"
```

### Step 7 — Push and open the PR

```bash
git push -u origin upgrade/LLM01-prompt-injection-multimodal
```

Open the PR against `GenAI-Security-Project/GenAI-LLM-Top10:main`. Title format: `LLM0X: <short description>`. In the description:

- Summarize what changed and why.
- Note whether the sub-team has internally reviewed the change already.
- Flag any cross-entry impact (affected entries, owners notified).
- Link to the issue or discussion the upgrade responds to, if any.

### Step 8 — Review and merge

See [Review process](#review-process).

---

## Shared workflow

Everything below applies to both tracks.

### Branch protection and what reviewers will check

**All changes to `main` must go through a pull request.** Direct pushes, force-pushes, and branch deletions from contributor accounts are rejected at the server. Every PR must satisfy **all** of the following before it can merge:

1. **Opened as a pull request.** The only path to `main` is a PR from a feature branch. There is no "direct commit" escape hatch for contributors.
2. **Two approving reviews.** Dismissed on new pushes. One must come from a [`CODEOWNERS`](../.github/CODEOWNERS) entry (enforced for every path).
3. **Approval of the last push.** Any new commits after approval require re-approval.
4. **All review conversations resolved.**
5. **All commits signed.** Unsigned commits are rejected.
6. **Linear history.** No merge commits into your branch — rebase, don't merge. See [Keeping your branch current](#keeping-your-branch-current).
7. **No force-pushes or deletions** on `main` (admins may bypass in emergencies; contributors cannot).

Repository admins can bypass these rules only in emergencies. Contributors should assume full enforcement at all times — if in doubt, open a PR.

### Signing your commits

Branch protection requires every commit to `main` to be signed. Set this up once per machine.

**Option 1 — SSH signing (simplest if you already push via SSH).**

1. In [GitHub → Settings → SSH and GPG keys](https://github.com/settings/keys), add your SSH public key a second time, this time with the type **"Signing Key"**.
2. Configure git locally:
   ```bash
   git config --global gpg.format ssh
   git config --global user.signingkey ~/.ssh/id_ed25519.pub
   git config --global commit.gpgsign true
   ```

**Option 2 — GPG signing.**

1. Generate or import a GPG key. Export the public key and paste it into [GitHub → Settings → SSH and GPG keys](https://github.com/settings/keys).
2. Configure git locally:
   ```bash
   git config --global user.signingkey <YOUR-GPG-KEY-ID>
   git config --global commit.gpgsign true
   ```

**Option 3 — Edit in the GitHub web UI.** Commits made through the GitHub web editor are signed automatically by GitHub's web-flow key. This is the easiest path for small fixes.

Verify a commit is signed with `git log --show-signature -1`.

### Keeping your branch current

`main` requires linear history, so merge commits are rejected. Keep your branch current with rebase:

```bash
git fetch upstream
git rebase upstream/main
# resolve conflicts if any, then:
git push --force-with-lease
```

Use `--force-with-lease` (not `--force`) so you do not clobber reviewer commits that might have been pushed to your branch.

### Commit message style

- Use the imperative mood: `LLM01: add multimodal attack scenario` (not `Added...`).
- For entry changes, prefix with the entry ID: `LLM03:`, `LLM10:`, etc.
- For cross-cutting changes, use a plain description.
- Keep the subject line under ~72 characters; elaborate in the body if needed.

### Review process

1. Open your PR. Fill out the description completely.
2. CI and any hooks run. Address any automated feedback.
3. Request review from at least two reviewers — at least one must be a [`CODEOWNERS`](../.github/CODEOWNERS) entry (GitHub auto-requests them for changed paths).
4. Reviewers leave comments. Respond to each one. Either apply the suggestion or explain why not.
5. When a conversation is resolved, click **"Resolve conversation"** on it — branch protection requires all threads resolved before merge.
6. If you push new commits after approval, the existing approvals are dismissed. Re-request review.
7. Once you have **two approvals (including one CODEOWNER)**, all threads resolved, and a clean linear history, a maintainer (or you, if you have merge permissions) squashes or rebases the PR onto `main`.

### After merge

- Delete your feature branch from your fork.
- If your change affects other in-flight PRs (e.g., terminology shift), leave a comment on those PRs.

---

## Style and formatting (short reference)

The full style guide is authoritative: [`documentation/style/`](../documentation/style/README.md). Highlights:

- **Markdown.** ATX-style headings (`#`, `##`, ...), no skipped levels.
- **Language.** US English. Clear, international, jargon-defined.
- **Lists.** `*` for unordered; explicit numbers for ordered.
- **Emphasis.** `**bold**`, `*italic*`.
- **Links.** Inline, to local paths where a local equivalent exists.
- **Code.** Backticks for inline, triple backticks for blocks.
- **Tables.** Markdown pipe syntax (see [`documentation/style/general.md`](../documentation/style/general.md#tables)).
- **Images.** `![alt](path)`, with assets stored in [`2026/artifacts/`](./artifacts/).

Entry-specific rules (section order, heading level per section, *Example of Risk* vs. *Example Attack Scenario*) are detailed in [`documentation/style/entries.md`](../documentation/style/entries.md).

---

## Getting help

- **Content questions** (what belongs in which section, scope of your entry): open a GitHub issue and tag the relevant CODEOWNERS.
- **Style questions**: reread [`documentation/style/entries.md`](../documentation/style/entries.md); if unclear, open an issue so the ambiguity gets fixed in the style guide itself.
- **Workflow / tooling questions** (signing, rebasing, branch protection): open an issue or ask in your PR description — reviewers will help.

Thank you for contributing.
