/**
 * OWASP Top 10 for LLM Applications — 2026 Update
 * Sprint 2 Voting Form Generator (single combined ballot, both tracks)
 *
 * Owner: Rock Lambros (rock@rockcyber.ai)
 * Version: 2.0  (consolidated from prior dual-form design)
 *
 * WHAT THIS DOES
 *   Programmatically creates the Sprint 2 Google Form covering both tracks:
 *     - Track B: 10 existing entries (Importance + Clarity)
 *     - Track A:  8 new candidates  (Importance + Clarity + Distinctness)
 *
 *   One ballot, one URL, one captive audience. All Likerts are optional.
 *   Voters skip any entry they have not read. Skip rate is a deliberate metric.
 *
 * USAGE
 *   1. Go to https://script.google.com and create a new project
 *   2. Paste this entire file into Code.gs
 *   3. Run createSprintTwoForm()
 *   4. Authorize when prompted (FormApp + Drive scopes)
 *   5. The execution log prints:
 *        - Published URL  (share this with voters and paste into create_issues.py)
 *        - Edit URL       (for the working group)
 *        - Form ID        (used by the aggregation pipeline)
 *
 * NOTES
 *   - setLimitOneResponsePerUser is a Google Workspace feature. If the project
 *     is not on a Workspace account, the call is a no-op and dedup falls to
 *     the aggregation pipeline (which dedups by collected email).
 *   - Track B appears first because the existing entries are familiar; that
 *     builds voter momentum into the Track A section.
 *   - Each entry is on its own page so voters see progress and can resume.
 */

// ---------- Configuration ----------

// Form ID of the existing live form. Used by rebuildSprintTwoForm() to
// update in place without changing the URL. Source of truth: same value
// stored in scripts/issues.json under _meta.form.form_id.
const FORM_ID = '1lNZHaqUQC_A9DJeSy9JJ1FQkzE1T-lA92vbJLoE6K_k';

const FORM_TITLE =
  'OWASP Top 10 for LLM Applications 2026 — Sprint 2 Community Vote';

const REPO_ENTRY_BASE =
  'https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/blob/main/2026/';

const REPO_CANDIDATE_BASE =
  'https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/blob/main/2026/new_entry_candidates/';

const REPO_ISSUE_BASE_A =
  'https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/issues?q=is%3Aissue+label%3Atrack-b+label%3A';

const REPO_ISSUE_BASE_B =
  'https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/issues?q=is%3Aissue+label%3Atrack-a+label%3A';

const VOTING_CLOSE = 'May 18, 2026 at 23:59 UTC';

const TRACK_B_ENTRIES = [
  { id: 'LLM01', title: 'Prompt Injection',                       file: 'LLM01_PromptInjection.md' },
  { id: 'LLM02', title: 'Sensitive Information Disclosure',       file: 'LLM02_SensitiveInformationDisclosure.md' },
  { id: 'LLM03', title: 'Supply Chain',                           file: 'LLM03_SupplyChain.md' },
  { id: 'LLM04', title: 'Data and Model Poisoning',               file: 'LLM04_DataModelPoisoning.md' },
  { id: 'LLM05', title: 'Improper Output Handling',               file: 'LLM05_ImproperOutputHandling.md' },
  { id: 'LLM06', title: 'Excessive Agency',                       file: 'LLM06_ExcessiveAgency.md' },
  { id: 'LLM07', title: 'System Prompt Leakage',                  file: 'LLM07_SystemPromptLeakage.md' },
  { id: 'LLM08', title: 'Vector and Embedding Weaknesses',        file: 'LLM08_VectorAndEmbeddingWeaknesses.md' },
  { id: 'LLM09', title: 'Misinformation',                         file: 'LLM09_Misinformation.md' },
  { id: 'LLM10', title: 'Unbounded Consumption',                  file: 'LLM10_UnboundedConsumption.md' },
];

const TRACK_A_ENTRIES = [
  { id: 'TA-CFAS', title: 'Compositional Fine-Tuning Alignment Subversion', file: 'compositional-finetuning-alignment-subversion.md' },
  { id: 'TA-CMSB', title: 'Cross-Modal Safety Bypass',                       file: 'cross-modal-safety-bypass.md' },
  { id: 'TA-ITSC', title: 'Inference-Time Side-Channel Disclosure',          file: 'inference-time-side-channel-disclosure.md' },
  { id: 'TA-MCPX', title: 'MCP Tool Interface Exploitation',                 file: 'mcp-tool-interface-exploitation.md' },
  { id: 'TA-MMIS', title: 'Model Misalignment',                              file: 'model-misalignment.md' },
  { id: 'TA-MSDA', title: 'Model Scheming and Deceptive Alignment',          file: 'model-scheming-and-deceptive-alignment.md' },
  { id: 'TA-SICG', title: 'Systemic Insecure Code Generation',               file: 'systemic-insecure-code-generation.md' },
  { id: 'TA-WLLA', title: 'Weaponized LLM Abuse',                            file: 'weaponized-llm-abuse.md' },
];

// ---------- Entry point ----------

function createSprintTwoForm() {
  const form = FormApp.create(FORM_TITLE);

  // FormApp.create() sets the Drive file name only. The display title shown
  // to voters defaults to "Untitled form" until setTitle() is called.
  form.setTitle(FORM_TITLE);
  form.setDescription(buildDescription());
  form.setCollectEmail(true);
  form.setAllowResponseEdits(true);
  form.setShowLinkToRespondAgain(false);
  form.setProgressBar(true);
  form.setConfirmationMessage(
    'Thanks for voting in Sprint 2. Your scores have been recorded. ' +
    'Comments and discussion live on the GitHub issues. Vote results ' +
    'and the candidate-selection process publish at the start of Sprint 3.'
  );

  // Workspace-only. Wrapped because non-Workspace accounts will throw.
  try { form.setLimitOneResponsePerUser(true); } catch (e) {
    Logger.log('setLimitOneResponsePerUser not available (non-Workspace account). ' +
               'Email dedup will be enforced in aggregation.');
  }

  buildVoterMetadataPage(form);
  buildTrackAEntries(form);
  buildTrackBEntries(form);

  Logger.log('=== SPRINT 2 FORM CREATED ===');
  Logger.log('Title:         ' + form.getTitle());
  Logger.log('Form ID:       ' + form.getId());
  Logger.log('Published URL: ' + form.getPublishedUrl());
  Logger.log('Edit URL:      ' + form.getEditUrl());
  Logger.log('Short URL:     ' + form.shortenFormUrl(form.getPublishedUrl()));
  Logger.log('==============================');
  Logger.log('Next step: paste the Published URL into ../scripts/create_issues.py --form-url');
}

// ---------- Update path: rebuild existing form on the same URL ----------

/**
 * Rebuilds the live Sprint 2 form on the existing Form ID. URL stays the
 * same. All items get wiped and re-added from the TRACK_B_ENTRIES and
 * TRACK_A_ENTRIES arrays above. Use this when:
 *
 *   - You have edits to existing entry titles, files, or rubric text
 *   - You're adding new candidate entries to Track A
 *   - Voting hasn't accumulated meaningful responses yet
 *
 * DO NOT run this once real votes are in. Wiping items breaks the response
 * Sheet schema. Old responses sit in orphaned columns; new responses get
 * fresh columns. Aggregation becomes a manual reconciliation job.
 *
 * SAFE OPERATING WINDOW: first 24-48 hours of voting, before the comms
 * launch hits the broader audience, while turnout is single-digit.
 *
 * Workflow:
 *   1. Edit TRACK_B_ENTRIES and/or TRACK_A_ENTRIES arrays above to reflect
 *      the new state (rename entries, add new candidates, update file refs).
 *   2. Save the script.
 *   3. Run rebuildSprintTwoForm(). URL stays the same. Issues already on
 *      GitHub continue to point at the right form.
 *   4. For NEW candidates added: run create_issues.py with --only-ids to
 *      create just the new GitHub issues without duplicating the existing 18.
 */
function rebuildSprintTwoForm() {
  const form = FormApp.openById(FORM_ID);

  const beforeCount = form.getItems().length;
  Logger.log('Existing items in form: ' + beforeCount);
  Logger.log('Existing response count: ' + form.getResponses().length);

  // Defensive: log a warning if there are responses already.
  if (form.getResponses().length > 0) {
    Logger.log('WARNING: form has responses already. Rebuild will orphan ' +
               'response columns. Export the response Sheet first.');
  }

  // Wipe items. Repeatedly delete index 0 to avoid index-shift bugs.
  while (form.getItems().length > 0) {
    form.deleteItem(form.getItems()[0]);
  }
  Logger.log('Items wiped. Rebuilding...');

  // Re-apply title and description in case they changed in the script.
  form.setTitle(FORM_TITLE);
  form.setDescription(buildDescription());

  // Rebuild from the (potentially edited) entry arrays.
  buildVoterMetadataPage(form);
  buildTrackAEntries(form);
  buildTrackBEntries(form);

  const afterCount = form.getItems().length;
  Logger.log('=== SPRINT 2 FORM REBUILT ===');
  Logger.log('Items before:   ' + beforeCount);
  Logger.log('Items after:    ' + afterCount);
  Logger.log('Form ID:        ' + form.getId() + '  (unchanged)');
  Logger.log('Published URL:  ' + form.getPublishedUrl() + '  (unchanged)');
  Logger.log('Track B count:  ' + TRACK_B_ENTRIES.length);
  Logger.log('Track A count:  ' + TRACK_A_ENTRIES.length);
  Logger.log('==============================');
  Logger.log('If you added new Track A candidates, fire their GitHub issues:');
  Logger.log('  cd polling/scripts');
  Logger.log('  export GH_TOKEN=$(gh auth token)');
  Logger.log('  python3 create_issues.py --form-url <URL> --only-ids "TA-XXXX,TA-YYYY"');
}

// ---------- Dynamic update path: pulls entry list from remote issues.json ----------

/**
 * Rebuild the form using the entry list from the LIVE issues.json on GitHub.
 *
 * This is the recommended update path when the team is making changes via
 * sync_sprint2.py (which writes to local issues.json that then gets pushed
 * to main). Apps Script fetches the latest registry from raw.githubusercontent
 * and rebuilds the form against that. No need to copy/paste entry arrays.
 *
 * WORKFLOW
 *   1. On your machine: python3 sync_sprint2.py
 *   2. git push the updated issues.json
 *   3. In Apps Script: run rebuildSprintTwoFormDynamic()
 *
 * The Apps Script reads the public raw URL of issues.json. No auth needed.
 * Cache: GitHub raw URLs serve the latest commit on the named branch
 * within seconds.
 */
const REGISTRY_URL =
  'https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/polling/scripts/issues.json';

function rebuildSprintTwoFormDynamic() {
  // Fetch the registry from the remote repo
  let registry;
  try {
    const response = UrlFetchApp.fetch(REGISTRY_URL, {
      muteHttpExceptions: false,
      followRedirects: true,
      validateHttpsCertificates: true,
    });
    registry = JSON.parse(response.getContentText());
  } catch (e) {
    Logger.log('ERROR: failed to fetch registry from GitHub: ' + e);
    Logger.log('URL: ' + REGISTRY_URL);
    Logger.log('Falling back to in-script TRACK_B_ENTRIES and TRACK_A_ENTRIES.');
    Logger.log('To use the dynamic path, run sync_sprint2.py and push issues.json first.');
    rebuildSprintTwoForm();
    return;
  }

  const remoteA = registry.track_a || [];
  const remoteB = registry.track_b || [];
  Logger.log('Fetched registry from remote:');
  Logger.log('  Track A: ' + remoteA.length + ' entries');
  Logger.log('  Track B: ' + remoteB.length + ' entries');

  // Override the in-script arrays with the remote ones, in place. Note that
  // const-bound arrays can't be reassigned, but we can mutate them.
  TRACK_A_ENTRIES.length = 0;
  remoteA.forEach(function (e) { TRACK_A_ENTRIES.push(e); });
  TRACK_B_ENTRIES.length = 0;
  remoteB.forEach(function (e) { TRACK_B_ENTRIES.push(e); });

  // Hand off to the existing rebuild function
  rebuildSprintTwoForm();
}

// ---------- Description ----------

function buildDescription() {
  return [
    'Single ballot covering both tracks of the Sprint 2 community vote:',
    '  Track B — 10 refreshed existing entries (LLM01–LLM10)',
    '  Track A — 8 new candidate entries',
    '',
    'Estimated time: 10 minutes if you score every entry. Less if you skip ' +
    'entries you have not read. Skipping is a valid signal — it tells the ' +
    'working group an entry is niche or under-explained.',
    '',
    'WHAT TO DO',
    '1. Read each entry on GitHub (links provided per section).',
    '2. Score Importance and Clarity on a 1–5 scale. Track A adds Distinctness.',
    '3. Use the GitHub issue link under each entry for qualitative comments. ' +
    'The form captures scores. The issues capture discussion.',
    '',
    'DEFINITIONS',
    '• Importance: How critical is this risk to LLM application security in 2026?',
    '• Clarity: How clearly does the entry describe the risk and mitigations?',
    '• Distinctness (Track A only): Is this materially different from existing ' +
    'entries (LLM01–LLM10), or could it be merged into one of them?',
    '',
    'INTEGRITY',
    '• One vote per person. Dedup by email.',
    '• Email is collected for dedup. It is not published.',
    '• Voting closes ' + VOTING_CLOSE + '.',
    '',
    'CODE OF CONDUCT: ' +
    'https://owasp.org/www-policy/operational/code-of-conduct'
  ].join('\n');
}

// ---------- Voter metadata page ----------

function buildVoterMetadataPage(form) {
  form.addSectionHeaderItem()
      .setTitle('About You')
      .setHelpText('Two minutes. Used for transparency reporting and to ' +
                   'stratify the results.');

  form.addListItem()
      .setTitle('Affiliation')
      .setHelpText('Pick the option that best describes your primary role.')
      .setChoiceValues([
        'Industry — security or engineering',
        'Industry — leadership',
        'Academia or research',
        'Consultancy or professional services',
        'Independent practitioner',
        'Government or regulator',
        'Student',
        'Prefer not to say'
      ])
      .setRequired(true);

  form.addListItem()
      .setTitle('Self-rated familiarity with LLM application security')
      .setHelpText('Used to stratify results. Honest answers help us interpret ' +
                   'the data. There is no "wrong" answer.')
      .setChoiceValues([
        'Novice — learning the space',
        'Practitioner — work on LLM security regularly',
        'Expert — deep specialization or published research'
      ])
      .setRequired(true);

  form.addTextItem()
      .setTitle('GitHub username (optional)')
      .setHelpText('If you contribute to the repo, share your handle. We use ' +
                   'this only to cross-validate engagement and detect anomalies.')
      .setRequired(false);

  form.addMultipleChoiceItem()
      .setTitle('I will submit only one ballot')
      .setHelpText('We dedup by email. This box is a reminder, not a control.')
      .setChoiceValues(['I confirm'])
      .setRequired(true);
}

// ---------- Track B ----------

function buildTrackAEntries(form) {
  form.addPageBreakItem()
      .setTitle('Track B: Existing Entries (LLM01–LLM10)')
      .setHelpText('Score Importance and Clarity for each existing entry. ' +
                   'Leave blank any entry you have not read. Estimated time: ' +
                   '5 minutes. Track A (new candidates) follows after this section.');

  TRACK_B_ENTRIES.forEach(function (entry, idx) {
    addEntrySection(form, entry, false /* not Track A */, REPO_ENTRY_BASE, REPO_ISSUE_BASE_A);
    if (idx !== TRACK_B_ENTRIES.length - 1) {
      form.addPageBreakItem();
    }
  });
}

// ---------- Track A ----------

function buildTrackBEntries(form) {
  form.addPageBreakItem()
      .setTitle('Track A: New Candidate Entries')
      .setHelpText('Now scoring new candidates for the 2026 Top 10. Sprint 3 ' +
                   'cuts these 8 down to 5. Track A adds a third dimension — ' +
                   'Distinctness — which tells us whether a candidate stands ' +
                   'alone or should merge into an existing entry. Estimated ' +
                   'time: 5 minutes. Skip any candidate you have not read.');

  TRACK_A_ENTRIES.forEach(function (entry, idx) {
    addEntrySection(form, entry, true /* Track A */, REPO_CANDIDATE_BASE, REPO_ISSUE_BASE_B);
    if (idx !== TRACK_A_ENTRIES.length - 1) {
      form.addPageBreakItem();
    }
  });
}

// ---------- Per-entry section ----------

function addEntrySection(form, entry, isTrackB, draftBase, issueBase) {
  const draftLink = draftBase + entry.file;
  const issueLink = issueBase + encodeURIComponent(entry.id);
  const label = isTrackB ? entry.title : (entry.id + ' — ' + entry.title);

  form.addSectionHeaderItem()
      .setTitle(label)
      .setHelpText(
        'Read the draft: ' + draftLink + '\n' +
        'Comment on GitHub: ' + issueLink
      );

  form.addScaleItem()
      .setTitle(label + ' — Importance')
      .setHelpText('How critical is this risk to LLM application security in 2026?')
      .setBounds(1, 5)
      .setLabels('1 — Not important', '5 — Critical')
      .setRequired(false);

  form.addScaleItem()
      .setTitle(label + ' — Clarity')
      .setHelpText('How clearly does the entry describe the risk and mitigations?')
      .setBounds(1, 5)
      .setLabels('1 — Confusing', '5 — Crystal clear')
      .setRequired(false);

  if (isTrackB) {
    form.addScaleItem()
        .setTitle(label + ' — Distinctness')
        .setHelpText('Is this distinct from existing OWASP Top 10 LLM entries ' +
                     '(LLM01–LLM10), or could it be merged into one?')
        .setBounds(1, 5)
        .setLabels('1 — Already covered', '5 — Clearly distinct')
        .setRequired(false);
  }

  form.addParagraphTextItem()
      .setTitle(label + ' — Brief comment (optional)')
      .setHelpText('One or two sentences max. For longer feedback use the ' +
                   'GitHub issue linked above.')
      .setRequired(false);
}
