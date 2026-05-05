## LLM04:2026 Data and Model Poisoning

### Description

Data & Model Poisoning describes a class of attacks and failures where an adversary (or unsafe process) manipulates data or model artifacts to embed harmful behavior, bias, or exploitable weaknesses into an AI system. In modern GenAI environments, poisoning is not limited to "training data" in the traditional sense — it can occur anywhere data is ingested, transformed, retrieved, or reused, including during pre-training, fine-tuning, embedding creation, retrieval augmentation (RAG), and model distribution. The result is an AI system that may still appear functional but behaves in ways that undermine trust, safety, and security.

Data poisoning occurs when pre-training, fine-tuning, or embedding data is tampered with to introduce vulnerabilities, backdoors, or biases. This can happen intentionally (malicious poisoning) or unintentionally (poor data hygiene, contaminated sources). The manipulation compromises model integrity — the model learns the wrong patterns, internalizes malicious correlations, or is conditioned to behave incorrectly under certain conditions. The consequences include harmful outputs, impaired capabilities, and degraded reliability.

The key idea: poisoning targets the model's "learning process," not a single runtime bug. Unlike typical software vulnerabilities that can be patched by fixing code, poisoning can require data revalidation, retraining, model replacement, or pipeline redesign — making it expensive and operationally disruptive.

Poisoning can occur across multiple stages of the LLM lifecycle:

- **Pre-training:** The model learns from broad, large-scale corpora. If a portion of that corpus is maliciously crafted or contaminated, the model may absorb harmful patterns, unsafe instructions, or skewed representations.

- **Fine-tuning:** Models are adapted for specific tasks or domains (e.g., customer support, coding assistants, financial Q&A). If fine-tuning datasets contain manipulated samples, the model can inherit domain-specific failure modes or hidden triggers.

- **Embeddings and vectorization:** Text is converted into vectors for search and retrieval. Poisoning can target embedding generation data (or the stored vectors) to influence what content is retrieved, resulting in "steered" answers or subtle misinformation.

- **Transfer learning / model reuse:** Organizations frequently reuse pre-trained models or community models. If the source model is compromised, downstream systems inherit that compromise.

- **Continuous learning / retraining pipelines:** Some systems update with new data over time. If ingestion is automated and insufficiently validated, attackers can feed poisoned data into the loop and gradually shape model behavior.

Understanding these stages is essential because it clarifies where vulnerabilities originate and how they propagate.

The data poisoning surface expands because organizations increasingly rely on:

- External datasets (public sources, scraped content, third-party corpora)
- RAG and embeddings (vector databases, retrieval pipelines, document ingestion)
- Shared models and open repositories (community weights, fine-tunes, adapters)
- Agentic workflows and automation (AI controlling tasks, actions, and tool use)

Moreover, models distributed through shared repositories or open-source platforms can carry risks through bundled non-weight artifacts — including malicious deserialization (e.g. pickle files) and tampering of bundled non-weight artifacts (chat templates, tokenizer configs, LoRA/PEFT adapters, quantization artifacts) — any of which can execute harmful code or alter model behavior when the model is loaded. Poisoning may also allow for the implementation of a backdoor. Such backdoors may leave the model's behavior untouched until a certain trigger causes it to change, in effect creating the opportunity for a model to become a sleeper agent.

In agentic deployments, poisoning risks extend to tool integrations, persistent memory stores, and RLHF feedback loops — attack surfaces covered in depth in the OWASP Top 10 for Agentic Applications.

---

### Common Examples of Risk

1. **Training & Fine-Tuning Data Poisoning:** Attackers manipulate training or fine-tuning datasets by injecting biased or malicious content. Microsoft Tay demonstrated this when users poisoned its learning data, causing harmful outputs within hours. This shows how untrusted inputs can rapidly degrade model integrity in adaptive or continuously learning AI systems.

2. **Financial Model Data Poisoning:** In financial systems, attackers inject mislabeled or manipulated transaction data to influence fraud detection models. For example, labeling fraudulent transactions as legitimate trains the model to ignore real threats. This targeted poisoning enables fraud bypass, leading to financial losses and undermining trust in AI-driven decision-making systems.

3. **Open-Source Dataset Supply Chain Poisoning:** Attackers poison widely used datasets by contributing seemingly benign but malicious data. A 2024 case showed attackers inserting trigger phrases into datasets, impacting dozens of models and introducing backdoors. This highlights how AI supply chains can be compromised upstream, affecting multiple downstream applications and requiring costly retraining efforts.

4. **Low-Volume High-Impact Backdoor Poisoning:** Research demonstrates that poisoning attacks require a near-constant number of adversarial samples regardless of dataset size — as few as 250 poisoned documents compromise models from 600M to 13B parameters, even when training on 20x more clean data (Souly et al., arXiv:2510.07192, 2025). Large-scale data access is not required — minimal but strategic manipulation is sufficient for significant impact.

5. **AI Recommendation / Memory Poisoning:** Attackers embed hidden instructions in web content to manipulate AI assistants' memory or recommendations. Microsoft observed cases where AI tools were subtly influenced to favor specific vendors. This form of poisoning impacts decision-making without detection, demonstrating risks in agent-based systems and persistent AI memory manipulation.

6. **RAG Knowledge Base Poisoning:** AI systems relying on retrieval (RAG) can be poisoned by inserting manipulated documents into knowledge bases. Research demonstrates that injecting as few as 3-10 semantically optimized adversarial documents into a RAG knowledge base is sufficient to override accurate content across the retrieval pipeline (CorruptRAG, Zhang et al., 2025). Standard defenses including perplexity-based filtering fail against semantically crafted adversarial documents.

7. **Agent / Multi-System Poisoning:** In multi-agent or enterprise AI workflows, poisoned inputs can influence system behavior and data access. Incidents have shown how manipulated inputs led to unintended data exposure and workflow impact. This demonstrates the risk of poisoning not just models, but entire AI-driven ecosystems and decision pipelines.

8. **Healthcare Model Poisoning:** Even small amounts of poisoned medical training data can significantly alter model outputs, leading to unsafe recommendations. Studies show minimal poisoning can increase harmful responses while passing standard evaluations. This highlights the critical risk of poisoning in safety-sensitive domains like healthcare and diagnostics.

9. **Malicious AI Models in Supply Chain:** Attackers distribute compromised models via public repositories, embedding backdoors or malicious behaviors. Organizations downloading these models unknowingly inherit risks, including hidden triggers or system compromise. This reflects a growing AI supply chain threat where trust in third-party models becomes a major vulnerability surface.

10. **Prompt / Content Injection via External Data:** Attackers inject malicious content through user inputs, forums, or APIs to influence AI behavior. Real incidents show chatbots producing unsafe or manipulated outputs and exposing internal instructions. This highlights how external, unverified data sources can act as indirect poisoning vectors in modern AI systems.

---

### Prevention and Mitigation Strategies

1. Track dataset and model lineage using SBOM/ML-BOM (e.g., CycloneDX), enforce signing and verification, and continuously validate data integrity across lifecycle stages to prevent poisoned inputs from entering pipelines.

2. Establish strict validation for all incoming data, rigorously vet third-party vendors, and continuously compare outputs against trusted sources to detect bias, anomalies, or adversarial manipulation early.

3. Protect RAG systems by enforcing trust boundaries, filtering retrieved content, applying source scoring, and isolating system instructions to prevent malicious external data from influencing model outputs.

4. Use sandboxing and strict isolation controls to limit model interaction with unverified data, plugins, or external systems, ensuring untrusted inputs cannot directly influence model behavior or execution context.

5. Apply statistical and AI-based anomaly detection to identify suspicious data patterns, outliers, and trigger-based inputs, helping detect poisoning attempts across training, embedding, and inference pipelines.

6. Use curated, domain-specific datasets for fine-tuning and isolate use cases to reduce exposure to untrusted data, improving model accuracy while minimizing risk of cross-domain contamination or poisoning.

7. Enforce least-privilege access, network segmentation, and strict data access controls to prevent unauthorized data injection and limit model exposure to unintended or sensitive data sources.

8. Use tools like DVC to track dataset changes, maintain version history, and detect unexpected modifications, enabling rollback and forensic analysis when poisoning or anomalous behavior is detected.

9. Control automated retraining and feedback loops by validating incoming data, requiring human oversight, and applying rate limits to prevent gradual poisoning through incremental malicious data injection.

10. Continuously test models using adversarial inputs, trigger-based prompts, and red team scenarios to identify hidden backdoors, poisoning effects, and weaknesses before deployment into production environments.

11. Monitor model outputs, training loss, and behavioral patterns for drift, bias changes, or anomalies, using defined thresholds to detect subtle poisoning effects that evolve over time.

12. Implement grounding techniques with validation layers, ensuring retrieved or external content is verified before influencing outputs, reducing risks from hallucinations and poisoned external context.

13. Treat inference artifacts — including chat templates, tokenizer configurations, LoRA/PEFT adapters, and quantization artifacts — as security-relevant code. Enforce signing, hash verification, diff checks, and static analysis before deployment to prevent hidden instructions or malicious logic from influencing model behavior during runtime.

---

### Example Attack Scenarios

**Scenario #1**

An attacker gains access to an internal knowledge repository (or public ingestion pipeline) and inserts manipulated documents optimized for retrieval. When users query the system, poisoned documents are retrieved and influence responses, leading to incorrect recommendations, manipulated business decisions, or reputational damage.

**Scenario #2**

An attacker embeds hidden instructions in webpages or documents designed to be summarized by AI tools. When ingested into RAG or memory systems, these instructions bias the model to recommend specific products or services, enabling financial manipulation, unfair market advantage, and loss of trust in AI outputs.

**Scenario #3**

An organization enables automated retraining using user feedback. An attacker repeatedly submits crafted inputs into the feedback loop, gradually shifting the model's behavior over time. No access to training infrastructure is required — only the ability to submit feedback through the standard user interface available to any member of the public. The result is slow model drift leading to degraded accuracy, biased outputs, or unsafe recommendations.

**Scenario #4**

A malicious insider or external attacker injects mislabeled transaction data into the training dataset (fraud labeled as legitimate). The model learns incorrect patterns and fails to detect similar fraud attempts, resulting in financial losses, compliance violations, and breach of regulatory obligations.

**Scenario #5**

An attacker uploads a poisoned pre-trained model or fine-tuned weights to a public repository. Organizations download and deploy the model without verification. The model includes hidden malicious behaviors triggered under specific conditions. Research demonstrates that standard safety training techniques fail to remove embedded backdoors and in some cases cause models to better conceal malicious behavior rather than eliminate it (Hubinger et al., arXiv:2401.05566, 2024). This can result in system compromise, data leakage, or targeted manipulation at scale.

**Scenario #6**

An attacker alters a model's inference-time artifact (e.g., chat template/Jinja2 logic in a GGUF package) to embed conditional instructions triggered by specific token patterns. The poisoned template is redistributed via a public model hub, behaving normally under benign inputs. Validated across 18 models, 7 model families, and 4 inference runtimes — under triggered conditions factual accuracy drops from 90% to 15% and attacker-controlled URL emission exceeds 80% success rate. Under benign inputs, model behavior is indistinguishable from the clean version, evading standard behavioral monitoring entirely (Fogel et al., arXiv:2602.04653, 2026). This enables covert, trigger-based output manipulation at runtime without modifying model weights, evading traditional integrity checks and model verification controls.

**Scenario #7**

A developer loads a third-party model using unsafe serialization (e.g., pickle). The model artifact contains embedded malicious code that executes during loading, enabling host compromise, lateral movement, and infrastructure breach.

**Scenario #8**

In a shared AI environment, one tenant injects adversarial data into shared embeddings or memory layers. This influences responses generated for other tenants, causing cross-tenant data contamination, integrity violations, and privacy risk.

**Scenario #9**

An attacker interacts with an AI agent and injects malicious instructions into its persistent memory. Over time, the agent begins prioritizing attacker-controlled logic in future decisions, resulting in long-term manipulation of automated workflows, business logic compromise, and hidden persistence.

---

### Reference Links

1. [CycloneDX — Machine Learning Bill of Materials (AI/ML-BOM)](https://cyclonedx.org/capabilities/mlbom/)
2. [OWASP Developer Guide — CycloneDX](https://owasp.org/www-project-developer-guide/)
3. [CycloneDX (official site)](https://cyclonedx.org)
4. [OWASP Foundation — CycloneDX project page](https://owasp.org/www-project-cyclonedx/)
5. [ECMA-424 — CycloneDX Bill of Materials specification](https://www.ecma-international.org/publications-and-standards/standards/ecma-424/)
6. [DVC — Documentation](https://dvc.org/doc)
7. [DVC — Get Started](https://dvc.org/doc/start)
8. [DVC — User Guide](https://dvc.org/doc/user-guide)
9. [redteams.ai — RAG Retrieval Poisoning](https://redteams.ai)
10. [GitHub — AI Red Team Framework: RAG Poisoning Playbook](https://github.com)
11. [MITRE ATLAS (official site)](https://atlas.mitre.org)
12. [MITRE ATLAS case study — Split-View poisoning](https://atlas.mitre.org/studies)
13. [NIST CSRC — MITRE ATLAS Overview (PDF)](https://csrc.nist.gov)
14. [PyTorch — SafeTensors project page](https://pytorch.org)
15. [JFrog Security Research — GGUF-SSTI (Jinja2 template injection)](https://jfrog.com/blog/)
16. [PromptFoo LLM Security DB — Chat Template Hidden Instructions](https://promptfoo.dev)
17. [GitHub Security Advisory — Giskard agents Jinja2 SSTI (GHSA-frv4-x25r-588m)](https://github.com/advisories/GHSA-frv4-x25r-588m)
18. [GitLab Advisory — CVE-2026-34172 (Giskard agents SSTI)](https://gitlab.com)
19. [F5 Operations Guide — Data and model poisoning](https://f5.com)
20. [Inference-Time Backdoors via Hidden Instructions in LLM Chat Templates — Fogel et al., arXiv:2602.04653](https://arxiv.org/abs/2602.04653)

---

### Related Frameworks and Taxonomies

- **MITRE ATLAS™** — ATT&CK-style matrix of AI/ML tactics and techniques, including poisoning-related techniques and case studies. [MITRE ATLAS](https://atlas.mitre.org)

- **MITRE ATLAS case study: Web-scale Split-View poisoning** — demonstrates dataset poisoning risks in URL-based datasets. [ATLAS split-view poisoning case study](https://atlas.mitre.org/studies)

- **NIST CSRC overview referencing ATLAS** — useful for governance and security audiences linking ATLAS to assurance concepts. [NIST CSRC ATLAS overview](https://csrc.nist.gov)

- **NIST AI Risk Management Framework (AI RMF 1.0)** — lifecycle risk management functions (Govern/Map/Measure/Manage) that can be mapped to poisoning controls. [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

- **NIST AI RMF publication (NIST.AI.100-1 PDF)** — authoritative document for formal citations. [NIST AI RMF PDF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)

- **CSA AI Controls Matrix (AICM)** — vendor-agnostic control objectives framework for cloud AI systems, including mappings to ISO 42001 and NIST AI RMF. [CSA AICM](https://cloudsecurityalliance.org)

- **ISO/IEC 42001 (AI Management System / AIMS)** — certifiable management system standard for governing AI responsibly across lifecycle. [ISO/IEC 42001](https://www.iso.org/standard/81230.html)

- **CycloneDX (ECMA-424) Bill of Materials standard** — supports SBOMs and AI/ML-BOM for model and dataset transparency and provenance tracking. [CycloneDX ML-BOM](https://cyclonedx.org/capabilities/mlbom/)

- **OWASP Top 10 for Agentic Applications — ASI04 (Supply Chain) and ASI06 (Memory and Context Poisoning)** — for practitioners extending LLM04 controls to agentic deployment contexts. [OWASP Agentic Top 10](https://genai.owasp.org)
