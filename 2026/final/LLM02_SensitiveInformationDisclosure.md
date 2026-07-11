## LLM02:2026 Sensitive Information Disclosure

### Description

Sensitive information disclosure occurs when an LLM-integrated system exposes confidential, regulated, privileged, or proprietary data through a channel the data subject, controller, or system owner did not authorize. The channel is not only the final answer: tool-call arguments, reasoning traces, retrieved chunks, multimodal output, logs, telemetry, embeddings, and observable inference properties (timing, token length, log-probabilities, confidence, cache-hit behavior) are all disclosure surfaces. Treat each as an output subject to the same classification and redaction rules.

Disclosure arises across four phases of the LLM lifecycle:

1. **Training-time.** A model, fine-tune, or LoRA adapter memorizes corpus content and later reproduces it verbatim or reconstructably. Memorization scales log-linearly with capacity, duplication, and context length; narrow adapters memorize rare examples with high fidelity, a targeted extraction surface distinct from the base model.
2. **Inference-time.** The model discloses live context — system prompt, RAG chunks, files, tool outputs, memory, or another session's data — often because summarization, translation, or extraction surfaces more than was asked, including visually-redacted spans.
3. **Pipeline-time.** Fine-tuning, distillation, synthetic-data generation, gradients, SDKs, and observability move sensitive data into derived artifacts.
4. **Observation-time.** Adversaries infer facts from externally measurable properties — token length under TLS, latency, log-probabilities, confidence, cache-hit signals — without receiving content.

Protected information includes PII, PHI, financial data, credentials, API keys, trade secrets, model weights, privileged communications, classified or export-controlled material, and biometric and genomic identifiers. Two structural failures drive most incidents. First, **oversharing upstream**: unscoped drives, legacy permissions, and knowledge bases feed RAG with sensitive data the model then retrieves as designed — the fix is the data surface, not the model (DSGAI01). Second, **persistence**: once data influences weights, embeddings, or adapters it stays extractable after source deletion, straining GDPR Article 17 and CCPA §1798.105 erasure obligations. **Open-weights** deployments cannot rely on rate limits, since extraction, membership inference, and inversion run offline at unbounded rates.

Severity should turn on what the recipient can learn, not on whether the leak looked like natural language. Applicable regimes include the EU AI Act (Regulation (EU) 2024/1689, high-risk obligations from August 2026), GDPR, HIPAA, CCPA/CPRA, ISO/IEC 42001, and NIST AI 600-1. This entry covers the LLM as an application *component*; where it acts as an autonomous actor (cross-session memory, tool choice, multi-step exfiltration), amplified risk is owned by ASI, with deeper controls in DSGAI.

### Common Examples of Risk

The seven sub-classes map to the four phases: training-time → §1, §6; inference-time → §2 with §3 and §4; pipeline-time → §6, §7; observation-time → §5.

**1. Training-data memorization and extraction.** The November 2023 "poem" divergence attack drove `gpt-3.5-turbo` to emit more than 10,000 unique memorized examples for roughly USD 200; vendor patches have been bypassed repeatedly. LoRA adapters are a separate, high-fidelity extraction surface (StolenLoRA, USENIX Security 2025), and fine-tuned models are markedly more extractable than base models of the same scale. Litigation exhibits (NYT v. OpenAI, Getty v. Stability AI, Kadrey v. Meta) supply direct evidence of verbatim reproduction of copyrighted and watermarked material.

**2. Inference-time context and output disclosure.** The March 2023 ChatGPT Redis bug exposed payment PII for 1.2% of Plus subscribers; more than 4,500 shared conversations were indexed by Google in 2025 through missing `noindex` directives. A 2026 cross-sector audit of enterprise RAG deployments found **73% of audited pipelines failing at least one critical security control**, and clinical-embedding vector stores sit in HIPAA audit-control scope most teams have not operationalized — evidence that retrieval-layer authorization is widely under-implemented. Treat reasoning traces and tool arguments as outputs, not debugging leftovers; the trace channel also enables reasoning-trace-coercion model extraction. Regex and blocklist filters fall to cross-lingual, base64, and hex encodings. Aggregation across individually-permitted sources (budget + hiring + diligence → a pending M&A target) is a disclosure when policy prohibits the synthesized conclusion.

**3. Embedding and representation disclosure.** Modern inversion reconstructs plaintext from leaked or exported vectors, so an "embeddings-only" backup is a source-document breach. Cosine similarity does not respect ACLs; authorize before retrieval, because post-generation filtering cannot undo a chunk already supplied to the model. Mechanisms are owned by LLM09:2026 and DSGAI13; this entry owns the regulatory consequence.

**4. Multimodal disclosure.** Vision models OCR credentials and PII from screenshots, notifications, and PDF metadata; generators reproduce watermarks and identifiable faces (the Getty / Stable Diffusion watermark case is canonical). Cross-modal transformation — text rendered as image, image OCR'd to text — bypasses single-modality DLP.

**5. Inference-time side channels.** SPV-MIA raised membership-inference AUC to 0.9 against fine-tuned targets — enough for a regulatory breach determination about a named individual. Whisper Leak (Microsoft, 2025) classified conversation topics at greater than 98% AUPRC across 28 production models from encrypted traffic; Weiss et al. (2024) reconstructed 29% of response content and inferred topic for 55% via token length. NDSS 2025 demonstrated prompt leakage through KV-cache sharing in multi-tenant serving; Dong et al. (USENIX Security 2025) inverted a 4,112-token medical prompt from a middle layer at F1 86.88; and Carlini et al. (2024) recovered a production model's projection layer through a logit-bias channel.

**6. Training-pipeline disclosure.** Gradient inversion with malicious aggregation (Boenisch et al., 2023), distillation, and synthetic-data carryover move examples into derived models. A 2026 attack class, **Differential Privacy Reversal via LLM Feedback**, iterates LLM-refined queries against a DP-protected model, homing in on confidence spikes until individuals are re-identified — so fixed-epsilon DP is necessary but not sufficient without rate-limiting, query-pattern detection, and per-user budgets.

**7. Platform and ecosystem disclosure.** Observability platforms (Langfuse, LangSmith, Datadog LLM Observability) log full prompts, completions, chunks, and traces by default. Marquee 2025–2026 incidents: DeepSeek's January 2025 ClickHouse exposure of more than one million rows of logs and API keys; Anthropic's March–April 2026 Claude Code source-map leak of roughly 1,900 files / 512,000 lines, with a critical Claude Code vulnerability disclosed days later; a Claude browser-extension zero-click XSS ("ShadowPrompt") and CVE-2026-0628 in Chrome's Gemini Live integration; and Check Point's February 2026 disclosure of ChatGPT exfiltration through a hidden outbound channel in the code-execution runtime, where one crafted prompt turned the runtime into a silent DNS/image channel while the visible answer stayed benign.

### Prevention and Mitigation Strategies

Mitigations follow the DSGAI tiered structure for a graduated implementation path.

**Tier 1 — Foundational (every deployment).**
- Govern corpora: provenance, classification, and deduplication across near-duplicates, transliterations, and format variants; scrub PII at ingest. Deduplication reduces but does not eliminate memorization.
- Minimize context: send only task-required fields to external providers; disable auto-context (`customer_360`, full-record append) unless justified per template.
- Authorize before retrieval: enforce document- and chunk-level authorization inside the index query, not at the application layer after retrieval; isolate per-tenant indexes for high-sensitivity workloads.
- System-prompt hygiene: never store secrets, credentials, or regulated data in system prompts.
- Sanitize with classifiers, not regex alone: pattern matching plus NER plus trained classifiers, because regex fails on encoded and cross-lingual output.
- Budget queries per user and per session on sensitive endpoints to disrupt enumeration and membership probing.
- Operational hygiene: restrict and scrub logs and traces before APM ingestion; encrypt in transit and at rest; technically enforce no-train/no-retain, not policy text alone.

**Tier 2 — Hardening (regulated / high-sensitivity).**
- DP-SGD calibrated to sensitivity and cardinality with overfitting monitored as a memorization proxy; pair with detection, because fixed budgets degrade under adaptive querying.
- Vector-store protection: encryption, ACLs separate from document ACLs, restricted export APIs, minimum-scope k-NN, and embedding-space probing detection.
- Gate log-probabilities, confidence, and explanations on production endpoints.
- Classify and redact reasoning traces as first-class output; never log raw traces to unrestricted observability.
- Side-channel defenses: random padding and token batching for streaming; segregate high-sensitivity tenants on dedicated prefix caches; partition KV caches under co-tenancy.
- Format-preserving encryption for structured identifiers; strict internal-vs-external routing separation with field allowlists on the external path.
- AI-aware audit logging into SIEM; continuous DLP and AI-SPM; a documented domain inventory and enforced join policy so individually-permitted sources cannot combine into prohibited conclusions.

**Tier 3 — Advanced (regulated, classified, high-target).**
- Confidential computing (Intel TDX, AMD SEV-SNP, AWS Nitro Enclaves) or emerging privacy-preserving inference (the AloePri 2026 covariant-obfuscation framework) where the threat model justifies the utility and latency cost.
- Verifiable erasure across raw data, embeddings, checkpoints, and adapters, validated by post-unlearning extraction and membership-inference probes.
- Disclosure red-teaming as a release gate: extraction, membership inference, embedding inversion, internal-state inversion, side channels, and LoRA extractability, measured quantitatively and aligned to MITRE ATLAS.
- Audit synthetic data against extractors; resist distillation with probing detection, rate limits, and watermarking; budget aggregate analytics.
- Exercise a disclosure incident-response playbook: data-class and affected-subject/session scoping; GDPR 72-hour, HIPAA 60-day, and EU AI Act Article 73 *without-undue-delay* notification; unlearning, retraining, or withdrawal; vector and cache cleanup; vendor notice; persistent-memory audit.

### Example Attack Scenarios

1. Divergence prompts make a production model emit memorized PII, URLs, and live credentials at scale, triggering GDPR Article 33 notification.
2. A shared-inference-state defect leaks one user's medical-letter prompt into another user's reasoning trace; HIPAA 60-day notification applies.
3. Extended-thinking traces logged verbatim to a shared APM project expose retrieved PII to hundreds of engineers while the answer stays sanitized.
4. Prompt injection makes a support bot print its system prompt and an embedded vendor API key.
5. A shared legal RAG index crosses firm boundaries, synthesizing one client's privileged strategy into another's answer — an attorney-client waiver event.
6. A leaked "embeddings-only" vector backup is reclassified as a source-document breach after inversion, restarting the 72-hour clock.
7. Whisper Leak topic inference on encrypted streaming identifies users querying medical, legal, or political topics without decryption.
8. Membership inference against a clinical fine-tune identifies 312 of 500 patients at AUC 0.89 for about USD 150 — HIPAA-reportable with no record extracted.
9. A model summarizes PII hidden beneath a black-rectangle PDF redaction layer rendered over unmodified text.
10. A published LoRA adapter yields verbatim customer-support transcripts through offline StolenLoRA-style extraction.
11. An injected "diagnostic check" makes a code runtime encode spreadsheet content into DNS queries while the visible statistical summary stays benign.

### Reference Links

1. [OWASP GenAI Data Security 2026 (v1.0)](https://genai.owasp.org/): OWASP GenAI Security Project, Mar 2026
2. [Scalable Extraction of Training Data from Production LMs](https://arxiv.org/abs/2311.17035): Nasr, Carlini et al., 2023
3. [Teach LLMs to Phish](https://arxiv.org/abs/2403.00871): Panda et al., IEEE S&P 2024
4. [SPV-MIA: Membership Inference with Self-Prompt Calibration](https://neurips.cc/virtual/2024/poster/95327): Fu et al., NeurIPS 2024
5. [Depth Gives a False Sense of Privacy: LLM Internal-State Inversion](https://arxiv.org/abs/2507.16372): Dong et al., USENIX Security 2025
6. [Whisper Leak: Side-Channel Attack on Remote LMs](https://arxiv.org/abs/2511.03675): McDonald et al., 2025
7. [What Was Your Prompt? Remote Keylogging on AI Assistants](https://arxiv.org/abs/2403.09751): Weiss et al., USENIX Security 2024
8. [Prompt Leakage via KV-Cache Sharing in Multi-Tenant Serving](https://www.ndss-symposium.org/ndss-paper/i-know-what-you-asked-prompt-leakage-via-kv-cache-sharing-in-multi-tenant-llm-serving/): NDSS 2025
9. [Stealing Part of a Production Language Model](https://arxiv.org/abs/2403.06634): Carlini et al., 2024
10. [When the Curious Abandon Honesty: Federated Learning Is Not Private](https://arxiv.org/abs/2112.02918): Boenisch et al., IEEE EuroS&P 2023
11. [RAG-Thief: Scalable Extraction of Private Data from RAG](https://arxiv.org/abs/2411.14110): 2024
12. [Wiz Research Uncovers Exposed DeepSeek Database](https://www.wiz.io/blog/wiz-research-uncovers-exposed-deepseek-database-leak): Wiz, Jan 2025
13. [ChatGPT Data Leakage via Hidden Outbound Runtime Channel](https://research.checkpoint.com/2026/chatgpt-data-leakage-via-a-hidden-outbound-channel-in-the-code-execution-runtime): Check Point, Feb 2026
14. [Claude Extension Flaw Enabled Zero-Click XSS Prompt Injection](https://thehackernews.com/2026/03/claude-extension-flaw-enabled-zero.html): The Hacker News, Mar 2026
15. [Gemini Live in Chrome Hijacking (CVE-2026-0628)](https://unit42.paloaltonetworks.com/gemini-live-in-chrome-hijacking): Palo Alto Unit 42, Mar 2026
16. [Anthropic Claude Code Source Leak](https://www.theguardian.com/technology/2026/apr/01/anthropic-claudes-code-leaks-ai): The Guardian, Apr 2026
17. [73% of Enterprise RAG Fails Audit](https://ragaboutit.com/73-of-enterprise-rag-fails-audit-nists-4-step-fix/): RAG About It, Jun 2026
18. [Vector Database Security: RAG Compliance & Monitoring](https://beyondscale.tech/blog/vector-database-security-rag-compliance-monitoring): BeyondScale, May 2026
19. [Differential Privacy Reversal via LLM Feedback](https://instatunnel.my/blog/differential-privacy-reversal-via-llm-feedback-the-silent-killer-of-data-anonymization): InstaTunnel, Feb 2026
20. [Privacy-Preserving LLM Inference via Covariant Obfuscation (AloePri)](https://arxiv.org/abs/2603.01499): arXiv:2603.01499, Mar 2026
