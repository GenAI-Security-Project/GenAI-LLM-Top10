/**
 * OWASP Top 10 for LLM Applications — 2026 Update
 * Sprint 2 Voting Form Generator (single combined ballot, both tracks)
 *
 * Owner: Rock Lambros (rock@rockcyber.ai)
 * Version: 2.0  (consolidated from prior dual-form design)
 *
 * WHAT THIS DOES
 *   Programmatically creates the Sprint 2 Google Form covering both tracks:
 *     - Track A: 10 existing entries (Importance + Clarity)
 *     - Track B:  8 new candidates  (Importance + Clarity + Distinctness)
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
 *   - Track A appears first because the existing entries are familiar; that
 *     builds voter momentum into the Track B section.
 *   - Each entry is on its own page so voters see progress and can resume.
 */

// ---------- Configuration ----------

const FORM_TITLE =
  'OWASP Top 10 for LLM Applications 2026 — Sprint 2 Community Vote';

const REPO_ENTRY_BASE =
  'https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/blob/main/2026/';

const REPO_CANDIDATE_BASE =
  'https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/blob/main/2026/new_entry_candidates/';

const REPO_ISSUE_BASE_A =
  'https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/issues?q=is%3Aissue+label%3Atrack-a+label%3A';

const REPO_ISSUE_BASE_B =
  'https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/issues?q=is%3Aissue+label%3Atrack-b+label%3A';

const VOTING_CLOSE = 'May 18, 2026 at 23:59 UTC';

const TRACK_A_ENTRIES = [
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

const TRACK_B_ENTRIES = [
  { id: 'TB-CFAS', title: 'Compositional Fine-Tuning Alignment Subversion', file: 'compositional-finetuning-alignment-subversion.md' },
  { id: 'TB-CMSB', title: 'Cross-Modal Safety Bypass',                       file: 'cross-modal-safety-bypass.md' },
  { id: 'TB-ITSC', title: 'Inference-Time Side-Channel Disclosure',          file: 'inference-time-side-channel-disclosure.md' },
  { id: 'TB-MCPX', title: 'MCP Tool Interface Exploitation',                 file: 'mcp-tool-interface-exploitation.md' },
  { id: 'TB-MMIS', title: 'Model Misalignment',                              file: 'model-misalignment.md' },
  { id: 'TB-MSDA', title: 'Model Scheming and Deceptive Alignment',          file: 'model-scheming-and-deceptive-alignment.md' },
  { id: 'TB-SICG', title: 'Systemic Insecure Code Generation',               file: 'systemic-insecure-code-generation.md' },
  { id: 'TB-WLLA', title: 'Weaponized LLM Abuse',                            file: 'weaponized-llm-abuse.md' },
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

// ---------- Description ----------

function buildDescription() {
  return [
    'Single ballot covering both tracks of the Sprint 2 community vote:',
    '  Track A — 10 refreshed existing entries (LLM01–LLM10)',
    '  Track B — 8 new candidate entries',
    '',
    'Estimated time: 10 minutes if you score every entry. Less if you skip ' +
    'entries you have not read. Skipping is a valid signal — it tells the ' +
    'working group an entry is niche or under-explained.',
    '',
    'WHAT TO DO',
    '1. Read each entry on GitHub (links provided per section).',
    '2. Score Importance and Clarity on a 1–5 scale. Track B adds Distinctness.',
    '3. Use the GitHub issue link under each entry for qualitative comments. ' +
    'The form captures scores. The issues capture discussion.',
    '',
    'DEFINITIONS',
    '• Importance: How critical is this risk to LLM application security in 2026?',
    '• Clarity: How clearly does the entry describe the risk and mitigations?',
    '• Distinctness (Track B only): Is this materially different from existing ' +
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

// ---------- Track A ----------

function buildTrackAEntries(form) {
  form.addPageBreakItem()
      .setTitle('Track A: Existing Entries (LLM01–LLM10)')
      .setHelpText('Score Importance and Clarity for each existing entry. ' +
                   'Leave blank any entry you have not read. Estimated time: ' +
                   '5 minutes. Track B (new candidates) follows after this section.');

  TRACK_A_ENTRIES.forEach(function (entry, idx) {
    addEntrySection(form, entry, false /* not Track B */, REPO_ENTRY_BASE, REPO_ISSUE_BASE_A);
    if (idx !== TRACK_A_ENTRIES.length - 1) {
      form.addPageBreakItem();
    }
  });
}

// ---------- Track B ----------

function buildTrackBEntries(form) {
  form.addPageBreakItem()
      .setTitle('Track B: New Candidate Entries')
      .setHelpText('Now scoring new candidates for the 2026 Top 10. Sprint 3 ' +
                   'cuts these 8 down to 5. Track B adds a third dimension — ' +
                   'Distinctness — which tells us whether a candidate stands ' +
                   'alone or should merge into an existing entry. Estimated ' +
                   'time: 5 minutes. Skip any candidate you have not read.');

  TRACK_B_ENTRIES.forEach(function (entry, idx) {
    addEntrySection(form, entry, true /* Track B */, REPO_CANDIDATE_BASE, REPO_ISSUE_BASE_B);
    if (idx !== TRACK_B_ENTRIES.length - 1) {
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
