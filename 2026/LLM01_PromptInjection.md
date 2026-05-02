## LLM01:2026 Prompt Injection

### Description

A **prompt-injection vulnerability** occurs when input to a large language model (LLM) — direct user input, retrieved documents, tool output, image/audio/video content, intermediate reasoning, or persistent memory — alters the model's behavior in ways the operator did not intend. Because LLMs make no architectural distinction between "instructions" and "data" — both are tokens on the same stream ([NCSC, Dec 2025](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection)) — there is no clean equivalent to parameterized queries. Inputs need not be human-readable, need not arrive directly from a user, and need not be visible in the rendered interface to influence the model.

Prompt injection vulnerabilities exist in how models process input and how that input can force the model to pass data, or instructions, incorrectly to other parts of the system. Three deployment-time properties make this worse. First, **context-window pooling**: the model treats system prompt, user input, retrieved documents, tool outputs, conversation history, and memory as a single token stream, with no enforced trust boundary. Second, **memory persistence**: an injection that writes to long-term memory, a RAG corpus, a vector store, or a hosted memory service taints every subsequent session that reads from that store. Third, **agentic execution**: when the model's output drives tool calls — file system, shell, email, cloud APIs, MCP servers, sub-agents — the blast radius extends from the chat surface to whatever the agent's tools can reach, and tool outputs re-enter the context window, enabling chained or self-replicating effects.

A given prompt injection anatomy can be characterized along three axes: **how it reaches the model** (direct input, retrieved content, tool output, MCP channel, persistent memory, or, indirectly, a fine-tuning interface used to craft the payload); **how it propagates** (single-shot, multi-step kill-chain, cross-session through memory or RAG, or self-replicating across agents); and **how it is encoded** (plain text, base64 or other obfuscation, invisible Unicode, multimodal or steganographic, low-resource language). Decomposing a scenario along these axes is a useful threat-modeling step before selecting which mitigations apply.

A single attack typically combines one item from each axis. *Example:* the [August 2024 M365 Copilot ASCII-smuggling PoC](https://embracethered.com/blog/posts/2024/m365-copilot-prompt-injection-tool-invocation-and-data-exfil-using-ascii-smuggling/) was (a) document-file delivery, (b) single-shot in the targeted session but multi-step in its tool-invocation chain, (c) Tag-block invisible Unicode encoding. Decomposing each scenario along these axes is the first step of any threat model and the framework against which each control below is evaluated.

The severity and nature of a successful prompt injection vary with the business context the model operates in and the agency with which it is architected. Generally, prompt injection can lead to outcomes that include but are not limited to:

- Disclosure of sensitive information, system-prompt content, retrieved private documents, or infrastructure details.
- Manipulation of model output to produce biased, harmful, or attacker-chosen content that downstream systems or users act on.
- Unauthorized invocation of tools the agent is permitted to call (file system, shell, email, cloud APIs).
- Data exfiltration via image-URL channels, hidden Unicode characters in rendered output, or covert tool-logging side channels.
- Persistent compromise of agent behavior across sessions through memory or RAG corpus poisoning.
- Where the agent has shell, file-system, or cloud-API access: arbitrary command execution and destructive actions on the host or connected systems.
- Crafting of high-success-rate adversarial payloads against closed-weight production models by abusing a vendor's fine-tuning API as a gradient oracle (the "fun-tuning" class), which expands earlier white-box optimization techniques into reach against closed-weight deployments.

*Note: prompt injection differs from LLM02:2025 Sensitive Information Disclosure, which addresses what the model leaks through its outputs — including reasoning-channel content — and from LLM06:2025 Excessive Agency, which addresses the consequences of model output reaching privileged actions. This entry concerns the input boundary itself.*

---

### Types of Prompt Injection

### Direct Prompt Injection

A user, or an attacker with the user's access path, supplies input that changes model behavior unexpectedly. Direct injection can be **intentional** (a malicious user crafting a jailbreak) or **unintentional** (a legitimate user copy-pasting content that happens to contain conflicting instructions, or a user who relies on an LLM to help them and inadvertently optimizes their input against an unrelated downstream LLM — see Scenario #3). 

While prompt injection and jailbreaking are related concepts in LLM security, they are often incorrectly used interchangeably. Prompt injection involves manipulating model responses through specific inputs to alter its behavior, which can include bypassing safety measures. Jailbreaking is a subset of prompt injection where the attacker goal is to make the model violate its safety protocols. Developers can build safeguards into system prompts and input handling to help mitigate prompt injection attacks, but effective prevention of jailbreaking requires ongoing updates to the model's training and safety mechanisms.



### Indirect Prompt Injection

The model ingests content from an external source — a web page, a document, an email, a tool response, a retrieved RAG passage, an image, an MCP server's output, a database row, an issue title — that contains attacker-controlled instructions. The user did not supply or see those instructions. The trust profile of the delivery surface (axis (a) of the anatomy) determines what defenses are practical:

- **Untrusted surfaces.** Public web pages, emails from unknown senders, public files, search results. Defenders generally treat anything from these sources as suspicious. Most prompt-injection research has focused here.
- **Semi-trusted surfaces.** Issue titles in a public bug tracker, package READMEs and changelogs, third-party API responses, content the user *chose* to retrieve but did not author. The user trusts the platform but not necessarily individual contributors.
- **Trusted surfaces.** Code in a repository the developer owns, rows in the developer's own production database, internal documents, the user's own emails or calendar, content authored by colleagues. The developer may not realize an attacker has placed content here — perhaps via an unrelated upstream vector such as a public bug-report form or a customer-facing input.

The shared structure: the attacker does not need to compromise the backend directly. They place text where the developer's LLM will read it, and the LLM — operating with the developer's privileges — does the work. Defenses that focus only on the chat surface miss this entirely. 

Indirect prompt injection is increasingly used to turn the user's own LLM instance into the weapon against the user's own backend. The pattern: an attacker submits text into a *trusted-by-the-user* location through a low-privilege channel (a public form, a customer ticket, a community pull request), and waits for the user's MCP-connected agent or developer assistant to read that text while operating under the user's elevated credentials. The agent — not the attacker — performs the privileged action. Researcher proof-of-concept attacks against production systems include a poisoned GitHub issue causing an MCP-connected coding assistant to exfiltrate private repository contents (Invariant Labs, May 2025); a customer support ticket causing Cursor's Supabase MCP server to dump the production database into the user-visible support thread (General Analysis, July 2025); and a crafted code comment in a third-party library causing a developer's IDE coding agent to flip a configuration flag and enable unrestricted command execution (CVE-2025-53773, August 2025).

### Common Examples of Vulnerability

1. **Direct prompt-input override.** A user-supplied message bypasses the system prompt's role and capability constraints, causing the model to disclose, generate, or act outside its intended scope. The input can be intentional or unintentional; both should be handled.

2. **Indirect injection through retrieved content.** A RAG passage, retrieved web page, document, or email contains attacker-supplied instructions that the model follows when the content reaches the context window. CVE-2024-5184 (EmailGPT, 2024) is an example of this class against a deployed Gmail extension.

3. **Trusted-surface indirect injection.** An attacker submits text through a low-privilege channel (issue tracker, customer-feedback form, support ticket) into a location the user's LLM treats as trusted. The LLM operates with the user's elevated credentials and performs privileged actions — exfiltrating private repositories, dumping databases, or modifying IDE configuration — that the attacker could not perform directly. Examples include the GitHub MCP, Supabase MCP, and GitHub Copilot / VS Code (CVE-2025-53773) cases above.

4. **Multimodal and steganographic injection.** Adversarial perturbations invisible to humans are embedded in images, audio waveforms, or video frames; vision and audio encoders extract the payload. All four frontier vision-language models tested in a 2024 oncology-imaging study (Clusmann et al., *Nature Communications*) were susceptible to sub-visual prompt injection.

5. **Invisible-character injection and exfiltration.** Tag-block characters (U+E0000–U+E007F), variation-selector characters (U+FE00–U+FE0F), and zero-width characters (U+200B/C/D, U+2060) carry instructions or exfiltrate bytes through text that appears benign in standard rendering. The August 2024 ASCII-smuggling proof-of-concept against Microsoft 365 Copilot demonstrated MFA-code exfiltration from a controlled demo workspace.

6. **Cross-session memory and RAG corpus poisoning.** An adversarial document written into persistent memory (vector store, conversation summary, hosted memory service) or into a RAG corpus influences every future session that reads from the tainted entry. As few as five injected documents achieved 97% attack success on Natural Questions in the PoisonedRAG study (USENIX Security 2025).

7. **Fine-tuning interface as gradient oracle ("fun-tuning").** An attacker with access to a vendor's fine-tuning API submits candidate adversarial inputs paired with a desired malicious target output, reads the per-example loss the API returns, and uses that loss as a gradient surrogate to drive a greedy token search. The optimized payload is then delivered through any of the standard surfaces and produces the attacker-chosen output with high reliability — 65–82% attack success on Gemini in the original paper. This brings white-box-style optimization within reach of closed-weight production deployments.

8. **Multilingual, encoded, or low-resource-language payloads.** Translation to low-resource or code-mixed languages reduces classifier accuracy substantially — refusal rates can fall from approximately 79% in English to approximately 23% in some low-resource languages on identical content. Encoding (Base64, ROT13) and emoji-substituted prompts evade text classifiers that have not been trained on the encoding scheme.

---

### Prevention and Mitigation Strategies

Prompt injection vulnerabilities are possible due to the nature of generative AI. Given the stochastic influence at the heart of the way models work, it is unclear if there are fool-proof methods of prevention for prompt injection. Modern guidance and research indicates that there is likely no way to completely prevent prompt injection today, but that controls should focus on a defense-in-depth posture, with each control recommended below considered one layer and none sufficient on its own. 

#### 1. Constrain what the model is permitted to do by writing an explicit role and capability boundary in the system prompt

Write a system prompt that names the model's role, the tasks it may perform, the data it may access, and the actions it must decline. Use declarative, affirmative statements ("You assist with X only; you do not access Y; you do not forward output to external addresses") rather than open-ended capability grants. Treat this as a partial control that reduces blast radius across axis (b) propagation behavior, not a reliable barrier across axis (a) delivery surface: an attacker who knows or guesses the system prompt's structure can craft an injection that satisfies its surface logic while still achieving a malicious goal.

**Addresses anatomy axes:** primarily (b) propagation; partial mitigation across (a).
**Assumes:** you control the system prompt and it reaches the model before user-supplied content; the model is generally instruction-following.
**Known limits:** adaptive attackers who can observe or infer the system prompt can bypass it ([Nasr/Carlini 2025](https://arxiv.org/abs/2510.09023)). Pair with architectural privilege controls (Control 4) so that a bypassed boundary does not grant access to consequential capabilities.
**Citations:** [NCSC (2025)](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection); [NIST AI 100-2 E2025 (2025)](https://csrc.nist.gov/pubs/ai/100/2/e2025/final); [Nasr/Carlini (2025)](https://arxiv.org/abs/2510.09023).
**MITRE ATLAS:** mitigates [AML.T0051.000 / .001](https://atlas.mitre.org/), partial mitigation of [AML.T0054](https://atlas.mitre.org/).

#### 2. Define a concrete output schema and validate each response against it before acting on the output

Specify the exact format of model responses (e.g., a JSON schema with named fields and permitted value ranges) and enforce compliance deterministically in application code before any downstream system consumes the output. Use structural validation rather than relying on a second LLM call to check the first.

**Addresses anatomy axes:** primarily (b) propagation — limits the actions an injected instruction can effect downstream.
**Assumes:** the format is constrained enough that injected instructions cannot be embedded inside a conformant response; validation runs in trusted application code, not inside the LLM.
**Known limits:** schema validation catches format violations, not semantic manipulation; a structurally valid response can still encode an attacker-chosen action (e.g., a valid JSON object containing a malicious SQL query, a valid email body containing exfiltration-formatted data).
**Citations:** [OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/); [NIST AI 600-1 (2024)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf).
**MITRE ATLAS:** [AML.T0051.000 / .001](https://atlas.mitre.org/), partial mitigation of [AML.T0102](https://atlas.mitre.org/) (Generate Malicious Commands).

#### 3. Apply input and output filters at every modality boundary — text, image, audio, and structured data — not only at the text layer

Define categories of sensitive or prohibited content and enforce filtering at each point where untrusted content enters the model context and where model output exits to downstream systems. Text-only filters are insufficient: vision encoders process image content holistically, and pixel-level steganographic payloads can carry instructions invisible to humans and to text classifiers. Run modality-specific classifiers, OCR over images, and transcription over audio; pass extracted text through the same text-based filters. Filtering accuracy degrades for low-resource languages — refusal rates can fall from ~79% (English) to ~23% (some low-resource languages) on identical content ([arXiv:2504.11168, 2025](https://arxiv.org/html/2504.11168v2)).

**Addresses anatomy axes:** primarily (c) encoding; partial across (a).
**Assumes:** the application controls the content pipeline; modality-specific classifiers exist and have been evaluated on adversarial examples.
**Known limits:** semantic filters can be evaded by rephrasing or encoding; no filter set has demonstrated complete coverage as of Apr 2026; pixel-level adversarial perturbations bypass image safety classifiers not trained on adversarial examples.
**Citations:** [Clusmann et al. *Nature Communications* (2024)](https://www.nature.com/articles/s41467-024-55631-x); [Wang et al. *JPS* ACM MM (2025)](https://dl.acm.org/doi/10.1145/3746027.3754561); [arXiv:2504.11168 (2025)](https://arxiv.org/html/2504.11168v2).
**MITRE ATLAS:** [AML.T0051.000 / .001, AML.T0068](https://atlas.mitre.org/); see Control 5 for Unicode-specific normalization.

#### 4. Grant the LLM only the minimum permissions it needs for each operation, and hold API credentials and state-change capabilities in application code, not in the model context

Provision the application layer — not the model — with API tokens, database write access, file-system permissions, and external communication channels. The model receives structured requests and returns structured responses; application code performs the privileged operation only after validating the response. Where possible, route privileged calls through a deterministic policy engine that re-validates intent and arguments at execution time, not only at agent startup.

**Addresses anatomy axes:** primarily (b) propagation; structural mitigation against (a) trusted-surface attacks.
**Assumes:** the application can interpose between model output and privileged action; tool calls are auditable before execution.
**Known limits:** broad permissions granted "for convenience" degrade this control; an injection that passes application-layer validation may still execute. Multi-agent pipelines can re-introduce the full property set at a downstream node, undoing the boundary established here.
**Citations:** [NCSC (2025)](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection); [NIST AI 100-2 E2025 (2025)](https://csrc.nist.gov/pubs/ai/100/2/e2025/final); [NIST AI 600-1 (2024)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf).
**MITRE ATLAS:** [AML.T0051.001, AML.T0086, AML.T0099, AML.T0102](https://atlas.mitre.org/); see Control 8 for Rule of Two capability budgeting.

#### 5. Strip or reject Tag-block, variation-selector, and zero-width Unicode characters at every boundary where untrusted content enters the model context or where model output is rendered

Apply Unicode normalization at each ingest point (API gateway, document parser, email, tool output) and at each render point (UI, downstream system, log). Remove or replace Tag-block (U+E0000–U+E007F), variation-selector (U+FE00–U+FE0F), and zero-width classes (U+200B/C/D, U+2060). These character classes are visually invisible in standard rendering and allow attackers to embed instructions or exfiltration-formatted bytes inside text that appears benign. The [August 2024 PoC against M365 Copilot (Embrace The Red)](https://embracethered.com/blog/posts/2024/m365-copilot-prompt-injection-tool-invocation-and-data-exfil-using-ascii-smuggling/) demonstrated MFA-code exfiltration; subsequent variant-selector techniques ([Embrace The Red, 2025](https://embracethered.com/blog/posts/2025/sneaky-bits-and-ascii-smuggler/)) reduced cost to ~2 invisible characters per byte.

**Addresses anatomy axes:** primarily (c) encoding — invisible-Unicode subclass.
**Assumes:** normalization runs in trusted application code; the same scheme is applied at both ingest and render boundaries.
**Known limits:** does not prevent injection through visible-text payloads; future steganographic categories outside the normalization list will evade until added; very aggressive normalization may break legitimate multilingual content.
**Citations:** [Embrace The Red (2024)](https://embracethered.com/blog/posts/2024/m365-copilot-prompt-injection-tool-invocation-and-data-exfil-using-ascii-smuggling/); [NIST AI 100-2 E2025 (2025)](https://csrc.nist.gov/pubs/ai/100/2/e2025/final); [Promptfoo ASCII-smuggling docs](https://www.promptfoo.dev/docs/red-team/plugins/ascii-smuggling/).
**MITRE ATLAS:** [AML.T0068, AML.T0057](https://atlas.mitre.org/).

#### 6. Pass external content to the model through a structurally separate, explicitly labeled channel so the model can distinguish trusted instructions from untrusted data

Mark each piece of content with its provenance before context assembly. Use structural separators — encoding schemes, prompt-level markers, or formatting the model has been trained to recognize as a trust signal — to reduce the probability that the model will treat externally sourced data as an instruction. Academic work on structured-channel separation ([Chen et al. *StruQ*, USENIX Security 2025](https://www.usenix.org/system/files/usenixsecurity25-chen-sizhe.pdf)) and provenance marking at the prompt level (sometimes called "spotlighting" — [Microsoft Research, 2025](https://www.microsoft.com/en-us/research/publication/defending-against-indirect-prompt-injection-attacks-with-spotlighting/)) reduce ASR substantially in non-adaptive evaluations, but adaptive bypass rates are materially higher.

**Addresses anatomy axes:** primarily (a) delivery surface — explicitly marks each surface's trust level.
**Assumes:** the application controls context assembly; the model is fine-tuned for or evaluated against the marking scheme in use.
**Known limits:** an attacker who knows the marking scheme can mimic the marker format to "break out" of the data channel; multi-hop retrieval can introduce payloads after initial separation; [StruQ and related defenses were bypassed under adaptive attack (Nasr/Carlini, 2025)](https://arxiv.org/abs/2510.09023).
**Citations:** [Chen et al. *StruQ* (2025)](https://www.usenix.org/system/files/usenixsecurity25-chen-sizhe.pdf); [NCSC (2025)](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection); [Microsoft Research (2025) — Vendor](https://www.microsoft.com/en-us/research/publication/defending-against-indirect-prompt-injection-attacks-with-spotlighting/).
**MITRE ATLAS:** [AML.T0051.001, AML.T0099, AML.T0070](https://atlas.mitre.org/).

#### 7. Require explicit, informed human confirmation before any privileged, irreversible, or externally visible action is taken

Identify high-risk operations — sending email, executing code, deleting records, calling external APIs, writing to persistent storage — and route them through a confirmation step that surfaces the specific action verbatim to a human reviewer before execution. The reviewer must see the exact rendered text of what will be done, not a summary.

**Addresses anatomy axes:** primarily (b) propagation — caps single-shot and multi-step kill-chain depth.
**Assumes:** the confirmation interface strips or exposes invisible Unicode (Control 5); the reviewer has sufficient context to evaluate the action.
**Known limits:** invisible-character smuggling can cause the displayed action to differ from the executed action ([Embrace The Red 2024](https://embracethered.com/blog/posts/2024/m365-copilot-prompt-injection-tool-invocation-and-data-exfil-using-ascii-smuggling/)); approval fatigue degrades reviewer judgment at high volume; multi-step "galaxy-brained" reasoning can produce plausible justifications for harmful actions.
**Citations:** [NCSC (2025)](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection); [Embrace The Red (2024)](https://embracethered.com/blog/posts/2024/m365-copilot-prompt-injection-tool-invocation-and-data-exfil-using-ascii-smuggling/); [NIST AI 600-1 (2024)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf).
**MITRE ATLAS:** [AML.T0051.001, AML.T0086, AML.T0102, AML.T0105](https://atlas.mitre.org/).

#### 8. Budget agent capabilities explicitly using the Rule of Two as a minimum baseline, and audit each [A,B], [A,C], and [B,C] configuration for residual risk

Identify whether each agent simultaneously has access to (A) untrusted input, (B) sensitive systems / private data, and (C) state change / external comms. Any [A,B,C] configuration requires per-action human approval. For [A,B] and [A,C] configurations, perform an explicit residual-risk assessment: the [Amazon Q July 2025 incident](https://aws.amazon.com/security/security-bulletins/AWS-2025-019/) demonstrated an [A,B] configuration was exploited to wipe a developer's local file system and delete cloud resources when injected instructions bypassed Human-in-the-Loop confirmation. The underlying principle — minimize the privileged-action surface available to an LLM acting on untrusted input — is independently endorsed by [NIST AI 100-2 E2025 (Mar 2025)](https://csrc.nist.gov/pubs/ai/100/2/e2025/final) and the [CISA / FBI / NSA / ACSC + allied joint guidance on AI in operational technology (Dec 2025)](https://www.cisa.gov/sites/default/files/2025-12/joint-guidance-principles-for-the-secure-integration-of-artificial-intelligence-in-operational-technology-508c.pdf), which warn against process-model drift and unmediated agent control of safety-critical systems. Treat the Rule of Two as a floor, not a ceiling: layer least-privilege, tool-call allowlisting, and per-operation approval proportionate to damage potential.

**Addresses anatomy axes:** primarily (b) propagation — caps multi-step kill-chain depth and lateral spread; secondary mitigation across (a).
**Assumes:** agent capabilities and data access can be enumerated at design time; human-approval mechanisms exist for state-changing actions.
**Known limits:** the rule is silent on agent autonomy depth ([Noma Security critique, 2025](https://noma.security/blog/mcp-servers-agentic-risk-and-the-framework-that-protects-it/)); multi-agent pipelines can re-introduce the full property set downstream.
**Citations:** [NIST AI 100-2 E2025 (2025)](https://csrc.nist.gov/pubs/ai/100/2/e2025/final); [CISA + allied OT guidance (2025)](https://www.cisa.gov/sites/default/files/2025-12/joint-guidance-principles-for-the-secure-integration-of-artificial-intelligence-in-operational-technology-508c.pdf); [Meta (2025) — Vendor](https://ai.meta.com/blog/practical-ai-agent-security/); [Noma Security (2025)](https://noma.security/blog/mcp-servers-agentic-risk-and-the-framework-that-protects-it/); [AWS-2025-019 (2025) — Vendor](https://aws.amazon.com/security/security-bulletins/AWS-2025-019/).
**MITRE ATLAS:** [AML.T0051.001, AML.T0086, AML.T0099, AML.T0102, AML.T0105](https://atlas.mitre.org/).

#### 9. Treat agent memory writes as privileged operations: log the causing prompt, classify writes for instruction content, and require approval before instruction-containing memories persist across sessions

When an agent maintains persistent memory (vector DB, key-value store, conversation history, hosted memory service), treat each write as a privileged action subject to the same controls as an external API call. Log the exact prompt and context that triggered each write. Apply a classifier to the content; if it contains instructions, directives, or role-modification language, route it to human or policy review before persisting. A [Feb 2025 PoC against Gemini Advanced](https://embracethered.com/blog/posts/2025/google-gemini-memory-persistence-prompt-injection/) demonstrated cross-session memory poisoning via delayed tool invocation; [MITRE ATLAS classifies this as AML.T0080.001](https://atlas.mitre.org/) (AI Agent Context Poisoning: Memory).

**Addresses anatomy axes:** primarily (b) propagation — cross-session subclass; secondary on (a) memory delivery surface.
**Assumes:** the application has a write hook / audit log; a classifier exists for distinguishing factual entries from behavioral instructions; memory writes are separable from reads architecturally.
**Known limits:** factual memories shade into instructions; multi-step poisoning can evade per-write classification; many small writes can assemble a poisoned set incrementally.
**Citations:** [MITRE ATLAS AML.T0080 (2024)](https://atlas.mitre.org/); [Embrace The Red (2025)](https://embracethered.com/blog/posts/2025/google-gemini-memory-persistence-prompt-injection/).
**MITRE ATLAS:** [AML.T0080.001, AML.T0051.001](https://atlas.mitre.org/).

#### 10. Pin, sign, and verify every Model Context Protocol (MCP) server and third-party tool package your agents use; audit tool descriptions for hidden instructions; and monitor for changes in tool composition

Treat MCP servers and third-party tool packages as a software supply-chain surface. Pin versions; verify package signatures or content hashes at install and at startup; audit tool descriptions and schema definitions for embedded instructions or unusual permission requests; monitor tool composition for unauthorized additions. The [postmark-mcp incident (Sept 2025)](https://www.koi.ai/blog/postmark-mcp-npm-malicious-backdoor-email-theft) — corroborated by [BleepingComputer](https://www.bleepingcomputer.com/news/security/unofficial-postmark-mcp-npm-silently-stole-users-emails/) — demonstrated a malicious npm package silently BCC'd email content to an attacker for ~8 days, affecting an estimated 300 organizations. The [GitHub MCP Server vulnerability (Invariant Labs, May 2025)](https://invariantlabs.ai/blog/mcp-github-vulnerability) and the [Supabase MCP database-leak PoC (General Analysis, July 2025)](https://generalanalysis.com/blog/supabase-mcp-blog) demonstrated indirect prompt injection through trusted-but-attacker-influenced surfaces (a public GitHub issue; a customer-submitted support ticket) causing private-data exfiltration via agent tool calls.

**Addresses anatomy axes:** primarily (a) MCP delivery surface; secondary on (b) propagation through trusted-surface chains.
**Assumes:** the organization controls which MCP servers agents may connect to; verification runs before agent startup; tool descriptions are treated as untrusted.
**Known limits:** version pinning does not protect against a payload introduced in a version already pinned; tool-description poisoning may not change the version number; baseline tool-composition enumeration must be actively maintained.
**Citations:** [Koi Security (2025)](https://www.koi.ai/blog/postmark-mcp-npm-malicious-backdoor-email-theft); [Invariant Labs (2025)](https://invariantlabs.ai/blog/mcp-github-vulnerability); [General Analysis (2025)](https://generalanalysis.com/blog/supabase-mcp-blog); [Hou et al. ACM TOSEM (2025)](https://dl.acm.org/doi/10.1145/3796519).
**MITRE ATLAS / ATT&CK:** [AML.T0110, AML.T0099, AML.T0051.001, AML.T0086](https://atlas.mitre.org/); [ATT&CK T1195](https://attack.mitre.org/techniques/T1195/) (Supply Chain Compromise) for the package-delivery phase.

#### 11. Test your defenses against adaptive attackers — assume the attacker has read the defense — and reject vendor or internal claims based only on static-attack evaluations

Static test suites underestimate real-world ASR (Attack Success Rate) because they measure attackers who cannot adapt. For in-house evaluation, use structured agent-evaluation frameworks ([AgentDojo, NeurIPS 2024](https://arxiv.org/abs/2406.13352): 97 tasks, 629 security test cases) and standardized adversarial-prompt benchmarks ([JailbreakBench, NeurIPS 2024](https://arxiv.org/abs/2404.01318)) as a baseline; augment with adaptive red-team exercises in which the testers receive the full defense specification and are allowed to optimize against it. For procurement and acceptance: require any defense's ASR to be measured the same way before relying on it. [Nasr, Carlini et al. (Oct 2025)](https://arxiv.org/abs/2510.09023) showed that for most of 12 recent defenses, static ASR was near zero while adaptive ASR exceeded 90%. The [LLMail-Inject challenge (Microsoft MSRC / SaTML 2025)](https://www.microsoft.com/en-us/msrc/blog/2025/03/announcing-the-winners-of-the-adaptive-prompt-injection-challenge-llmail-inject/) is one example of partially-competitive adaptive evaluation in practice.

**Addresses anatomy axes:** evaluation coverage across all three (a/b/c).
**Assumes:** the testing team has white-box or gray-box access to the defense; evaluation is repeated after every significant change to model, prompt, classifier rules, or tool configuration; procurement decisions weigh adaptive-attack ASR rather than vendor-supplied static figures.
**Known limits:** adaptive testing is bounded by the testers' compute and creativity; results from one model or version may not transfer; adaptive evaluation does not scale to high-frequency deployment changes; the procurement gate depends on a vendor's willingness to expose enough of the defense for meaningful adaptive testing.
**Citations:** [Nasr/Carlini (2025)](https://arxiv.org/abs/2510.09023); [Debenedetti et al. *AgentDojo* (2024)](https://arxiv.org/abs/2406.13352); [Chao et al. *JailbreakBench* (2024)](https://arxiv.org/abs/2404.01318); [Microsoft LLMail-Inject (2025) — Vendor](https://www.microsoft.com/en-us/msrc/blog/2025/03/announcing-the-winners-of-the-adaptive-prompt-injection-challenge-llmail-inject/).
**MITRE ATLAS:** evaluation coverage for [AML.T0051.000 / .001, AML.T0054, AML.T0065, AML.T0068](https://atlas.mitre.org/).

---

### Example Attack Scenarios

**Scenario #1: Direct Injection.** An attacker injects a prompt into a customer-support chatbot, instructing it to ignore previous guidelines, query private data stores, and send emails — leading to unauthorized access and privilege escalation.

**Anatomy:** (a) direct user input · (b) single-shot · (c) plain text

**Citations:** [OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/); [NIST AI 100-2 E2025 (2025)](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)

---

**Scenario #2: Indirect Injection via Retrieved Web Content.** A user asks an LLM-powered assistant to summarize a webpage that contains hidden instructions. The model follows the instructions and inserts a markdown image whose URL exfiltrates the user's private conversation context to an attacker-controlled domain. The user never sees the instruction; they may see the rendered image.

**Anatomy:** (a) retrieved web content (indirect) · (b) single-shot with image-URL exfiltration · (c) plain text (hidden in page source)

**Citations:** [Greshake et al. "Not What You've Signed Up For" arXiv:2302.12173 (2023)](https://arxiv.org/abs/2302.12173); [NCSC "Prompt injection is not SQL injection" (2025)](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection)

---

**Scenario #3: Unintentional Injection.** A company embeds an AI-detection instruction in a job-description PDF. An applicant, unaware of the instruction, uses an LLM to optimize their resume against the JD. The model surfaces the AI-detection instruction during evaluation and the recruiting system flags the candidate. This is a prompt injection caused by neither party acting maliciously.

**Anatomy:** (a) indirect (document / PDF) · (b) single-shot · (c) plain text

**Citations:** [Kai Greshake "Inject My PDF" (2023)](https://kai-greshake.de/posts/inject-my-pdf); [OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

---

**Scenario #4: RAG Repository Poisoning.** An attacker contributes documents to a corpus the application retrieves over. When a user's query returns the modified content, the malicious instructions alter the LLM's output. As few as five injected documents have been shown to achieve attack-success rates above 95% on standard question-answering corpora ([PoisonedRAG, USENIX Security 2025](https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf)).

**Anatomy:** (a) retrieved content (RAG corpus) · (b) cross-session / cross-user · (c) plain text

**Citations:** [Zou et al. *PoisonedRAG*, USENIX Security 2025](https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf); [NIST AI 100-2 E2025 (2025)](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)

---

**Scenario #5: Payload Splitting.** An attacker submits a resume with malicious instructions split across multiple input fields (header, body, attachment) such that no individual field looks malicious to a single-field classifier. When the LLM evaluates the candidate, the recombined instructions manipulate the model's recommendation.

**Anatomy:** (a) direct user input (split across fields) · (b) single-shot (recombined at eval) · (c) plain text (fragmented)

**Citations:** [Greshake et al. "Not What You've Signed Up For" arXiv:2302.12173 (2023)](https://arxiv.org/abs/2302.12173); [OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

---

**Scenario #6: Multimodal Steganographic Injection.** An attacker embeds a malicious instruction within an image at the pixel level, below human visual threshold. When a multimodal LLM processes the image alongside benign text, the vision encoder extracts the payload and the model's behavior changes — leading to harmful output or unauthorized tool invocation. This class has been demonstrated against four frontier vision-language models in a domain-specific (oncology) deployment ([Clusmann et al., *Nature Communications*, 2024](https://www.nature.com/articles/s41467-024-55631-x)) and against general-purpose multimodal models via combined visual perturbation and text steering ([JPS, ACM MM 2025](https://dl.acm.org/doi/10.1145/3746027.3754561)).

**Anatomy:** (a) image input (indirect / multimodal) · (b) single-shot · (c) steganographic / pixel-level encoding

**Citations:** [Clusmann et al., *Nature Communications* (2024)](https://www.nature.com/articles/s41467-024-55631-x); [Wang et al. *JPS*, ACM MM (2025)](https://dl.acm.org/doi/10.1145/3746027.3754561)

---

**Scenario #7: Zero-Click Document-Borne Agentic Exfiltration.** A crafted email triggers an LLM-powered productivity assistant to exfiltrate organizational data without user interaction. Aim Security researchers demonstrated this class against Microsoft 365 Copilot ([CVE-2025-32711, "EchoLeak", patched June 2025](https://arxiv.org/abs/2509.10540)), bypassing both the deployed prompt-injection classifier and the link-redaction filter.

**Anatomy:** (a) email / document (indirect) · (b) single-shot with tool invocation · (c) plain text with invisible-Unicode exfiltration channel

**Citations:** [Reddy and Gujral, "EchoLeak" arXiv:2509.10540 (2025)](https://arxiv.org/abs/2509.10540); [NVD CVE-2025-32711](https://nvd.nist.gov/vuln/detail/CVE-2025-32711)

---

**Scenario #8: Agentic Destructive Command Execution.** Two events from July 2025 illustrate the same impact through different attack vectors. In one, an attacker compromised access to the Amazon Q VS Code extension repository and committed a system prompt instructing deletion of home directories and AWS resources; the malicious version reached approximately one million installs before reversion ([AWS-2025-015](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/)). In the other, a separately demonstrated runtime injection caused Amazon Q to execute arbitrary code through prompt injection alone ([AWS-2025-019](https://aws.amazon.com/security/security-bulletins/AWS-2025-019/)). Both surface the same risk: an agent with shell, file-system, or cloud-API access amplifies an injection into a host-impacting incident.

**Anatomy:** (a) supply-chain / compromised system prompt (AWS-2025-015) or runtime indirect injection (AWS-2025-019) · (b) persistent cross-session (supply-chain) / single-shot with shell tool execution (runtime) · (c) plain text

**Citations:** [AWS-2025-015](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/); [AWS-2025-019](https://aws.amazon.com/security/security-bulletins/AWS-2025-019/)

---

**Scenario #9: Trusted-Backend Indirect Injection through MCP.** An attacker submits crafted text into a low-privilege channel — a public GitHub issue, a customer support ticket, or a malicious npm package the developer installs — and the developer's LLM reads it while operating under elevated credentials. In May 2025, Invariant Labs showed that a malicious GitHub issue caused an MCP-connected coding assistant to exfiltrate private repository contents. In July 2025, General Analysis showed that a customer support ticket caused Cursor's Supabase MCP server (running with `service_role` privileges that bypass row-level security) to dump the production database into the user-visible support thread. In September 2025, a malicious `postmark-mcp` npm package silently BCC'd email content to an attacker for approximately eight days before discovery.

**Anatomy:** (a) trusted-surface indirect (MCP channel — issue, ticket, npm package) · (b) multi-step tool-chain · (c) plain text

**Citations:** [Invariant Labs (May 2025)](https://invariantlabs.ai/blog/mcp-github-vulnerability); [General Analysis (July 2025)](https://generalanalysis.com/blog/supabase-mcp-blog); [Koi Security (Sept 2025)](https://www.koi.ai/blog/postmark-mcp-npm-malicious-backdoor-email-theft)

### Reference Links

1. [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173): Greshake et al., **arXiv** 2023
2. [Inject My PDF: Prompt Injection for your Resume](https://kai-greshake.de/posts/inject-my-pdf): **Kai Greshake**, 2023
3. [Universal and Transferable Adversarial Attacks on Aligned Language Models](https://arxiv.org/abs/2307.15043): Zou et al., **arXiv** 2023
4. [Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations (NIST AI 100-2 E2025)](https://csrc.nist.gov/pubs/ai/100/2/e2025/final): **NIST**, March 2025
5. [Generative AI Profile (NIST AI 600-1)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf): **NIST**, July 2024
6. [Prompt injection is not SQL injection](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection): **UK NCSC**, December 2025
7. [Principles for the Secure Integration of AI in Operational Technology](https://www.cisa.gov/sites/default/files/2025-12/joint-guidance-principles-for-the-secure-integration-of-artificial-intelligence-in-operational-technology-508c.pdf): **CISA + FBI + NSA + ACSC + allied partners**, December 2025
8. [The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections](https://arxiv.org/abs/2510.09023): Nasr, Carlini et al., October 2025
9. [Prompt injection attacks on vision language models in oncology](https://www.nature.com/articles/s41467-024-55631-x): Clusmann et al., ***Nature Communications***, 2024
10. [JPS: Jailbreak Multimodal LLMs with Collaborative Visual Perturbation and Textual Steering](https://dl.acm.org/doi/10.1145/3746027.3754561): Wang et al., **ACM MM 2025**
11. [Bypassing Prompt Injection Guardrails via Code-Switching and Unicode Transcoding](https://arxiv.org/html/2504.11168v2): **arXiv**:2504.11168, 2025
12. [PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation](https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf): Zou et al., **USENIX Security 2025**
13. [StruQ: Defending Against Prompt Injection with Structured Queries](https://www.usenix.org/system/files/usenixsecurity25-chen-sizhe.pdf): Chen et al., **USENIX Security 2025**
14. [Fun-tuning: Characterizing the Vulnerability of Proprietary LLMs to Optimization-based Prompt Injection Attacks via the Fine-Tuning Interface](https://arxiv.org/abs/2501.09798): Labunets et al., **arXiv** 2501.09798, January 2025
15. [Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions](https://dl.acm.org/doi/10.1145/3796519): Hou et al., **ACM TOSEM 2025**
16. [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352): Debenedetti et al., **NeurIPS 2024**
17. [JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models](https://arxiv.org/abs/2404.01318): Chao et al., **NeurIPS 2024**
18. [M365 Copilot Prompt Injection, Tool Invocation and Data Exfil using ASCII Smuggling](https://embracethered.com/blog/posts/2024/m365-copilot-prompt-injection-tool-invocation-and-data-exfil-using-ascii-smuggling/): Johann Rehberger (**Embrace The Red**), August 2024
19. [Sneaky Bits & ASCII Smuggler updates](https://embracethered.com/blog/posts/2025/sneaky-bits-and-ascii-smuggler/): Johann Rehberger (**Embrace The Red**), 2025
20. [Hacking Gemini's Memory with Prompt Injection and Delayed Tool Invocation](https://embracethered.com/blog/posts/2025/google-gemini-memory-persistence-prompt-injection/): Johann Rehberger, February 2025
21. [GitHub Copilot Remote Code Execution via Prompt Injection (CVE-2025-53773)](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/): Johann Rehberger, 2025
22. [Promptfoo ASCII-smuggling red-team plugin docs](https://www.promptfoo.dev/docs/red-team/plugins/ascii-smuggling/): **Promptfoo**
23. [GitHub MCP Server Vulnerability](https://invariantlabs.ai/blog/mcp-github-vulnerability): **Invariant Labs**, May 2025
24. [Supabase MCP can leak your entire SQL database](https://generalanalysis.com/blog/supabase-mcp-blog): **General Analysis**, July 2025
25. [Postmark-MCP npm Malicious Backdoor — Email Theft](https://www.koi.ai/blog/postmark-mcp-npm-malicious-backdoor-email-theft): **Koi Security**, September 2025
26. [Unofficial Postmark MCP npm package silently stole users' emails](https://www.bleepingcomputer.com/news/security/unofficial-postmark-mcp-npm-silently-stole-users-emails/): **BleepingComputer**, September 2025
27. [Defending Against Indirect Prompt Injection Attacks With Spotlighting](https://www.microsoft.com/en-us/research/publication/defending-against-indirect-prompt-injection-attacks-with-spotlighting/): **Microsoft Research**, 2025
28. [Announcing the Winners of the Adaptive Prompt Injection Challenge — LLMail-Inject](https://www.microsoft.com/en-us/msrc/blog/2025/03/announcing-the-winners-of-the-adaptive-prompt-injection-challenge-llmail-inject/): **Microsoft MSRC**, March 2025
29. [Practical AI Agent Security: Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/): **Meta AI**, October 2025
30. [Why the Rule of Two Can't Protect Your Agents](https://noma.security/blog/mcp-servers-agentic-risk-and-the-framework-that-protects-it/): **Noma Security**, 2025
31. [AWS-2025-015 (Amazon Q VS Code extension supply-chain incident)](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/): **AWS Security Bulletin**, July 2025
32. [AWS-2025-019 (Amazon Q runtime injection)](https://aws.amazon.com/security/security-bulletins/AWS-2025-019/): **AWS Security Bulletin**, July 2025
33. [EchoLeak (CVE-2025-32711) — Microsoft 365 Copilot zero-click prompt injection](https://arxiv.org/abs/2509.10540): Reddy and Gujral, **Aim Security, AAAI Fall Symposium 2025**; paired with [NVD entry](https://nvd.nist.gov/vuln/detail/CVE-2025-32711)
34. [CVE-2024-5184 (EmailGPT) advisory](https://www.incibe.es/en/incibe-cert/early-warning/vulnerabilities/cve-2024-5184): **INCIBE-CERT**, 2024

---
### Related Frameworks and Taxonomies

Refer to this section for comprehensive information, scenarios, strategies, and best practices that complement this entry.

- AML.T0051.000 — LLM Prompt Injection: Direct (MITRE ATLAS)
- AML.T0051.001 — LLM Prompt Injection: Indirect (MITRE ATLAS)
- AML.T0054 — LLM Jailbreak Injection: Direct (MITRE ATLAS)
- AML.T0068 — LLM Prompt Obfuscation (MITRE ATLAS)
- AML.T0080.001 — AI Agent Context Poisoning: Memory (MITRE ATLAS)
- AML.T0099 — AI Agent Tool Data Poisoning (MITRE ATLAS)
- AML.T0086 — Exfiltration via AI Agent Tool Invocation (MITRE ATLAS)
- AML.T0102 — Generate Malicious Commands (MITRE ATLAS)
- AML.T0105 — Escape to Host (MITRE ATLAS)
- AML.T0110 — AI Agent Tool Poisoning (MITRE ATLAS)
- T1195 — Supply Chain Compromise (MITRE ATT&CK)
- NIST AI 100-2 E2025 — Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations
- OWASP AIVSS — AI Vulnerability Scoring System
