## LLM09:2026 Vector and Embedding Weaknesses

### Description

Vector and embedding weaknesses present security risks in any LLM application that converts text, images, code, or audio into numerical representations and uses similarity search to decide what the model sees. Retrieval-Augmented Generation (RAG) is the most familiar case, but the same machinery underlies vector-backed agent memory, semantic caches, and deduplication pipelines. Whenever similarity search sits between a data source and the prompt, the embedding layer becomes part of the application's trust boundary.

These weaknesses are distinct from prompt injection. They exploit the geometry of the embedding space and the mechanics of similarity search rather than the model's instruction-following behavior; many succeed even when the retrieved content carries no malicious instructions at all. A useful frame: poisoning makes the system wrong, inversion makes it leak, jamming makes it silent, and access-control failure makes it indiscriminate.

This entry covers attacks that depend on the embedding layer to succeed. Indirect prompt injection through retrieved content is covered in LLM01:2026 Prompt Injection; training-time poisoning of the embedding model in LLM05:2026 Data and Model Poisoning; serialization flaws in vector-store libraries in LLM04:2026 Supply Chain; agent-memory attacks that do not rely on embedding geometry in ASI06:2026 Memory and Context Poisoning (OWASP Top 10 for Agentic Applications). Vectorless retrieval systems (BM25-only, LLM-native tree navigation) inherit the non-geometric risks but have no LLM09 attack surface.

### Common Examples of Risk

#### 1. Cross-Tenant Leakage via Shared Similarity Search

In multi-tenant deployments, similarity search frequently runs across the full index before access control is applied at the application layer. Where the application exposes result counts, score distributions, or measurable timing differences, an attacker can probe the index with crafted queries and infer the existence, topic, and approximate volume of other tenants' documents — without ever seeing the documents. The attack succeeds even when every document is correctly tagged and every API call authenticated, because the access-control decision happens after the embedding-space search has run. This also raises the stakes of ordinary authentication bugs in vector-store software: because a vector-store leak is recoverable to source documents via inversion (Risk #2), such a bug carries higher consequence than the same bug in a document database or key-value store.

#### 2. Embedding Inversion

Stored embeddings can be inverted to recover source text. Reported recovery rates range from roughly 50–70% of words from sentence embeddings to 92% exact reconstruction of short 32-token inputs (Vec2Text; Morris et al., EMNLP 2023), which trains an inversion model per encoder. ZSInvert (Zhang, Morris, Shmatikov) and Zero2Text (Kim et al.) operate zero-shot with no encoder-specific training, work in cross-domain and black-box settings, and remain effective against differential-privacy noise added at storage. Recovery feasibility varies with the encoder, the input length, and the attacker's knowledge, but the trend line is clear. Operationally: vector-database backups, embeddings shipped to third-party services, and embeddings exposed through misconfigured cloud storage should be treated as potentially equivalent to a leak of the underlying documents. Under GDPR and similar regimes, breach notification depends on risk to data subjects — and because modern embeddings can be inverted, that risk is real.

#### 3. Retrieval-Time Data Poisoning

An attacker who can write to the corpus — via public scraping pipelines, file uploads, partner feeds, or compromised internal sources — can craft content whose embedding lands close to a target query. When a user submits that query, the attacker's content is retrieved and fed to the LLM as trusted context. Published attacks reliably achieve high success rates with a handful of poisoned documents, even in corpora of millions and against black-box systems. A successful attack requires two conditions simultaneously: the poisoned content must be retrieved (geometric) and must steer the response (generation); defenders can intervene at either layer. MITRE ATLAS catalogs this class as AML.T0070 (RAG Poisoning) under the Persistence tactic. Training-time poisoning of the embedding model itself is LLM05:2026.

#### 4. Retrieval Jamming

Attackers can take a RAG system off the air by inserting a "blocker" document — content engineered to be retrieved for a specific query and to cause the LLM to refuse to answer or claim it lacks information. Unlike poisoning, the blocker carries no malicious instructions; it exploits retrieval mechanics and LLM safety behavior. A single blocker document, generated through black-box optimization without access to the target embedding model or LLM, is sufficient. This is an availability attack on the retrieval layer.

#### 5. Membership Inference via Similarity Search

The attacker wants to know whether a specific document — a medical record, a legal filing, an HR complaint — exists in the index, not what it says. If the application returns raw similarity scores or distances to the client, the index becomes a direct membership oracle with no LLM involved. If it returns only generated answers, the attacker can still infer membership by submitting partial documents or perturbed queries and analyzing responses. Membership information can itself be sensitive even when content remains protected.

#### 6. Semantic Cache and Deduplication Poisoning

Semantic caches and near-duplicate detection use a cosine-similarity threshold to decide two pieces of content are "the same." An attacker who can craft content landing just above or below that threshold can poison a cache entry so it serves attacker text to all semantically equivalent queries, bypass deduplication with near-duplicates of poisoned content, or force legitimate new content to be silently dropped as a duplicate. Wu et al. (NDSS 2026) demonstrate semantic cache poisoning end-to-end across AWS, Azure, and Alibaba deployments; Zhang et al. show black-box key-collision attacks that use surrogate embedding models to engineer threshold-straddling vectors without access to the target encoder. All three failure modes depend on embedding-space geometry and are invisible to document-level controls.

#### 7. Multimodal Embedding Poisoning

Cross-modal encoders such as CLIP and ColPali map images, audio, code, and text into one vector space. An attacker who can contribute non-text content can craft an image whose embedding sits close to a sensitive text query; when a user submits that query, the image is retrieved as trusted context. MM-PoisonRAG (Ha et al.) and Poisoned-MRAG (Liu et al.) demonstrate local and global poisoning across multimodal RAG pipelines; "One Pic is All it Takes" shows a single image suffices for targeted and universal VD-RAG poisoning. To a human reviewer the image appears unremarkable, and text-based content scanning does not catch it because the payload is not text.


### Prevention and Mitigation Strategies

#### 1. Permission and Access Control

Enforce tenant scoping inside the index query, not as a post-retrieval filter, and validate it server-side — a client-supplied scope is a suggestion, not a control. Authenticate embedding and similarity-search endpoints as first-class APIs with per-tenant rate limits. For high-sensitivity workloads, use physically separated indexes per tenant or trust zone. Apply access control at the chunk level: a mostly-public document can contain a confidential paragraph.

#### 2. Data Validation, Source Authentication, and Provenance

Normalize content before embedding: strip zero-width characters, white-on-white text, and Unicode homoglyphs at extraction. Track provenance for every embedding — source, ingestion time, trust tier, pipeline version — so compromised batches can be invalidated and audited. Apply human review to externally sourced content destined for sensitive indexes. Vet the embedding model itself; a backdoored encoder corrupts the geometry of everything ingested.

#### 3. Data Segregation by Trust Tier

Mixed-trust content — external web data, internal confidential documents, partner data — must not share an index without hard isolation. For high-sensitivity or high-assurance isolation, use separate indexes rather than classification tags on a shared index: separate indexes remove the misconfiguration path that a shared-index tagging scheme depends on.

#### 4. Anomaly Detection at Ingest and Retrieval

Flag new vectors that sit unusually close to a wide range of common queries — the signature of retrieval-hijacking poisoning. Watch for queries returning too many high-similarity matches, unusual volume on embedding endpoints (a precursor to query-based inversion), and clusters growing faster than expected after ingest. Do not return raw similarity scores to clients, and rate-limit endpoints that could be queried as oracles. Cross-encoder re-ranking raises attack cost but does not replace provenance and ingest controls; modern attacks target retrieval and ranking jointly.

#### 5. Storage Lifecycle Controls

Delete embeddings within a bounded time when the source document is deleted, and verify with reconciliation audits. Treat vector-database backups at the same sensitivity tier as source documents. Encrypt embeddings at rest with keys managed separately from the application layer. When rotating the embedding model, re-embed the corpus rather than mixing old and new vectors — heterogeneous embeddings create exploitable gaps in similarity behavior. Treat embedding-API keys as secrets; a leaked key gives an attacker query access to your exact encoder.

#### 6. Monitoring, Logging, and Incident Response

Keep immutable logs of retrieval activity (tenant scope, query, returned IDs, similarity scores). Monitor for tenant-filter bypass attempts, cross-tenant retrieval anomalies, and abnormal embedding-API consumption. Update incident-response playbooks so "embeddings only" leaks are treated as source-data leaks for breach assessment and notification under GDPR Article 33 and analogous regimes.

### Example Attack Scenarios

#### Scenario #1: Embedding Similarity Attack on a Public Ingestion Pipeline

A company's RAG system scrapes public documentation and forum posts on a schedule. An attacker publishes posts engineered so their embeddings land near specific internal queries, such as "what is our Q3 revenue projection." When an employee asks that question, the attacker's content is retrieved and fed to the LLM. The same text pasted into a chat would have no effect — the attack works only because the attacker can place content near a target query in embedding space.

#### Scenario #2: Cross-Tenant Inference in a Shared Vector Index

A multi-tenant SaaS product uses one shared vector index with tenant filtering at the application layer, and its API returns similarity scores and result counts to callers. Tenant A submits probing queries; similarity search runs across every embedding, including Tenant B's, before the filter is applied. A never sees B's documents, but the exposed scores, result counts, and timing differences reveal the existence and approximate topic of B's content. Over many queries, A builds a useful map of B's data.

#### Scenario #3: Embedding Inversion from a Leaked Vector Store

A cloud misconfiguration exposes a backup of a production vector database. The underlying documents — customer conversation logs containing PII — are encrypted separately and not exposed, so the incident is initially classified as low-severity: "only the embeddings leaked." The attacker runs a zero-shot inversion attack against the stolen embeddings and reconstructs a substantial fraction of the source content, including PII, without access to the original encoder. The incident is reclassified as equivalent to a source-document breach and notification obligations are reassessed. "Embeddings only" is not a safe-harbor classification.

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
15. [One Pic is All it Takes: Poisoning Visual Document Retrieval Augmented Generation with a Single Image](https://arxiv.org/abs/2504.02132): Shereen et al., **arXiv:2504.02132**.
16. [When Cache Poisoning Meets LLM Systems](https://www.ndss-symposium.org/ndss-paper/when-cache-poisoning-meets-llm-systems-semantic-cache-poisoning-and-its-countermeasures/): Wu et al., **NDSS 2026**.
17. [From Similarity to Vulnerability: Key Collision Attack on LLM Semantic Caching](https://arxiv.org/abs/2601.23088): Zhang, Liu, Xie, Huang, She, **arXiv:2601.23088**.
18. [Astute RAG: Overcoming Imperfect Retrieval Augmentation and Knowledge Conflicts for Large Language Models](https://arxiv.org/abs/2410.07176): **arXiv:2410.07176**.

### Related Frameworks and Taxonomies

| Framework | Reference | Relevance |
|---|---|---|
| **OWASP Top 10 for Agentic Applications (ASI)** | ASI04 — Agentic Supply Chain Vulnerabilities | Embedding-model supply chain: Prevention and Mitigation Strategies #2 directs vetting the embedding model itself, since "a backdoored embedding model corrupts the geometry of everything ingested" |
| **OWASP Top 10 for Agentic Applications (ASI)** | ASI06 — Memory & Context Poisoning | Agent-memory poisoning that does not rely on embedding geometry is out of scope here and referred to ASI06 (Description, final scope-boundary sentence) |
| **MITRE ATLAS** | [AML.T0020 — Poison Training Data](https://atlas.mitre.org/techniques/AML.T0020) | Training-time poisoning of the embedding model, distinguished from this entry's retrieval-time poisoning scope |
| **MITRE ATLAS** | [AML.T0024 — Exfiltration via AI Inference API](https://atlas.mitre.org/techniques/AML.T0024) | Exfiltration channel for cross-tenant inference or inverted-embedding recovery |
| **MITRE ATLAS** | [AML.T0024.001 — Invert AI Model](https://atlas.mitre.org/techniques/AML.T0024.001) | Model-inversion technique underlying Risk #2 Embedding Inversion |
| **MITRE ATLAS** | [AML.T0036 — Data from Information Repositories](https://atlas.mitre.org/techniques/AML.T0036) | Vector-store and RAG corpus access as an information-repository target |
| **MITRE ATLAS** | [AML.T0057 — LLM Data Leakage](https://atlas.mitre.org/techniques/AML.T0057) | General data-leakage technique applicable to embedding inversion and cross-tenant retrieval |
| **MITRE ATLAS** | [AML.T0070 — RAG Poisoning](https://atlas.mitre.org/techniques/AML.T0070) | Persistence tactic; primary mapping for Risk #3 Retrieval-Time Data Poisoning |
| **MITRE ATLAS** | [AML.T0086 — Exfiltration via AI Agent Tool Invocation](https://atlas.mitre.org/techniques/AML.T0086) | Relevant when agent tools become the exfiltration channel for cross-tenant inference or inverted embeddings |
| **MITRE ATLAS** | [AML.T0099 — AI Agent Tool Data Poisoning](https://atlas.mitre.org/techniques/AML.T0099) | Added in the January 2026 ATLAS update (atlas-data v5.2.0); agent-tool framing of the retrieval-time poisoning phenomenon captured by AML.T0070, applicable when the agent's "tool" is a vector-store retriever |
| **MITRE ATLAS** | [AML.M0005 — Control Access to AI Models and Data at Rest](https://atlas.mitre.org/mitigations/AML.M0005) | Storage-lifecycle and encryption-at-rest controls for embeddings and vector-store backups |
| **MITRE ATLAS** | [AML.M0019 — Control Access to AI Models and Data in Production](https://atlas.mitre.org/mitigations/AML.M0019) | Production access controls underlying the Permission and Access Control mitigations |
| **MITRE CWE** | [CWE-200 — Exposure of Sensitive Information to an Unauthorized Actor](https://cwe.mitre.org/data/definitions/200.html) | General sensitive-information exposure via embedding inversion or cross-tenant leakage |
| **MITRE CWE** | [CWE-285 — Improper Authorization](https://cwe.mitre.org/data/definitions/285.html) | Cross-tenant retrieval where authorization is applied after, rather than inside, the index query |
| **MITRE CWE** | [CWE-732 — Incorrect Permission Assignment for Critical Resource](https://cwe.mitre.org/data/definitions/732.html) | Vector-store access-control misconfiguration |
| **NIST AI 100-2** | Adversarial Machine Learning — Privacy Attacks (Membership Inference, Model Inversion) | Privacy-attack taxonomy underlying Risk #2 Embedding Inversion and Risk #5 Membership Inference via Similarity Search |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI11 — Cross-Context & Multi-User Conversation Bleed | Illustrative scenario (shared vector store, missing tenant scoping in the retrieval filter) parallels Risk #1 Cross-Tenant Leakage via Shared Similarity Search |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI13 — Vector Store Platform Data Security | Closest peer entry. Its illustrative scenario (mis-scoped ACLs, k-NN reconstruction of proprietary documents from a leaked index) mirrors Risks #1 and #2 together |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI18 — Inference & Data Reconstruction | Describes embedding inversion via nearest-neighbor approximation and membership inference against vector stores, mapping to Risk #2 and Risk #5 |

