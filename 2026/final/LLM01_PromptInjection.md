## LLM01:2026 Prompt Injection

### Description

A **prompt-injection vulnerability** occurs when input to a large language model (LLM) — direct user input, retrieved documents, tool output, image/audio/video content, intermediate reasoning, or persistent memory — alters the model's behavior in ways the application developer did not intend. Because LLMs make no architectural distinction between "instructions" and "data" — both are tokens on the same stream (NCSC, Dec 2025) — there is no clean equivalent to parameterized queries. Inputs need not be human-readable, need not arrive directly from a user, and need not be visible in the rendered interface to influence the model.

Prompt injection vulnerabilities exist in how models process input and how that input can force the model to pass data, or instructions, incorrectly to other parts of the system. Three deployment-time properties make this worse. First, **context-window pooling**: the model treats system prompt, user input, retrieved documents, tool outputs, conversation history, and memory as a single token stream, with no enforced trust boundary. Second, **memory persistence**: an injection that writes to long-term memory, a RAG corpus, a vector store, or a hosted memory service taints every subsequent session that reads from that store. Third, **agentic execution**: when the model's output drives tool calls — file system, shell, email, cloud APIs, MCP servers, sub-agents — the blast radius extends from the chat surface to whatever the agent's tools can reach, and tool outputs re-enter the context window, enabling chained or self-replicating effects.

A given prompt injection anatomy can be characterized along three axes: **Delivery surface** or how it reaches the model (direct input, retrieved content, tool output, tool connection channel, persistent memory, or, indirectly, a fine-tuning interface used to craft the payload); **propagation behavior** or how it spreads across time and boundaries (single-shot, multi-step kill-chain, cross-session through memory or RAG, or self-replicating across agents); and **encoding** or how the malicious instructions are represented in tokens or pixels (plain text, base64 or other obfuscation, invisible Unicode, multimodal or steganographic, low-resource language). Decomposing a scenario along these axes is a useful threat-modeling step before selecting which mitigations apply.

A single attack typically combines one item from each axis. *Example:* the August 2024 M365 Copilot ASCII-smuggling PoC (Embrace The Red) was (a) document-file delivery, (b) single-shot in the targeted session but multi-step in its tool-invocation chain, (c) Tag-block invisible Unicode encoding. Decomposing each scenario along these axes is the first step of any threat model and the framework against which each control below is evaluated.

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

Indirect prompt injection is increasingly used to turn the user's own LLM instance into the weapon against the user's own backend. The pattern: an attacker submits text into a *trusted-by-the-user* location through a low-privilege channel (a public form, a customer ticket, a community pull request), and waits for the user's MCP-connected agent or developer assistant to read that text while operating under the user's elevated credentials. The agent — not the attacker — performs the privileged action. Researcher proof-of-concept attacks against production systems include a poisoned GitHub issue causing an MCP-connected coding assistant to exfiltrate private repository contents (Invariant Labs, May 2025); a customer support ticket causing Cursor's Supabase MCP server to dump the production database into the user-visible support thread (General Analysis, July 2025); and a crafted code comment in a third-party library causing a developer's IDE coding agent to flip a configuration flag and enable unrestricted command execution (CVE-2025-53773, August 2025).

### Common Examples of Risk

1. **Direct prompt-input override.** A user-supplied message bypasses the system prompt's role and capability constraints, causing the model to disclose, generate, or act outside its intended scope. The input can be intentional or unintentional; both should be handled.

2. **Indirect injection through retrieved content.** A RAG passage, retrieved web page, document, or email contains attacker-supplied instructions that the model follows when the content reaches the context window. CVE-2024-5184 (EmailGPT, 2024) is an example against a deployed Gmail extension.

3. **Trusted-surface indirect injection.** An attacker submits text through a low-privilege channel (issue tracker, feedback form, support ticket) into a location the user's LLM treats as trusted; the LLM then performs privileged actions under the user's credentials — exfiltrating repositories, dumping databases, or modifying IDE configuration — that the attacker could not perform directly (GitHub MCP, Supabase MCP, CVE-2025-53773).

4. **Multimodal and steganographic injection.** Adversarial perturbations invisible to humans are embedded in images, audio, or video frames; vision and audio encoders extract the payload. All four frontier vision-language models tested in a 2024 oncology-imaging study (Clusmann et al., *Nature Communications*) were susceptible.

5. **Invisible-character injection and exfiltration.** Tag-block (U+E0000–U+E007F), variation-selector (U+FE00–U+FE0F), and zero-width (U+200B/C/D, U+2060) characters carry instructions or exfiltrate bytes through text that appears benign in standard rendering. The August 2024 ASCII-smuggling PoC against Microsoft 365 Copilot demonstrated MFA-code exfiltration.

6. **Cross-session memory and RAG corpus poisoning.** An adversarial document written into persistent memory or a RAG corpus influences every future session that reads the tainted entry. As few as five injected documents achieved 97% attack success on Natural Questions (PoisonedRAG, USENIX Security 2025).

7. **Fine-tuning interface as gradient oracle ("fun-tuning").** An attacker abuses a vendor's fine-tuning API — pairing candidate inputs with a target output and reading the returned per-example loss as a gradient surrogate — to optimize a payload that reliably produces attacker-chosen output (65–82% ASR on Gemini in the original paper), bringing white-box-style optimization to closed-weight deployments.

8. **Multilingual, encoded, or low-resource-language payloads.** Translation to low-resource or code-mixed languages sharply reduces classifier accuracy — refusal rates can fall from ~79% (English) to ~23% on identical content — and encodings (Base64, ROT13) or emoji substitution evade classifiers not trained on the scheme.

---

### Prevention and Mitigation Strategies

Prompt injection vulnerabilities are intrinsic to current generative AI: LLMs make no architectural distinction between instructions and data, and their behavior is stochastic, so no robust prevention mechanism exists today — a position consistent with NIST AI 100-2 E2025 (2025), NCSC (2025), and Debenedetti et al. (CaMeL, 2025). Defense is therefore architectural rather than interceptive. Design the surrounding system on the explicit assumption that the model's instruction boundary will eventually be bypassed, and constrain what the model is permitted to do — and what its outputs are permitted to reach — so a successful injection does not translate into a successful exploit.

Most high-impact prompt-injection incidents on record (EchoLeak / CVE-2025-32711; the Amazon Q runtime and supply-chain pair; the Supabase MCP `service_role` exfiltration; GitHub Copilot / CVE-2025-53773) became severe not because the injection itself succeeded but because the injection landed inside a system whose tools, scopes, or output-rendering capabilities let the compromised model act on the attacker's behalf at the user's privilege level. This is the operational relationship between this entry and **LLM06:2025 Excessive Agency**: prompt injection is the input-side compromise, and excessive functionality, permissions, or autonomy are what give that compromise consequences outside the chat window. Simon Willison's "lethal trifecta" (Jun 2025) restates the same structural diagnosis as a pre-deployment check: an agent that can simultaneously (1) access private data, (2) ingest untrusted content, and (3) communicate externally has the conditions for high-impact exploitation, and removing any one leg removes them. Treat LLM01 and LLM06 as a pair when threat-modeling agentic deployments.

Apply the controls below as defense-in-depth — no single control is sufficient. Some reduce injection success (and are expected to degrade against adaptive attackers); others bound the blast radius once injection succeeds (these are what survive against attackers who can probe the system). For agentic deployments, the least-privilege and capability-budgeting controls (#4, #8) are load-bearing — see **LLM06:2025** for the full agency-side treatment.

1. **Constrain the model's role and capabilities in the system prompt.** Use declarative allow/deny statements ("assist with X only; do not access Y; do not forward output to external addresses"), not open-ended grants. A partial control only — an attacker who infers the prompt can bypass it (Nasr/Carlini, 2025); pair with the privilege controls in #4.

2. **Define a strict output schema and validate every response in trusted application code** before any downstream system acts on it — structural validation, not a second LLM call. This catches format violations, not semantic manipulation: a schema-valid response can still carry a malicious SQL query or an exfiltration-formatted email body.

3. **Filter at every modality boundary — text, image, audio, structured data — not just text.** Run modality-specific classifiers, OCR over images, and transcription over audio, then apply text filters to the extracted content. Semantic filters are evadable by rephrasing or encoding, and accuracy drops for low-resource languages (refusal ~79% English → ~23%; arXiv:2504.11168, 2025).

4. **Hold credentials and state-change capability in application code, not the model, and grant least privilege per operation.** Route privileged calls through a deterministic policy engine that re-validates intent and arguments at execution time. NIST AI 100-2 E2025 and the CISA + Five Eyes OT joint guidance (Dec 2025) frame this deterministic mediation as a baseline procurement expectation. Broad "convenience" permissions and multi-agent hops re-introduce the risk downstream.

5. **Strip Tag-block (U+E0000–E007F), variation-selector (U+FE00–FE0F), and zero-width (U+200B/C/D, U+2060) characters at every ingest and render boundary.** These are invisible in normal rendering and smuggle instructions or exfiltration bytes; the Aug 2024 M365 Copilot PoC (Embrace The Red) exfiltrated an MFA code this way, and variation-selector variants (2025) cut cost to ~2 characters per byte. Does not stop visible-text payloads or future stego classes.

6. **Pass external content through a structurally separate, provenance-labeled channel** so the model can distinguish data from instructions (StruQ, USENIX Security 2025; "spotlighting," Microsoft Research 2025). This reduces ASR in non-adaptive tests only — an attacker who knows the marking scheme can mimic it, and StruQ was bypassed under adaptive attack (Nasr/Carlini, 2025).

7. **Require explicit human confirmation before any privileged, irreversible, or externally visible action**, surfacing the exact rendered action — not a summary — to the reviewer. Invisible-character smuggling can make the displayed action differ from the executed one (#5), and approval fatigue degrades reviewer judgment at volume.

8. **Budget agent capabilities with the Rule of Two as a floor.** Treat simultaneous access to (A) untrusted input, (B) sensitive data, and (C) state change / external comms as high-risk: any [A,B,C] agent needs per-action human approval, and [A,B]/[A,C] configurations need an explicit residual-risk assessment — the Amazon Q incident (AWS-2025-019) wiped a developer's files from an [A,B] config. Endorsed by NIST AI 100-2 E2025 and the CISA/FBI/NSA/ACSC OT guidance (Dec 2025); the rule is silent on autonomy depth (Noma Security, 2025).

9. **Treat agent memory writes as privileged operations** — log the causing prompt, classify writes for instruction or role-modification content, and require approval before instruction-bearing memories persist across sessions. A Feb 2025 Gemini PoC (Embrace The Red) poisoned memory via delayed tool invocation (MITRE ATLAS AML.T0080.001). Factual entries shade into instructions, and incremental writes can evade per-write classification.

10. **Pin, sign, and verify every MCP server and third-party tool package; audit tool descriptions for hidden instructions; monitor tool composition.** Treat these as a software supply-chain surface: the malicious postmark-mcp npm package (Koi Security, Sept 2025; corroborated by BleepingComputer) BCC'd email to an attacker for ~8 days across ~300 organizations. Pinning does not stop a payload shipped in the pinned version or tool-description poisoning that leaves the version unchanged.

11. **Test against adaptive attackers who have read your defense; reject static-only ASR claims.** Baseline with AgentDojo (NeurIPS 2024) and JailbreakBench (NeurIPS 2024), then red-team with the full defense specification disclosed to the testers. Nasr, Carlini et al. (Oct 2025) found static ASR near zero while adaptive ASR exceeded 90% for most of 12 recent defenses (see also LLMail-Inject, Microsoft MSRC / SaTML 2025).

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

**Scenario #6: Multimodal Steganographic Injection.** An attacker embeds an instruction in an image below the human visual threshold; a multimodal model's vision encoder extracts the payload and behavior changes, producing harmful output or unauthorized tool invocation. Demonstrated against four frontier vision-language models in oncology imaging (Clusmann et al., *Nature Communications*, 2024) and against general-purpose models via combined visual perturbation and text steering (JPS, ACM MM 2025).
**Anatomy:** (a) image input (indirect / multimodal) · (b) single-shot · (c) steganographic / pixel-level encoding

**Scenario #7: Zero-Click Document-Borne Agentic Exfiltration.** A crafted email triggers an LLM-powered productivity assistant to exfiltrate organizational data with no user interaction. Aim Security demonstrated this against Microsoft 365 Copilot (CVE-2025-32711, "EchoLeak", patched June 2025), bypassing both the deployed prompt-injection classifier and the link-redaction filter.
**Anatomy:** (a) email / document (indirect) · (b) single-shot with tool invocation · (c) plain text with invisible-Unicode exfiltration channel

**Scenario #8: Agentic Destructive Command Execution.** Two July 2025 events show the same impact via different vectors: an attacker committed a destructive system prompt to the Amazon Q VS Code extension repository, reaching ~1 million installs before reversion (AWS-2025-015); separately, a runtime injection caused Amazon Q to execute arbitrary code (AWS-2025-019). An agent with shell, file-system, or cloud-API access amplifies an injection into a host-impacting incident.
**Anatomy:** (a) supply-chain / compromised system prompt (AWS-2025-015) or runtime indirect injection (AWS-2025-019) · (b) persistent cross-session (supply-chain) / single-shot with shell tool execution (runtime) · (c) plain text

**Scenario #9: Trusted-Backend Indirect Injection through MCP.** An attacker plants text in a low-privilege channel — a public GitHub issue, a support ticket, or a malicious npm package — and the developer's LLM reads it under elevated credentials. Invariant Labs (May 2025) exfiltrated private repositories via a poisoned GitHub issue; General Analysis (July 2025) dumped a production database through Cursor's Supabase MCP server (running `service_role`, bypassing row-level security); the malicious `postmark-mcp` package (Sept 2025) BCC'd email to an attacker for ~8 days.
**Anatomy:** (a) trusted-surface indirect (MCP channel — issue, ticket, npm package) · (b) multi-step tool-chain · (c) plain text

### Reference Links

1. [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173): Greshake et al., **arXiv** 2023
2. [Inject My PDF: Prompt Injection for your Resume](https://kai-greshake.de/posts/inject-my-pdf): **Kai Greshake**, 2023
3. [Universal and Transferable Adversarial Attacks on Aligned Language Models](https://arxiv.org/abs/2307.15043): Zou et al., **arXiv** 2023
4. [Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations (NIST AI 100-2 E2025)](https://csrc.nist.gov/pubs/ai/100/2/e2025/final): **NIST**, March 2025
5. [Prompt injection is not SQL injection](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection): **UK NCSC**, December 2025
6. [Principles for the Secure Integration of AI in Operational Technology](https://www.cisa.gov/sites/default/files/2025-12/joint-guidance-principles-for-the-secure-integration-of-artificial-intelligence-in-operational-technology-508c.pdf): **CISA + FBI + NSA + ACSC + allied partners**, December 2025
7. [The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections](https://arxiv.org/abs/2510.09023): Nasr, Carlini et al., **arXiv** 2510.09023, October 2025
8. [Prompt injection attacks on vision language models in oncology](https://www.nature.com/articles/s41467-024-55631-x): Clusmann et al., ***Nature Communications***, 2024
9. [JPS: Jailbreak Multimodal LLMs with Collaborative Visual Perturbation and Textual Steering](https://dl.acm.org/doi/10.1145/3746027.3754561): Wang et al., **ACM MM 2025**
10. [Bypassing Prompt Injection Guardrails via Code-Switching and Unicode Transcoding](https://arxiv.org/html/2504.11168v2): **arXiv**:2504.11168, 2025
11. [PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation](https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf): Zou et al., **USENIX Security 2025**
12. [StruQ: Defending Against Prompt Injection with Structured Queries](https://www.usenix.org/system/files/usenixsecurity25-chen-sizhe.pdf): Chen et al., **USENIX Security 2025**
13. [Fun-tuning: Characterizing the Vulnerability of Proprietary LLMs to Optimization-based Prompt Injection Attacks via the Fine-Tuning Interface](https://arxiv.org/abs/2501.09798): Labunets et al., **arXiv** 2501.09798, January 2025
14. [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352): Debenedetti et al., **NeurIPS 2024**
15. [JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models](https://arxiv.org/abs/2404.01318): Chao et al., **NeurIPS 2024**
16. [M365 Copilot Prompt Injection, Tool Invocation and Data Exfil using ASCII Smuggling](https://embracethered.com/blog/posts/2024/m365-copilot-prompt-injection-tool-invocation-and-data-exfil-using-ascii-smuggling/): Johann Rehberger (**Embrace The Red**), August 2024
17. [Sneaky Bits & ASCII Smuggler updates](https://embracethered.com/blog/posts/2025/sneaky-bits-and-ascii-smuggler/): Johann Rehberger (**Embrace The Red**), 2025
18. [Hacking Gemini's Memory with Prompt Injection and Delayed Tool Invocation](https://embracethered.com/blog/posts/2025/google-gemini-memory-persistence-prompt-injection/): Johann Rehberger, February 2025
19. [GitHub Copilot Remote Code Execution via Prompt Injection (CVE-2025-53773)](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/): Johann Rehberger, 2025
20. [GitHub MCP Server Vulnerability](https://invariantlabs.ai/blog/mcp-github-vulnerability): **Invariant Labs**, May 2025
21. [Supabase MCP can leak your entire SQL database](https://generalanalysis.com/blog/supabase-mcp-blog): **General Analysis**, July 2025
22. [Postmark-MCP npm Malicious Backdoor — Email Theft](https://www.koi.ai/blog/postmark-mcp-npm-malicious-backdoor-email-theft): **Koi Security**, September 2025
23. [Unofficial Postmark MCP npm package silently stole users' emails](https://www.bleepingcomputer.com/news/security/unofficial-postmark-mcp-npm-silently-stole-users-emails/): **BleepingComputer**, September 2025
24. [Defending Against Indirect Prompt Injection Attacks With Spotlighting](https://www.microsoft.com/en-us/research/publication/defending-against-indirect-prompt-injection-attacks-with-spotlighting/): **Microsoft Research**, 2025
25. [Announcing the Winners of the Adaptive Prompt Injection Challenge — LLMail-Inject](https://www.microsoft.com/en-us/msrc/blog/2025/03/announcing-the-winners-of-the-adaptive-prompt-injection-challenge-llmail-inject/): **Microsoft MSRC**, March 2025
26. [Practical AI Agent Security: Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/): **Meta AI**, October 2025
27. [Why the Rule of Two Can't Protect Your Agents](https://noma.security/blog/mcp-servers-agentic-risk-and-the-framework-that-protects-it/): **Noma Security**, 2025
28. [AWS-2025-015 (Amazon Q VS Code extension supply-chain incident)](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/): **AWS Security Bulletin**, July 2025
29. [AWS-2025-019 (Amazon Q runtime injection)](https://aws.amazon.com/security/security-bulletins/AWS-2025-019/): **AWS Security Bulletin**, July 2025
30. [EchoLeak (CVE-2025-32711) — Microsoft 365 Copilot zero-click prompt injection](https://arxiv.org/abs/2509.10540): Reddy and Gujral, **Aim Security, AAAI Fall Symposium 2025**; paired with [NVD entry](https://nvd.nist.gov/vuln/detail/CVE-2025-32711)
31. [CVE-2024-5184 (EmailGPT) advisory](https://www.incibe.es/en/incibe-cert/early-warning/vulnerabilities/cve-2024-5184): **INCIBE-CERT**, 2024
32. [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813): Debenedetti et al., **arXiv** 2503.18813, 2025
33. [The lethal trifecta for AI agents: private data, untrusted content, and external communication](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/): **Simon Willison**, June 2025
34. [OWASP Top 10 for LLM Applications — LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/): **OWASP GenAI Security Project**, 2025

---
### Related Frameworks and Taxonomies

**OWASP Top 10 for Agentic Applications (ASI)**

| ID | Relevance |
|---|---|
| ASI01 — Agent Goal Hijack | Injected input overrides the system-prompt role/capability constraints, redirecting agent goals. |
| ASI02 — Tool Misuse & Exploitation | Injected input drives unauthorized tool invocation (the "lethal trifecta" conditions). |
| ASI03 — Identity & Privilege Abuse | Agent acts under the user's elevated credentials, performing actions the attacker could not. |
| ASI05 — Unexpected Code Execution (RCE) | Shell / file-system / cloud-API access turns injection into arbitrary command execution. |
| ASI06 — Memory & Context Poisoning | Memory and RAG poisoning taint every future session reading the store. |
| ASI08 — Cascading Failures | Tool outputs re-enter the context window, enabling chained or self-replicating effects. |
| ASI09 — Human-Agent Trust Exploitation | Injection bypasses human-in-the-loop confirmation. |

**MITRE ATLAS**

| ID | Relevance |
|---|---|
| AML.T0051.000 — LLM Prompt Injection: Direct | Direct-injection technique (Direct Prompt Injection; Scenario #1). |
| AML.T0051.001 — LLM Prompt Injection: Indirect | Indirect-injection technique (Scenarios #2, #4, #7, #9). |
| AML.T0054 — LLM Jailbreak Injection: Direct | Jailbreak subset of direct injection. |
| AML.T0057 — LLM Data Leakage | Disclosure outcome of a successful injection. |
| AML.T0065 — LLM Prompt Crafting | Adversarial payload construction, incl. the "fun-tuning" gradient-oracle technique. |
| AML.T0068 — LLM Prompt Obfuscation | Invisible-Unicode and multilingual/encoded payloads. |
| AML.T0070 — RAG Poisoning | RAG corpus poisoning (Scenario #4). |
| AML.T0080.001 — AI Agent Context Poisoning: Memory | Cross-session memory poisoning (Control #9). |
| AML.T0099 — AI Agent Tool Data Poisoning | Poisoned content retrieved by an MCP-connected tool, acted on under elevated credentials. |
| AML.T0086 — Exfiltration via AI Agent Tool Invocation | Tool-call-mediated exfiltration (Scenario #9). |
| AML.T0102 — Generate Malicious Commands | Attacker-directed generation of destructive commands (Scenario #8). |
| AML.T0105 — Escape to Host | Host-level execution via agent shell / cloud-API access. |
| AML.T0110 — AI Agent Tool Poisoning | Poisoned MCP server descriptions or tool definitions (Control #10). |

**Other frameworks**

| Framework / ID | Relevance |
|---|---|
| MITRE ATT&CK T1195 — Supply Chain Compromise | Compromised MCP server / npm package as a delivery surface (Control #10; Scenarios #8–#9). |
| NIST AI 100-2 E2025 | Baseline position that no robust prevention exists because LLMs do not separate instructions from data. |
| OWASP AIVSS | AI Vulnerability Scoring System — severity scoring applicable to prompt-injection findings. |
| OWASP GenAI Data Security 2026 — DSGAI01 (Sensitive Data Leakage) | Names indirect-PI exfiltration (markdown-image, tool-callback allowlisting) as a control category; both entries cite CVE-2024-5184. |
| OWASP GenAI Data Security 2026 — DSGAI06 (Tool, Plugin & Agent Data Exchange) | "Tool poisoning via crafted metadata" is the same mechanism as Control #10; both entries cite the postmark-mcp incident. |
