## LLM08:2026 Vector and Embedding Weaknesses

### Description

Vector and embedding weaknesses present security risks in any LLM application that converts text, images, code, or audio into numerical representations and uses similarity search to decide what the model sees. Retrieval-Augmented Generation (RAG) is the most familiar case, but the same machinery underlies vector-backed agent memory, semantic caches, and deduplication pipelines. Whenever similarity search sits between a data source and the prompt, the embedding layer becomes part of the application's trust boundary.

These weaknesses are distinct from prompt injection. They exploit the geometry of the embedding space and the mechanics of similarity search rather than the model's instruction-following behavior. Many of them succeed even when the retrieved content carries no malicious instructions at all. A useful frame: poisoning makes the system wrong, inversion makes it leak, jamming makes it silent, and access-control failure makes it indiscriminate.

This entry covers the attacks that depend on the embedding layer to succeed. Indirect prompt injection through retrieved content is covered in LLM01:2026 Prompt Injection. Training-time poisoning of the embedding model itself is covered in LLM04:2026 Data and Model Poisoning. Serialization and deserialization flaws in vector-store libraries are covered in LLM03:2026 Supply Chain. Agent-memory attacks that do not rely on embedding geometry are covered in ASI06:2026 Memory and Context Poisoning in the OWASP Top 10 for Agentic Applications. Vectorless retrieval systems (BM25-only, LLM-native tree navigation) inherit the non-geometric risks above but do not have an LLM08 attack surface.

### Common Examples of Risk

#### 1. Cross-Tenant Leakage via Shared Similarity Search

In multi-tenant deployments, similarity search frequently runs across the full index before access control is applied at the application layer. An attacker can probe the index with crafted queries and infer the existence, topic, and approximate volume of other tenants' documents from result counts, score distributions, and timing — without ever seeing the documents themselves. The attack succeeds even when every document is correctly tagged with its tenant and every API call is correctly authenticated, because the access-control decision happens after the embedding-space search has already run. Correct implementations enforce tenant scoping inside the index query, validate it server-side, and for high-sensitivity workloads use physically separated indexes per tenant or per trust zone.
Conventional authentication and access-control flaws in vector-DB software — for example CVE-2025-64513 (Milvus, forged sourceID header bypassing authentication, CVSS 9.3) and CVE-2025-69286 (RAGFlow, predictable token derivation enabling account takeover, CVSS 9.3), are out of scope for this entry, but they compound the impact of the geometric risk above. A vector-store leak is recoverable to source documents via embedding inversion (Risk #2), so an auth bug in a vector database carries higher consequence than the same bug in a document database or key-value store.

#### 2. Embedding Inversion

Stored embeddings can be inverted to recover source text. Early attacks required millions of paired training samples against a specific encoder and were considered impractical against production systems. Recent zero-shot and few-shot methods recover semantic content with no encoder-specific training, work in cross-domain and black-box settings, and remain effective against differential-privacy noise added at the storage layer. The operational consequence is that vector-database backups, embeddings shipped to third-party services, and embeddings exposed through misconfigured cloud storage should be treated as equivalent to a leak of the underlying source documents. Don't dismiss an "embeddings only" leak as a non-event. Under GDPR and similar regimes, breach notification depends on the risk to data subjects — and because modern embeddings can be inverted, that risk is real.

#### 3. Retrieval-Time Data Poisoning

An attacker who can write to the corpus — through public scraping pipelines, file uploads, partner data feeds, or compromised internal sources, can craft content whose embedding lands close to a target query in vector space. When a user submits that query, the attacker's content is retrieved and fed to the LLM as trusted context. Published attacks reliably achieve high success rates with a small number of poisoned documents, even in corpora containing millions of legitimate documents, and against black-box systems where the attacker has no knowledge of the embedding model. A successful attack requires two conditions to hold simultaneously: the poisoned content must be retrieved (a geometric condition) and it must steer the model's response (a generation condition). Defenders can intervene at either layer. This entry covers retrieval-time poisoning specifically; training-time poisoning of the embedding model is covered in LLM04:2026. MITRE ATLAS catalogs this class as AML.T0070 (RAG Poisoning) under the Persistence tactic.

#### 4. Retrieval Jamming

Attackers can take a RAG system off the air by inserting a "blocker" document — content engineered to be retrieved for a specific query and to cause the LLM to refuse to answer or claim it lacks information. Unlike poisoning, the blocker carries no malicious instructions; it exploits retrieval mechanics and LLM safety behavior to produce a refusal. A single blocker document, generated through black-box optimization without access to the target embedding model or LLM, is sufficient. This is an availability attack on the retrieval layer.

#### 5. Membership Inference via Similarity Search

The attacker wants to know whether a specific document — a medical record, a legal filing, an HR complaint, exists in the index, not what it says. Two variants exist. If the application returns raw similarity scores or distances to the client, the vector index becomes a direct membership oracle and no LLM is involved. If the application returns only generated answers, the attacker can still infer membership by submitting partial documents or perturbed queries and analyzing the response. Membership information can itself be sensitive even when content remains protected. Defenders should not return raw similarity scores to clients, should add noise and diversification at the retrieval-ranking layer, and should rate-limit endpoints that could be queried as oracles.

#### 6. Semantic Cache and Deduplication Poisoning

Semantic caches and near-duplicate detection pipelines use a cosine-similarity threshold to decide that two pieces of content are "the same." An attacker who can craft content that lands just above or just below that threshold can poison a cache entry so it serves attacker text to all semantically equivalent queries, bypass deduplication by injecting many near-duplicates of poisoned content, or force legitimate new content to be silently dropped as a duplicate. All three failure modes depend on the geometry of the embedding space and are invisible to controls applied at the document level.

#### 7. Multimodal Embedding Poisoning

Cross-modal encoders such as CLIP and ColPali map images, audio, code, and text into the same vector space so that semantically related content across modalities produces similar vectors. An attacker who can contribute non-text content can craft an image whose embedding sits close to a sensitive text query. When a user submits that query, the attacker's image is retrieved and fed to the model as trusted context. To a human reviewer, the image appears unremarkable. Standard text-based content scanning does not catch the payload because the payload is not text. Image, audio, and code ingestion should carry the same provenance and trust-tier controls as text, and externally sourced non-text assets should not share an index with sensitive text content.

### Prevention and Mitigation Strategies

#### 1. Permission and Access Control

Enforce tenant scoping inside the index query, not as a post-retrieval filter. Validate the filter server-side; a client-supplied scope is a suggestion, not a control. Authenticate embedding and similarity-search endpoints as first-class APIs with per-tenant rate limits. For high-sensitivity workloads, use physically separated indexes per tenant or per trust zone. Apply access control at the chunk level, not just the document level: a mostly-public document can contain a confidential paragraph that any matching query will surface.

#### 2. Data Validation, Source Authentication, and Provenance

Normalize content before embedding. Strip zero-width characters, white-on-white text, and Unicode homoglyph tricks at the text-extraction step. Track provenance for every embedding — source, ingestion time, trust tier, pipeline version — so that compromised batches can be invalidated and audited later. Apply human review for externally sourced content destined for sensitive indexes. Vet the embedding model itself; a backdoored embedding model corrupts the geometry of everything ingested.

#### 3. Data Segregation by Trust Tier

Mixed-trust content — external web data, internal confidential documents, third-party partner data, must not share an index without hard isolation. Index-level segregation is a stronger control than classification tags applied to a shared index, because it removes the possibility of misconfiguration leaking content across trust tiers.

#### 4. Anomaly Detection at Ingest and Retrieval

Flag any new vector that sits unusually close to a wide range of common queries; this is the signature of retrieval-hijacking poisoning. Watch for queries that return too many high-similarity matches at once, for unusual volume on embedding endpoints (a precursor to query-based inversion), and for clusters that grow faster than expected after ingest. Cross-encoder re-ranking raises the cost of poisoning attacks but does not replace provenance and ingest-time controls; modern attacks target retrieval and ranking jointly.

#### 5. Storage Lifecycle Controls

When a source document is deleted, its embeddings must be deleted within a bounded time. Verify with reconciliation audits. Treat vector-database backups at the same sensitivity tier as the source documents, because embeddings can be inverted. Encrypt embeddings at rest. When the embedding model is rotated, re-embed the corpus rather than mixing old-model and new-model vectors in a single index. Heterogeneous embeddings create exploitable gaps in similarity behavior. Treat embedding-API keys as secrets; a leaked key gives an attacker query access to your exact encoder.

#### 6. Monitoring, Logging, and Incident Response

Maintain immutable logs of retrieval activity, including tenant scope, query, returned IDs, and similarity scores. Monitor for tenant-filter bypass attempts, cross-tenant retrieval anomalies, and abnormal embedding-API consumption. Update incident-response playbooks so that "embeddings only" leaks are treated as equivalent to source-data leaks for the purpose of breach assessment and notification under GDPR Article 33 and analogous regimes.

### Example Attack Scenarios

#### Scenario #1: Embedding Similarity Attack on a Public Ingestion Pipeline

A company's RAG system scrapes public documentation and forum posts on a schedule. An attacker publishes posts engineered so that their embeddings land near specific internal queries, such as "what is our Q3 revenue projection" or "recommended vendor for X." When an employee asks one of those questions, the attacker's content is retrieved and fed to the LLM. The same text pasted directly into a chat would have no effect — there would be nothing to retrieve. The attack only works because the attacker can place content near a target query in embedding space. Mitigations include flagging vectors that sit unusually close to many common queries, tracking provenance on every piece of ingested external content, and keeping external content out of indexes that also hold internal high-trust content.

#### Scenario #2: Cross-Tenant Inference in a Shared Vector Index

A multi-tenant SaaS product uses a single shared vector index for all customers and applies tenant filtering at the application layer. Tenant A submits queries designed to probe the index. Similarity search runs across every embedding, including Tenant B's, before the filter is applied. A never sees B's documents directly, but observes timing differences, result counts, and gaps in the score distribution that reveal the existence and approximate topic of B's content. Over many queries, A builds a useful map of B's data. The architectural fix is to push tenant scoping into the index query itself and validate server-side. For high-sensitivity workloads, separate physical indexes per tenant remove the shared-search surface entirely. Real-world incidents in this category include CVE-2025-69286 (RAGFlow), where predictable token generation enabled cross-account compromise in a widely deployed open-source RAG engine.

#### Scenario #3: Embedding Inversion from a Leaked Vector Store

A cloud misconfiguration exposes a backup of a production vector database. The underlying documents — customer conversation logs containing PII — are encrypted separately and were not exposed. Initial assessment classifies the incident as low-severity: "only the embeddings leaked." The attacker points a local model at the stolen embeddings and runs a zero-shot inversion attack. A substantial fraction of the source content, including PII, is reconstructed without any access to the original encoder. The incident is reclassified as equivalent in impact to a source-document breach, and notification obligations are reassessed. The operational lesson is that "embeddings only" is not a safe-harbor classification. Vector-store backups should be protected at the same tier as source-document backups, embeddings should be encrypted at rest, and incident-response playbooks should reflect the reconstructability of modern embeddings.

#### Scenario #4: Retrieval Jamming of a Customer-Support Assistant

A vendor operates a customer-support assistant grounded in a public knowledge base that accepts community contributions. An attacker submits a single carefully constructed document, optimized in a black-box setting against the deployed retriever. The document carries no instructions and triggers no content-safety classifier. When customers ask about a specific high-value product feature, the assistant retrieves the blocker document and refuses to answer, claiming it lacks information. The attacker has not exfiltrated data, modified the model's responses, or compromised the backend; the assistant is simply silent on the queries the attacker chose. Mitigations include retrieval anomaly detection on refusal-correlated documents, provenance tracking for community-contributed content, and re-ranking that does not collapse to the blocker.

#### Scenario #5: Multimodal Poisoning via an Image Index

An e-commerce assistant uses a shared multimodal index that stores both product photos and customer-uploaded images. An attacker uploads images whose embeddings sit close to the text query "is this product safe for children." The assistant retrieves the attacker's images and incorporates them into its response, leading the model to recommend products the attacker chose to promote. The attack succeeds without text payloads, hidden Unicode, or instructions of any kind — the geometry of the cross-modal embedding space is the entire attack surface. Mitigations include keeping externally contributed images out of indexes that serve sensitive queries, applying provenance and trust-tier controls to non-text assets, and treating cross-modal retrieval as a privileged operation.

### Reference Links

1. [Universal Zero-shot Embedding Inversion](https://arxiv.org/abs/2504.00147): Zhang, Morris, Shmatikov, **arXiv:2504.00147**.
2. [Zero2Text: Zero-Training Cross-Domain Inversion Attacks on Textual Embeddings](https://arxiv.org/abs/2602.01757): Kim et al., **arXiv:2602.01757** (2026).
3. [Information Leakage in Embedding Models](https://arxiv.org/abs/2004.00053): Song & Raghunathan, **arXiv:2004.00053**.
4. [Sentence Embedding Leaks More Information than You Expect: Generative Embedding Inversion Attack to Recover the Whole Sentence](https://arxiv.org/abs/2305.03010): Li et al., **arXiv:2305.03010**.
5. [Text Embeddings Reveal (Almost) As Much As Text](https://arxiv.org/abs/2310.06816): Morris et al., **EMNLP 2023**, arXiv:2310.06816.
6. [ALGEN: Few-shot Inversion Attacks on Textual Embeddings via Cross-Model Alignment and Generation](https://aclanthology.org/2025.acl-long.1185/): Chen, Xu, Bjerva, **ACL 2025**, arXiv:2502.11308.
7. [PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models](https://www.usenix.org/conference/usenixsecurity25/presentation/zou-poisonedrag): Zou et al., **USENIX Security 2025**, arXiv:2402.07867.
8. [BadRAG: Identifying Vulnerabilities in Retrieval Augmented Generation of Large Language Models](https://arxiv.org/abs/2406.00083): Xue et al., **arXiv:2406.00083**.
9. [Phantom: General Backdoor Attacks on Retrieval Augmented Language Generation](https://arxiv.org/abs/2405.20485): Chaudhari et al., **arXiv:2405.20485**.
10. [AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases](https://arxiv.org/abs/2407.12784): Chen et al., **NeurIPS 2024**, arXiv:2407.12784.
11. [Machine Against the RAG: Jamming Retrieval-Augmented Generation with Blocker Documents](https://www.usenix.org/conference/usenixsecurity25/presentation/shafran): Shafran, Schuster, Shmatikov, **USENIX Security 2025**, arXiv:2406.05870.
12. [RevPRAG: Revealing Poisoning Attacks in Retrieval-Augmented Generation through LLM Activation Analysis](https://aclanthology.org/2025.findings-emnlp.698/): Tan et al., **Findings of EMNLP 2025**, arXiv:2411.18948.
13. [MM-PoisonRAG: Disrupting Multimodal RAG with Local and Global Poisoning Attacks](https://arxiv.org/abs/2502.17832): Ha et al., **arXiv:2502.17832**.
14. [Poisoned-MRAG: Knowledge Poisoning Attacks to Multimodal Retrieval Augmented Generation](https://arxiv.org/abs/2503.06254): Liu et al., **arXiv:2503.06254**.
15. [The Hidden Threat in Plain Text: Attacking RAG Data Loaders](https://dl.acm.org/doi/10.1145/3733799.3762976): Castagnaro et al., **AISec '25 (CCS 2025)**, arXiv:2507.05093.
16. [Astute RAG: Overcoming Imperfect Retrieval Augmentation and Knowledge Conflicts for Large Language Models](https://arxiv.org/abs/2410.07176): **arXiv:2410.07176**.
17. [GHSA-mhjq-8c7m-3f7p — Milvus Proxy Authentication Bypass (CVE-2025-64513)](https://github.com/milvus-io/milvus/security/advisories/GHSA-mhjq-8c7m-3f7p): **CVSS 9.3**, affects Milvus < 2.4.24, < 2.5.21, < 2.6.5.
18. [GHSA-9j5g-g4xm-57w7 — RAGFlow Predictable Token Generation (CVE-2025-69286)](https://github.com/infiniflow/ragflow/security/advisories/GHSA-9j5g-g4xm-57w7): **CVSS 9.3**, affects RAGFlow < 0.22.0.

### Related Frameworks and Taxonomies

Refer to this section for comprehensive information, scenarios, strategies, and best practices that complement this entry.

* [AML.T0020 — Poison Training Data](https://atlas.mitre.org/techniques/AML.T0020) **MITRE ATLAS**
* [AML.T0024 — Exfiltration via AI Inference API](https://atlas.mitre.org/techniques/AML.T0024) **MITRE ATLAS**
* [AML.T0024.001 — Invert AI Model](https://atlas.mitre.org/techniques/AML.T0024.001) **MITRE ATLAS**
* [AML.T0036 — Data from Information Repositories](https://atlas.mitre.org/techniques/AML.T0036) **MITRE ATLAS**
* [AML.T0057 — LLM Data Leakage](https://atlas.mitre.org/techniques/AML.T0057) **MITRE ATLAS**
* [AML.T0070 — RAG Poisoning](https://atlas.mitre.org/techniques/AML.T0070) **MITRE ATLAS** (Persistence tactic; primary mapping for Risk #3 Retrieval-Time Data Poisoning)
* [AML.T0086 — Exfiltration via AI Agent Tool Invocation](https://atlas.mitre.org/techniques/AML.T0086) **MITRE ATLAS** (relevant when agent tools become the exfiltration channel for cross-tenant inference or inverted embeddings)
* [AML.T0099 — AI Agent Tool Data Poisoning](https://atlas.mitre.org/techniques/AML.T0099) **MITRE ATLAS** (added in the January 2026 ATLAS update (atlas-data v5.2.0); agent-tool framing of the retrieval-time poisoning phenomenon captured by AML.T0070, applicable when the agent's "tool" is a vector-store retriever)
* [AML.M0005 — Control Access to AI Models and Data at Rest](https://atlas.mitre.org/mitigations/AML.M0005) **MITRE ATLAS**
* [AML.M0019 — Control Access to AI Models and Data in Production](https://atlas.mitre.org/mitigations/AML.M0019) **MITRE ATLAS**
* [CWE-200 — Exposure of Sensitive Information to an Unauthorized Actor](https://cwe.mitre.org/data/definitions/200.html) **MITRE CWE**
* [CWE-285 — Improper Authorization](https://cwe.mitre.org/data/definitions/285.html) **MITRE CWE** (cross-tenant retrieval)
* [CWE-340 — Generation of Predictable Numbers or Identifiers](https://cwe.mitre.org/data/definitions/340.html) **MITRE CWE** (predictable-token vector-store auth bypass)
* [CWE-732 — Incorrect Permission Assignment for Critical Resource](https://cwe.mitre.org/data/definitions/732.html) **MITRE CWE** (vector-store access control)
* NIST AI 100-2: Adversarial Machine Learning — Privacy Attacks (Membership Inference, Model Inversion).
* OWASP Top 10 for Agentic Applications — ASI06:2026 Memory and Context Poisoning (cross-reference for agent-memory cases).
* OWASP Top 10 for LLM Applications — LLM01 (Prompt Injection), LLM02 (Sensitive Information Disclosure), LLM03 (Supply Chain), LLM04 (Data and Model Poisoning).
