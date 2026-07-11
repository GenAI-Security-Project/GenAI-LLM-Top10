## LLM01:2026 Prompt Injection

### Description

A **prompt-injection vulnerability** occurs when input to a large language model (LLM) — direct user input, retrieved documents, tool output, image/audio/video content, intermediate reasoning, or persistent memory — alters the model's behavior in ways the application developer did not intend. Because LLMs make no architectural distinction between "instructions" and "data" — both are tokens on the same stream (NCSC, 2025) — there is no clean equivalent to parameterized queries. Inputs need not be human-readable, need not arrive directly from a user, and need not be visible in the rendered interface to influence the model.

Prompt injection vulnerabilities exist in how models process input and how that input can force the model to pass data, or instructions, incorrectly to other parts of the system. Three deployment-time properties make this worse. First, **context-window pooling**: the model treats system prompt, user input, retrieved documents, tool outputs, conversation history, and memory as a single token stream, with no enforced trust boundary. Second, **memory persistence**: an injection that writes to long-term memory, a RAG corpus, a vector store, or a hosted memory service taints every subsequent session that reads from that store. Third, **agentic execution**: when the model's output drives tool calls — file system, shell, email, cloud APIs, MCP servers, sub-agents — the blast radius extends from the chat surface to whatever the agent's tools can reach, and tool outputs re-enter the context window, enabling chained or self-replicating effects.

A given prompt injection anatomy can be characterized along three axes: **Delivery surface** or how it reaches the model (direct input, retrieved content, tool output, tool connection channel, persistent memory, or, indirectly, a fine-tuning interface used to craft the payload); **propagation behavior** or how it spreads across time and boundaries (single-shot, multi-step kill-chain, cross-session through memory or RAG, or self-replicating across agents); and **encoding** or how the malicious instructions are represented in tokens or pixels (plain text, base64 or other obfuscation, invisible Unicode, multimodal or steganographic, low-resource language). Decomposing a scenario along these axes is a useful threat-modeling step before selecting which mitigations apply.

The severity and nature of a successful prompt injection vary with the business context the model operates in and the agency with which it is architected. Generally, prompt injection can lead to outcomes that include but are not limited to:

* Disclosure of sensitive information, system-prompt content, retrieved private documents, or infrastructure details.
* Manipulation of model output to produce biased, harmful, or attacker-chosen content that downstream systems or users act on.
* Unauthorized invocation of tools the agent is permitted to call (file system, shell, email, cloud APIs).
* Data exfiltration via image-URL channels, hidden Unicode characters in rendered output, or covert tool-logging side channels.
* Persistent compromise of agent behavior across sessions through memory or RAG corpus poisoning.
* Where the agent has shell, file-system, or cloud-API access: arbitrary command execution and destructive actions on the host or connected systems.
* Crafting of high-success-rate adversarial payloads against closed-weight production models by abusing a vendor's fine-tuning API as a gradient oracle (the "fun-tuning" class), which expands earlier white-box optimization techniques into reach against closed-weight deployments.

*Note: prompt injection differs from LLM02:2025 Sensitive Information Disclosure, which addresses what the model leaks through its outputs — including reasoning-channel content — and from LLM06:2025 Excessive Agency, which addresses the consequences of model output reaching privileged actions. This entry concerns the input boundary itself.*

---

### Types of Prompt Injection

### Direct Prompt Injection

A user, or an attacker with the user's access path, supplies input that changes model behavior in undesired ways. Direct injection can be **intentional** (a malicious user crafting a jailbreak) or **unintentional** (a legitimate user copy-pasting content that happens to contain conflicting instructions, or a user who relies on an LLM to help them and inadvertently optimizes their input against an unrelated downstream LLM — see Scenario #3). 

While prompt injection and jailbreaking are related concepts in LLM security, they are often incorrectly used interchangeably. Prompt injection involves manipulating model responses through specific inputs to alter its behavior, which can include bypassing safety measures. Jailbreaking is a subset of prompt injection where the attacker goal is to make the model violate its safety protocols. Developers can build safeguards into system prompts and input handling to help mitigate prompt injection attacks, but effective prevention of jailbreaking requires ongoing updates to the model's training and safety mechanisms.

### Indirect Prompt Injection

The model ingests content from an external source — a web page, a document, an email, a tool response, a retrieved RAG passage, an image, an MCP server's output, a database row, an issue title — that contains data which acts as prompt injection. The user did not supply or see those instructions. The trust profile of the delivery surface (axis (a) of the anatomy) determines what defenses are practical:

* **Untrusted surfaces.** Public web pages, emails from unknown senders, public files, search results. Defenders must generally treat anything from these sources as suspicious. Most prompt-injection research has focused here.
* **Semi-trusted surfaces.** Issue titles in a public bug tracker, package READMEs and changelogs, third-party API responses, content the user *chose* to retrieve but did not author. The user trusts the platform but not necessarily individual contributors.
* **Trusted surfaces.** Code in a repository the developer owns, rows in the developer's own production database, internal documents, the user's own emails or calendar, content authored by colleagues. The developer may not realize an attacker has placed content here — perhaps via an unrelated upstream vector such as a public bug-report form or a customer-facing input.

The shared structure: the attacker does not need to compromise the backend directly. They place text where the developer's LLM will read it, and the LLM — operating with the developer's privileges — does the work. Defenses that focus only on the chat surface miss this entirely. 

Indirect prompt injection is increasingly used to turn the user's own LLM instance into the weapon against the user's own backend. The pattern: an attacker submits text into a *trusted-by-the-user* location through a low-privilege channel (a public form, a customer ticket, a community pull request), and waits for the user's MCP-connected agent or developer assistant to read that text while operating under the user's elevated credentials. The agent — not the attacker — performs the privileged action. Researcher proof-of-concept attacks against production systems include a poisoned GitHub issue causing an MCP-connected coding assistant to exfiltrate private repository contents (Invariant Labs, 2025); a customer support ticket causing Cursor's Supabase MCP server to dump the production database into the user-visible support thread (General Analysis, 2025); and a crafted code comment in a third-party library causing a developer's IDE coding agent to flip a configuration flag and enable unrestricted command execution (Rehberger, 2025a).

### Common Examples of Risk

1. **Direct prompt-input override** — a user message overrides the system prompt's role and capability limits, making the model disclose, generate, or act outside its intended scope; intentional and unintentional inputs both count.

2. **Indirect injection through retrieved content** — attacker instructions ride in a RAG passage, web page, document, or email and run when the content reaches the context window (e.g., EmailGPT; INCIBE-CERT, 2024).

3. **Trusted-surface indirect injection** — text planted in a low-privilege but trusted channel (issue tracker, feedback form, support ticket) makes the user's LLM act under its own elevated credentials — exfiltrating repositories, dumping databases, or modifying IDE config — that the attacker could not do directly (Invariant Labs, 2025; General Analysis, 2025; Rehberger, 2025a).

4. **Multimodal and steganographic injection** — sub-perceptual perturbations in images, audio, or video are extracted by the encoder; all four frontier vision-language models in a 2024 oncology-imaging study were susceptible (Clusmann et al., 2025).

5. **Invisible-character injection and exfiltration** — Tag-block, variation-selector, and zero-width Unicode carry instructions or exfiltrate bytes inside benign-looking text; the August 2024 M365 Copilot ASCII-smuggling PoC exfiltrated an MFA code.

6. **Cross-session memory and RAG corpus poisoning** — one tainted entry in persistent memory or a RAG corpus reaches every future session that reads it; as few as five documents reached 97% attack success on Natural Questions (W. Zou et al., 2025).

7. **Fine-tuning interface as gradient oracle ("fun-tuning")** — an attacker reads per-example loss from a vendor's fine-tuning API to optimize a payload (65–82% ASR on Gemini), bringing white-box-style optimization to closed-weight models.

8. **Multilingual, encoded, or low-resource-language payloads** — low-resource or code-mixed translation drops refusal rates from ~79% to ~23% on identical content, and Base64/ROT13/emoji encodings evade classifiers not trained on the scheme.

---

### Prevention and Mitigation Strategies

Prompt injection vulnerabilities are intrinsic to current generative AI: LLMs make no architectural distinction between instructions and data, and their behavior is stochastic, so no robust prevention mechanism exists today — a position consistent with NIST (2025), NCSC (2025), and Debenedetti et al. (2025). Defense is therefore architectural rather than interceptive. Design the surrounding system on the explicit assumption that the model's instruction boundary will eventually be bypassed, and constrain what the model is permitted to do — and what its outputs are permitted to reach — so a successful injection does not translate into a successful exploit.

Most high-impact prompt-injection incidents on record (EchoLeak / CVE-2025-32711 [Reddy & Gujral, 2025]; the Amazon Q runtime and supply-chain pair [Amazon Web Services, 2025a, 2025b]; the Supabase MCP `service_role` exfiltration [General Analysis, 2025]; GitHub Copilot / CVE-2025-53773 [Rehberger, 2025a]) became severe not because the injection itself succeeded but because the injection landed inside a system whose tools, scopes, or output-rendering capabilities let the compromised model act on the attacker's behalf at the user's privilege level. This is the operational relationship between this entry and **LLM06:2025 Excessive Agency**: prompt injection is the input-side compromise, and excessive functionality, permissions, or autonomy are what give that compromise consequences outside the chat window. Simon Willison's "lethal trifecta" (2025) restates the same structural diagnosis as a pre-deployment check: an agent that can simultaneously (1) access private data, (2) ingest untrusted content, and (3) communicate externally has the conditions for high-impact exploitation, and removing any one leg removes them. Treat LLM01 and LLM06 as a pair when threat-modeling agentic deployments.

Apply the controls below as defense-in-depth — no single control is sufficient. Some reduce injection success (and are expected to degrade against adaptive attackers); others bound the blast radius once injection succeeds (these are what survive against attackers who can probe the system). For agentic deployments, the least-privilege and capability-budgeting controls (#4, #8) are load-bearing — see **LLM06:2025** for the full agency-side treatment.

1. **Constrain the model's role and capabilities in the system prompt.** Use declarative allow/deny statements ("assist with X only; do not access Y; do not forward output to external addresses"), not open-ended grants. A partial control only — an attacker who infers the prompt can bypass it (Nasr et al., 2025); pair with the privilege controls in #4.

2. **Define a strict output schema and validate every response in trusted application code** before any downstream system acts on it — structural validation, not a second LLM call. This catches format violations, not semantic manipulation: a schema-valid response can still carry a malicious SQL query or an exfiltration-formatted email body.

3. **Filter at every modality boundary — text, image, audio, structured data — not just text.** Run modality-specific classifiers, OCR over images, and transcription over audio, then apply text filters to the extracted content. Semantic filters are evadable by rephrasing or encoding, and accuracy drops for low-resource languages (refusal ~79% English → ~23%; Hackett et al., 2025).

4. **Hold credentials and state-change capability in application code, not the model, and grant least privilege per operation.** Route privileged calls through a deterministic policy engine that re-validates intent and arguments at execution time. NIST AI 100-2 E2025 and the CISA + Five Eyes OT joint guidance (CISA et al., 2025) frame this deterministic mediation as a baseline procurement expectation. Broad "convenience" permissions and multi-agent hops re-introduce the risk downstream.

5. **Strip Tag-block (U+E0000–E007F), variation-selector (U+FE00–FE0F), and zero-width (U+200B/C/D, U+2060) characters at every ingest and render boundary.** These are invisible in normal rendering and smuggle instructions or exfiltration bytes; the Aug 2024 M365 Copilot PoC (Rehberger, 2024) exfiltrated an MFA code this way, and variation-selector variants (Rehberger, 2025c) cut cost to ~2 characters per byte. Does not stop visible-text payloads or future stego classes.

6. **Pass external content through a structurally separate, provenance-labeled channel** so the model can distinguish data from instructions (S. Chen et al., 2025; Microsoft Research, 2025). This reduces ASR in non-adaptive tests only — an attacker who knows the marking scheme can mimic it, and StruQ was bypassed under adaptive attack (Nasr/Carlini, 2025).

7. **Require explicit human confirmation before any privileged, irreversible, or externally visible action**, surfacing the exact rendered action — not a summary — to the reviewer. Invisible-character smuggling can make the displayed action differ from the executed one (#5), and approval fatigue degrades reviewer judgment at volume.

8. **Budget agent capabilities with the Rule of Two as a floor.** Treat simultaneous access to (A) untrusted input, (B) sensitive data, and (C) state change / external comms as high-risk: any [A,B,C] agent needs per-action human approval, and [A,B]/[A,C] configurations need an explicit residual-risk assessment — the Amazon Q incident (Amazon Web Services, 2025b) wiped a developer's files from an [A,B] config. Endorsed by NIST AI 100-2 E2025 and the CISA/FBI/NSA/ACSC OT guidance (CISA et al., 2025); the rule is silent on autonomy depth (Noma Security, 2025).

9. **Treat agent memory writes as privileged operations** — log the causing prompt, classify writes for instruction or role-modification content, and require approval before instruction-bearing memories persist across sessions. A Feb 2025 Gemini PoC (Rehberger, 2025b) poisoned memory via delayed tool invocation (MITRE, n.d.). Factual entries shade into instructions, and incremental writes can evade per-write classification.

10. **Pin, sign, and verify every MCP server and third-party tool package; audit tool descriptions for hidden instructions; monitor tool composition.** Treat these as a software supply-chain surface: the malicious postmark-mcp npm package (Koi Security, 2025; Toulas, 2025) BCC'd email to an attacker for ~8 days across ~300 organizations. Pinning does not stop a payload shipped in the pinned version or tool-description poisoning that leaves the version unchanged.

11. **Test against adaptive attackers who have read your defense; reject static-only ASR claims.** Baseline with AgentDojo (Debenedetti et al., 2024) and JailbreakBench (Chao et al., 2024), then red-team with the full defense specification disclosed to the testers. Nasr et al. (2025) found static ASR near zero while adaptive ASR exceeded 90% for most of 12 recent defenses (see also LLMail-Inject, Microsoft Security Response Center, 2025).

---

### Example Attack Scenarios

**Scenario #1: Direct Injection.** An attacker prompts a customer-support chatbot to ignore its guidelines, query private data stores, and send emails — leading to unauthorized access and privilege escalation.
**Anatomy:** (a) direct user input · (b) single-shot · (c) plain text

**Scenario #2: Indirect Injection via Retrieved Web Content.** A user asks an assistant to summarize a web page containing hidden instructions; the model inserts a markdown image whose URL exfiltrates the private conversation to an attacker-controlled domain. The user sees only the rendered image, never the instruction.
**Anatomy:** (a) retrieved web content (indirect) · (b) single-shot with image-URL exfiltration · (c) plain text (hidden in page source)

**Scenario #3: Unintentional Injection.** A job-description PDF embeds an AI-detection instruction. An applicant unknowingly uses an LLM to optimize their resume against it; the model surfaces the instruction and the recruiting system flags the candidate — a prompt injection with neither party acting maliciously.
**Anatomy:** (a) indirect (document / PDF) · (b) single-shot · (c) plain text

**Scenario #4: RAG Repository Poisoning.** An attacker contributes poisoned documents to a corpus the application retrieves over; a matching query returns the modified content and its instructions alter the output. As few as five injected documents have achieved attack-success rates above 95% on standard question-answering corpora (PoisonedRAG, USENIX Security 2025).
**Anatomy:** (a) retrieved content (RAG corpus) · (b) cross-session / cross-user · (c) plain text

**Scenario #5: Payload Splitting.** An attacker splits malicious instructions across multiple resume fields (header, body, attachment) so no single field looks malicious to a per-field classifier; the LLM recombines them at evaluation and its recommendation is manipulated.
**Anatomy:** (a) direct user input (split across fields) · (b) single-shot (recombined at eval) · (c) plain text (fragmented)

**Scenario #6: Multimodal Steganographic Injection.** An attacker embeds an instruction in an image below the human visual threshold; a multimodal model's vision encoder extracts the payload and behavior changes, producing harmful output or unauthorized tool invocation. Demonstrated against four frontier vision-language models in oncology imaging (Clusmann et al., 2025) and against general-purpose models via combined visual perturbation and text steering (R. Chen et al., 2025).
**Anatomy:** (a) image input (indirect / multimodal) · (b) single-shot · (c) steganographic / pixel-level encoding

**Scenario #7: Zero-Click Document-Borne Agentic Exfiltration.** A crafted email triggers an LLM-powered productivity assistant to exfiltrate organizational data with no user interaction. Aim Security demonstrated this against Microsoft 365 Copilot (Reddy & Gujral, 2025), bypassing both the deployed prompt-injection classifier and the link-redaction filter.
**Anatomy:** (a) email / document (indirect) · (b) single-shot with tool invocation · (c) plain text with invisible-Unicode exfiltration channel

**Scenario #8: Agentic Destructive Command Execution.** Two July 2025 events show the same impact via different vectors: an attacker committed a destructive system prompt to the Amazon Q VS Code extension repository, reaching ~1 million installs before reversion (Amazon Web Services, 2025a); separately, a runtime injection caused Amazon Q to execute arbitrary code (AWS-2025-019). An agent with shell, file-system, or cloud-API access amplifies an injection into a host-impacting incident.
**Anatomy:** (a) supply-chain / compromised system prompt (AWS-2025-015) or runtime indirect injection (AWS-2025-019) · (b) persistent cross-session (supply-chain) / single-shot with shell tool execution (runtime) · (c) plain text

**Scenario #9: Trusted-Backend Indirect Injection through MCP.** An attacker plants text in a low-privilege channel — a public GitHub issue, a support ticket, or a malicious npm package — and the developer's LLM reads it under elevated credentials. Invariant Labs (2025) exfiltrated private repositories via a poisoned GitHub issue; General Analysis (2025) dumped a production database through Cursor's Supabase MCP server (running `service_role`, bypassing row-level security); the malicious `postmark-mcp` package (Koi Security, 2025) BCC'd email to an attacker for ~8 days.
**Anatomy:** (a) trusted-surface indirect (MCP channel — issue, ticket, npm package) · (b) multi-step tool-chain · (c) plain text
