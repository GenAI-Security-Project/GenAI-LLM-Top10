## LLM05:2026 Data and Model Poisoning

### Description

Data & Model Poisoning describes a class of attacks and failures where an adversary (or unsafe process) manipulates data or model artifacts to embed harmful behavior, bias, or exploitable weaknesses into an AI system. In modern GenAI environments, poisoning is not limited to "training data" in the traditional sense — it can occur anywhere data is ingested, transformed, retrieved, or reused, including during pre-training, fine-tuning, embedding creation, retrieval augmentation (RAG), and model distribution. The result is an AI system that may still appear 
functional but behaves in ways that undermine trust, safety, and security.

Data poisoning occurs when pre-training, fine-tuning, or embedding data is tampered with to introduce vulnerabilities, backdoors, or biases. This can happen intentionally (malicious poisoning) or unintentionally (poor data hygiene, contaminated sources). The manipulation compromises model integrity — the model learns the wrong patterns, internalizes malicious correlations, or is conditioned to behave incorrectly. The consequences include harmful outputs, impaired capabilities, and degraded reliability.

The key idea: poisoning targets the model's "learning process," not a single runtime bug. Unlike typical software vulnerabilities that can be patched by fixing code, poisoning can require data revalidation, retraining, model replacement, or pipeline redesign — making it expensive and operationally disruptive.

Poisoning can occur across multiple stages of the LLM lifecycle:

- **Pre-training:** Maliciously crafted or contaminated corpora cause the model to absorb harmful patterns, unsafe instructions, or skewed representations.
- **Fine-tuning:** Manipulated datasets introduce  domain-specific failure modes or hidden triggers.
- **Embeddings and vectorization:** Poisoning targets  stored vectors to influence retrieved content, resulting in steered answers or subtle misinformation.
- **Transfer learning / model reuse:** Compromised source models pass that compromise to downstream systems.
- **Continuous learning pipelines:** Automated ingestion without sufficient validation allows attackers to gradually shape model behavior.

The data poisoning surface expands because organizations increasingly rely on external datasets, RAG pipelines, shared model repositories, and agentic workflows. Models distributed through shared repositories can carry risks through bundled non-weight artifacts — including malicious deserialization (e.g. pickle files) and tampering of chat templates, tokenizer configs, LoRA/PEFT adapters, and quantization artifacts — any of which can execute harmful code or alter model behavior when loaded. Such backdoors may leave model behavior untouched until a trigger causes it to change, creating the opportunity for a model to become a sleeper agent.

In agentic deployments, poisoning risks extend to tool integrations, persistent memory stores, and RLHF feedback loops — attack surfaces covered in depth in the OWASP Top 10 for Agentic Applications.

---

### Common Examples of Risk

1. **Training & Fine-Tuning Data Poisoning:** Attackers inject biased or malicious content into datasets. Microsoft Tay demonstrated rapid degradation when users poisoned its learning data. A targeted variant deliberately erodes refusal behaviors while preserving general accuracy, making degradation undetectable through standard evaluation.

2. **Financial Model Data Poisoning:** Attackers inject mislabeled transaction data into fraud 
detection models, labeling fraud as legitimate. The model learns to ignore real threats, enabling fraud bypass and undermining trust in AI-driven financial systems.

3. **Open-Source Dataset Supply Chain Poisoning:** Attackers contribute malicious data to widely used datasets. A 2024 case showed trigger phrases inserted across dozens of downstream models, requiring costly retraining.

4. **Low-Volume High-Impact Backdoor Poisoning:** As few as 250 poisoned documents compromise models from 600M to 13B parameters regardless of dataset size (Souly et al., arXiv:2510.07192, 2025). Strategic minimal manipulation is sufficient for significant impact.

5. **AI Recommendation / Memory Poisoning:** Attackers embed hidden instructions in web content to manipulate AI memory or recommendations without detection, demonstrating risks in agent-based systems and persistent memory.

6. **RAG Knowledge Base Poisoning:** Injecting as few as 3-10 semantically optimized adversarial documents overrides accurate content across a retrieval pipeline. Standard defenses including perplexity-based filtering fail (CorruptRAG, Zhang et al., 2025).

7. **Agent / Multi-System Poisoning:** Poisoned inputs in multi-agent workflows influence behavior and data access across entire AI-driven ecosystems, not just individual models.

8. **Healthcare Model Poisoning:** Minimal poisoning of medical training data significantly alters model outputs while passing standard evaluations, creating unsafe recommendations in safety-critical domains.

9. **Malicious AI Models in Supply Chain:** Attackers distribute compromised models via public repositories with embedded backdoors. Organizations downloading these models unknowingly inherit hidden triggers or system compromise.

10. **Prompt / Content Injection via External Data:** Attackers inject malicious content through inputs, forums, or APIs. Real incidents show chatbots producing manipulated outputs and exposing internal instructions from unverified external sources.

---

### Prevention and Mitigation Strategies

1. Track dataset and model lineage using SBOM/ML-BOM (e.g., CycloneDX), enforce signing and verification, and continuously validate data integrity across lifecycle stages.

2. Establish strict validation for all incoming data, vet third-party vendors, and compare outputs against trusted sources to detect bias or adversarial manipulation early.

3. Protect RAG systems by enforcing trust boundaries, filtering retrieved content, applying source scoring, and isolating system instructions from external data.

4. Use sandboxing and strict isolation controls to limit model interaction with unverified data, plugins, or external systems.

5. Apply statistical and AI-based anomaly detection across training, embedding, and inference pipelines. Monitor outputs and behavioral patterns for drift using defined thresholds.

6. Use curated domain-specific datasets for fine-tuning to reduce exposure to untrusted data and cross-domain contamination.

7. Enforce least-privilege access, network segmentation, and strict data access controls to prevent unauthorized data injection.

8. Use DVC to track dataset changes, maintain version history, and enable rollback and forensic analysis when poisoning is detected.

9. Control automated retraining and feedback loops by validating incoming data, requiring human oversight, and applying rate limits against gradual poisoning through manipulated preference signals.

10. Continuously red team models with adversarial inputs and trigger-based prompts to identify hidden backdoors. Do not assume safety alignment removes backdoors — dedicated trigger-probing is required after every alignment cycle (Hubinger et al., arXiv:2401.05566, 2024).

11. Monitor outputs, training loss, and behavioral patterns for drift or anomalies using defined 
thresholds to detect subtle poisoning effects over time.

12. Implement grounding techniques with validation layers ensuring retrieved content is verified before influencing outputs.

13. Treat inference artifacts — including chat templates, tokenizer configs, LoRA/PEFT adapters, and quantization artifacts — as security-relevant code. Enforce signing, hash verification, diff checks, and static analysis before deployment.

---

### Example Attack Scenarios

**Scenario #1**

An attacker inserts manipulated documents into an internal knowledge repository. Poisoned documents surface in responses, leading to incorrect recommendations, manipulated business decisions, or reputational damage.

**Scenario #2**

An attacker embeds hidden instructions in webpages summarized by AI tools. When ingested into RAG or memory systems, the instructions bias the model to recommend specific products, enabling financial manipulation and loss of trust in AI outputs.

**Scenario #3**

An attacker submits crafted inputs into an automated retraining feedback loop. No infrastructure access is required — only standard user interface access. The result is slow model drift toward degraded accuracy, biased outputs, or unsafe recommendations.

**Scenario #4**

A malicious insider injects mislabeled transaction data into a training dataset. The model fails to 
detect fraud, resulting in financial losses, compliance violations, and regulatory breach.

**Scenario #5**

An attacker uploads poisoned pre-trained weights to a public repository. Standard safety training fails to remove embedded backdoors (Hubinger et al., arXiv:2401.05566, 2024). Organizations face system compromise, data leakage, or targeted manipulation at scale.

**Scenario #6**

An attacker modifies a chat template in a GGUF package with trigger-activated conditional 
instructions. Redistributed via a public hub, the model behaves normally under benign inputs. 
Validated across 18 models and 4 inference runtimes — factual accuracy drops from 90% to 15% under trigger conditions and URL emission exceeds 80% success rate (Fogel et al., arXiv:2602.04653, 2026).

**Scenario #7**

A developer loads a third-party model using unsafe serialization (e.g., pickle). Embedded malicious code executes during loading, enabling host compromise, lateral movement, and infrastructure breach.

**Scenario #8**

In a shared AI environment, one tenant injects adversarial data into shared embeddings or memory layers, influencing other tenants' responses and causing cross-tenant contamination and privacy risk.

**Scenario #9**

An attacker injects malicious instructions into an AI agent's persistent memory over multiple sessions. The agent begins prioritizing attacker-controlled logic, resulting in long-term workflow manipulation and hidden persistence.

---

### Reference Links

1. [CycloneDX — Machine Learning Bill of Materials (AI/ML-BOM)](https://cyclonedx.org/capabilities/mlbom/)
2. [DVC — Data Version Control](https://dvc.org/doc)
3. [MITRE ATLAS — Adversarial Threat Landscape for AI Systems](https://atlas.mitre.org)
4. [NIST AI Risk Management Framework (AI RMF 1.0)](https://www.nist.gov/itl/ai-risk-management-framework)
5. [JFrog Security Research — GGUF-SSTI (Jinja2 template injection)](https://jfrog.com/blog/)
6. [GitHub Security Advisory — Giskard Jinja2 SSTI (GHSA-frv4-x25r-588m)](https://github.com/advisories/GHSA-frv4-x25r-588m)
7. [Inference-Time Backdoors via Hidden Instructions in LLM Chat Templates — Fogel et al., arXiv:2602.04653](https://arxiv.org/abs/2602.04653)
8. [Sleeper Agents: Training Deceptive LLMs — Hubinger et al., arXiv:2401.05566](https://arxiv.org/abs/2401.05566)
9. [Near-Constant Poisoning Threshold — Souly et al., arXiv:2510.07192](https://arxiv.org/abs/2510.07192)
10. [F5 Operations Guide — Data and Model Poisoning](https://f5.com)

### Related Frameworks and Taxonomies

| Framework | Reference | Relevance |
|---|---|---|
| **OWASP Top 10 for Agentic Applications (ASI)** | ASI04 — Agentic Supply Chain Vulnerabilities | Poisoned pre-trained models and malicious deserialization distributed via public repositories (Scenarios #5, #7) and tampered inference-time artifacts such as chat templates/GGUF (Scenario #6; mitigation #13) |
| **OWASP Top 10 for Agentic Applications (ASI)** | ASI06 — Memory & Context Poisoning | Persistent agent memory and recommendation poisoning (Common Example #5) and long-term manipulation of agent decisions via injected memory (Scenario #9) |
| **OWASP Top 10 for Agentic Applications (ASI)** | ASI08 — Cascading Failures | Poisoned inputs propagating across multi-agent and enterprise workflows into unintended data exposure (Common Example #7) and cross-tenant contamination via shared embeddings/memory (Scenario #8) |
| **MITRE ATLAS** | [MITRE ATLAS](https://atlas.mitre.org) | ATT&CK-style knowledge base of adversary tactics and techniques against AI/ML systems, including poisoning techniques and case studies |
| **MITRE ATLAS** | [Split-View poisoning case study](https://atlas.mitre.org/studies) | Case study demonstrating dataset poisoning risk in web-scale, URL-based training datasets |
| **NIST CSRC** | [MITRE ATLAS overview](https://csrc.nist.gov) | Links the ATLAS technique taxonomy to NIST assurance concepts for governance and audit audiences |
| **NIST AI RMF** | [NIST AI Risk Management Framework 1.0](https://www.nist.gov/itl/ai-risk-management-framework) | Govern/Map/Measure/Manage lifecycle functions mappable to data and model poisoning controls |
| **NIST AI RMF** | [NIST.AI.100-1 (PDF)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) | Authoritative publication for formal citation of the AI RMF |
| **CSA AI Controls Matrix (AICM)** | [CSA AICM](https://cloudsecurityalliance.org) | Vendor-agnostic cloud AI control objectives, mapped to ISO 42001 and NIST AI RMF, applicable to dataset and model integrity controls |
| **ISO/IEC 42001 (AIMS)** | [ISO/IEC 42001](https://www.iso.org/standard/81230.html) | Certifiable AI management system standard for governing dataset and model integrity across the lifecycle |
| **CycloneDX (ECMA-424)** | [ML-BOM](https://cyclonedx.org/capabilities/mlbom/) | Bill-of-materials standard for dataset/model lineage and provenance tracking, aligned with this entry's SBOM/ML-BOM mitigation (Prevention #1) |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI04 — Data, Model & Artifact Poisoning | Closest peer entry — covers the same supply-chain compromise, artifact tampering, and training/retrieval poisoning lifecycle stages this entry addresses |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI05 — Data Integrity & Validation Failures | Schema/semantic validation bypass and snapshot-import path traversal that corrupt training or retrieval data without tripping ingestion alerts — a related but distinct failure mode from overt poisoning |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI21 — Disinformation & Integrity Attacks via Data Poisoning | RAG knowledge-base poisoning that surfaces adversary-controlled content as authoritative, mirroring this entry's Common Example #6 and Scenarios #1–#2 |
