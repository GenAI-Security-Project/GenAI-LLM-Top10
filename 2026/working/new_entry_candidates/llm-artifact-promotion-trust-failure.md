for additional guidance, refer to [the style guide](../documentation/style/README.md) and to the [glossary](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/wiki/Definitions)

## LLM artifact promotion trust failure

### Description

LLM applications increasingly depend on third-party model artifacts, adapters, datasets, and conversion outputs that are promoted through automated release pipelines. When those promotion steps are not trustworthy, attackers can introduce tampered or impersonated artifacts into development or production, leading to compromised model behavior, data exposure, unsafe outputs, or unauthorized access to downstream systems.

This risk is distinct from training-data poisoning because it focuses on the integrity of the promotion path and the trust decisions made when moving AI artifacts from untrusted or semi-trusted sources into a trusted deployment environment. The most common failure points include repository impersonation, unsigned artifacts, weak release gating, and conversion or merge workflows that do not verify provenance before publication.

### Common Examples of Risk

1. Example 1: A malicious actor publishes a lookalike model or adapter under a trusted-sounding name, and the artifact is accepted into a deployment workflow without strong verification.
2. Example 2: A model merge or format conversion pipeline produces a new artifact that appears valid but has been altered during processing to weaken safety controls or embed malicious behavior.
3. Example 3: A third-party adapter, plugin, or fine-tuned model is promoted into production based only on repository metadata or informal review, without signature, hash, or provenance checks.

### Prevention and Mitigation Strategies

1. Trust only verified sources for model artifacts, adapters, datasets, and tools, and restrict promotion to approved suppliers with strong account protection and clear ownership.
2. Require integrity validation before promotion into trusted environments, including hashes, signatures, attestations, and provenance records for AI artifacts.
3. Monitor high-risk workflows closely, including model hubs, merge services, conversion pipelines, release automation, and agent-tool publication paths. Use approval gates, logging, and human review for promotion points.

### Example Attack Scenarios

Scenario #1: An attacker compromises a supplier account or creates a lookalike repository and publishes a fake model under a familiar name. A downstream team downloads and deploys the artifact, which later produces unsafe outputs or exposes sensitive prompts.

Scenario #2: A malicious adapter is inserted into a model update workflow through a third-party collaborator or supplier. The adapter behaves normally in standard tests but triggers harmful or covert behavior when specific prompts or domains are used.

### Reference Links

1. [LLM03:2025 Supply Chain - OWASP Gen AI Security Project](https://genai.owasp.org/llmrisk/llm03-training-data-poisoning/): **OWASP Gen AI Security Project**
2. [Software Supply Chain Security - OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html): **OWASP Cheat Sheet Series**
3. [ML Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010): **MITRE ATLAS**
4. [OWASP GenAI Exploit Round-up Report Q1 2026](https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/): **OWASP GenAI Security Project**
5. [Attesting LLM Pipelines: Enforcing Verifiable Training and Release ...](https://arxiv.org/abs/2603.28988): **arXiv**
6. [Measuring Malicious Intermediary Attacks on the LLM Supply Chain](https://arxiv.org/html/2604.08407v1): **arXiv**
7. [Abusing supply chains: How poisoned models, data, and third-party artifacts spread risk](https://www.datadoghq.com/blog/detect-abuse-ai-supply-chains/): **Datadog**
8. [Malicious AI Models: Security Risks Across the AI Supply Chain](https://www.wiz.io/academy/ai-security/malicious-ai-models): **Wiz**
9. [Provenance and Traceability in AI: Ensuring Accountability and Trust](https://techstrong.ai/articles/provenance-and-traceability-in-ai-ensuring-accountability-and-trust/): **TechStrong**
11. [Exploiting Trust in Open-Source AI: The Hidden Supply Chain Risk ...](https://www.trendmicro.com/vinfo/us/security/news/cybercrime-and-digital-threats/exploiting-trust-in-open-source-ai-the-hidden-s...) : **Trend Micro**
12. Case Studies in Software Supply Chain Security. In: Supply Chain Software Security. Apress, Berkeley, CA. https://doi.org/10.1007/979-8-8688-0799-2_8