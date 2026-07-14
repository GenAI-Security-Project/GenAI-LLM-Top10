## LLM09:2026 Vector and Embedding Weaknesses

### Description

Vector and embedding weaknesses present security risks in any LLM application that converts text, images, code, or audio into numerical representations and uses similarity search to decide what the model sees. Retrieval-Augmented Generation (RAG) is the most familiar case, but the same machinery underlies vector-backed agent memory, semantic caches, and deduplication pipelines. Whenever similarity search sits between a data source and the prompt, the embedding layer becomes part of the application's trust boundary.

These weaknesses are distinct from prompt injection. They exploit the geometry of the embedding space and the mechanics of similarity search rather than the model's instruction-following behavior. Many succeed even when the retrieved content carries no malicious instructions at all. A useful frame: poisoning makes the system wrong, inversion makes it leak, jamming makes it silent, and access-control failure makes it indiscriminate.

This entry covers attacks that depend on the embedding layer to succeed. Adjacent risks live in other entries: indirect prompt injection through retrieved content in LLM01:2026 Prompt Injection, training-time poisoning of the embedding model in LLM05:2026 Data and Model Poisoning, serialization flaws in vector-store libraries in LLM04:2026 Supply Chain, and agent-memory attacks that do not rely on embedding geometry in ASI06:2026 Memory and Context Poisoning (OWASP Top 10 for Agentic Applications). Vectorless retrieval systems (BM25-only, LLM-native tree navigation) inherit the non-geometric risks but have no LLM09 attack surface.

### Common Examples of Risk

#### 1. Cross-Tenant Leakage via Shared Similarity Search

In multi-tenant deployments, similarity search frequently runs across the full index before access control is applied at the application layer. Where the system exposes similarity scores, result counts, or measurable timing differences, an attacker probing the index with crafted queries may infer the existence, topic, and approximate volume of other tenants' documents without ever seeing those documents. The attack can succeed even when every document is correctly tagged and every API call authenticated, because the access-control decision happens after the embedding-space search has run. Conventional authentication and access-control flaws in vector-database software are general application-security issues outside this entry's scope, but they carry higher consequence here: a vector-store leak is recoverable to source documents through inversion (Risk #2), so an authentication bug in a vector database is worse than the same bug in a document database or key-value store.

#### 2. Embedding Inversion

Stored embeddings can be inverted to recover source text. Attacks on popular sentence embeddings recover roughly 50–70% of input words (Song & Raghunathan, 2020), and Vec2Text reconstructs 92% of short 32-token inputs exactly by training an inversion model per encoder (Morris et al., 2023). ZSInvert (C. Zhang et al., 2025) and Zero2Text (Kim et al., 2026) operate zero-shot with no encoder-specific training and work in black-box settings, and Zero2Text reports that standard defenses such as differential privacy fail to mitigate the attack. Operationally, vector-database backups, embeddings shipped to third-party services, and embeddings exposed through misconfigured cloud storage should be treated as potentially equivalent to exposure of the underlying documents. Under GDPR and similar regimes, breach notification depends on risk to data subjects, and because modern embeddings are frequently invertible, that risk cannot be assumed away.

#### 3. Retrieval-Time Data Poisoning

An attacker who can write to the corpus, through public scraping pipelines, file uploads, partner feeds, or compromised internal sources, can craft content whose embedding lands close to a target query. When a user submits that query, the attacker's content is retrieved and fed to the LLM as trusted context. Published attacks reliably achieve high success rates with a handful of poisoned documents, even in corpora of millions and against black-box systems (W. Zou et al., 2025). A successful attack requires two conditions simultaneously: the poisoned content must be retrieved (geometric) and must steer the response (generation). Defenders can intervene at either layer. MITRE ATLAS catalogs this class as AML.T0070 (RAG Poisoning) under the Persistence tactic. Training-time poisoning of the embedding model itself is covered in LLM05:2026.

#### 4. Retrieval Jamming

Attackers can take a RAG system off the air by inserting a "blocker" document, content engineered to be retrieved for a specific query and to cause the LLM to refuse to answer or claim it lacks information. Unlike poisoning, the blocker carries no malicious instructions. It exploits retrieval mechanics and LLM safety behavior. A single blocker document, generated through black-box optimization without access to the target embedding model or LLM, is sufficient (Shafran et al., 2025). This is an availability attack on the retrieval layer.

#### 5. Membership Inference via Similarity Search

The attacker wants to know whether a specific document (a medical record, a legal filing, an HR complaint) exists in the index, not what it says. If the application returns raw similarity scores or distances to the client, the index becomes a direct membership oracle with no LLM involved. If it returns only generated answers, the attacker can still infer membership by submitting partial documents or perturbed queries and analyzing responses. Membership information can itself be sensitive even when content remains protected.

#### 6. Semantic Cache and Deduplication Poisoning

Semantic caches and near-duplicate detection use a cosine-similarity threshold to decide two pieces of content are "the same." An attacker who can craft content landing just above or below that threshold can poison a cache entry so it serves attacker text to all semantically equivalent queries, bypass deduplication with near-duplicates of poisoned content, or force legitimate new content to be silently dropped as a duplicate. Wu et al. (2026) demonstrate semantic cache poisoning end-to-end across AWS, Azure, and Alibaba deployments. Z. Zhang et al. (2026) show black-box key-collision attacks that use surrogate embedding models to engineer threshold-straddling vectors without access to the target encoder. All three failure modes depend on embedding-space geometry and are invisible to document-level controls.

#### 7. Multimodal Embedding Poisoning

Cross-modal encoders such as CLIP and ColPali map images, audio, code, and text into one vector space. An attacker who can contribute non-text content can craft an image whose embedding sits close to a sensitive text query. When a user submits that query, the image is retrieved as trusted context. MM-PoisonRAG (Ha et al., 2025) and Poisoned-MRAG (Liu et al., 2025) demonstrate local and global poisoning across multimodal RAG pipelines, and "One Pic is All it Takes" (Shereen et al., 2025) shows a single image suffices for targeted and universal VD-RAG poisoning. To a human reviewer the image appears unremarkable, and text-based content scanning does not catch it because the payload is not text.

### Prevention and Mitigation Strategies

#### 1. Permission and Access Control

Enforce tenant scoping inside the index query, not as a post-retrieval filter, and validate it server-side. A client-supplied scope is a suggestion, not a control. Authenticate embedding and similarity-search endpoints as first-class APIs with per-tenant rate limits. For high-sensitivity workloads, use physically separated indexes per tenant or trust zone. Apply access control at the chunk level: a mostly-public document can contain a confidential paragraph.

#### 2. Data Validation, Source Authentication, and Provenance

Normalize content before embedding: strip zero-width characters, white-on-white text, and Unicode homoglyphs at extraction. Track provenance for every embedding (source, ingestion time, trust tier, pipeline version) so compromised batches can be invalidated and audited. Apply human review to externally sourced content destined for sensitive indexes. Vet the embedding model itself, because a backdoored encoder corrupts the geometry of everything ingested.

#### 3. Data Segregation by Trust Tier

Mixed-trust content (external web data, internal confidential documents, partner data) must not share an index without hard isolation. For high-sensitivity or high-assurance workloads, use separate indexes per trust tier rather than classification tags on a shared index, which removes the misconfiguration path at the cost of added operational overhead.

#### 4. Anomaly Detection at Ingest and Retrieval

Flag new vectors that sit unusually close to a wide range of common queries, the signature of retrieval-hijacking poisoning. Watch for queries returning too many high-similarity matches, unusual volume on embedding endpoints (a precursor to query-based inversion), and clusters growing faster than expected after ingest. Do not return raw similarity scores to clients, and rate-limit endpoints that could be queried as oracles. Cross-encoder re-ranking raises attack cost but does not replace provenance and ingest controls, because modern attacks target retrieval and ranking jointly.

#### 5. Storage Lifecycle Controls

Delete embeddings within a bounded time when the source document is deleted, and verify with reconciliation audits. Treat vector-database backups at the same sensitivity tier as source documents. Encrypt embeddings at rest with keys managed separately from the application layer. When rotating the embedding model, re-embed the corpus rather than mixing old and new vectors, because heterogeneous embeddings create exploitable gaps in similarity behavior. Treat embedding-API keys as secrets, since a leaked key gives an attacker query access to the exact encoder.

#### 6. Monitoring, Logging, and Incident Response

Keep immutable logs of retrieval activity (tenant scope, query, returned IDs, similarity scores). Monitor for tenant-filter bypass attempts, cross-tenant retrieval anomalies, and abnormal embedding-API consumption. Update incident-response playbooks so "embeddings only" leaks are assessed as potential source-data leaks for breach assessment and notification under GDPR Article 33 and analogous regimes.

### Example Attack Scenarios

#### Scenario #1: Embedding Similarity Attack on a Public Ingestion Pipeline

A company's RAG system scrapes public documentation and forum posts on a schedule. An attacker publishes posts engineered so their embeddings land near specific internal queries, such as "what is our Q3 revenue projection." When an employee asks that question, the attacker's content is retrieved and fed to the LLM. The same text pasted into a chat would have no effect. The attack works only because the attacker can place content near a target query in embedding space.

#### Scenario #2: Cross-Tenant Inference in a Shared Vector Index

A multi-tenant SaaS product uses one shared vector index with tenant filtering at the application layer. Tenant A submits probing queries, and similarity search runs across every embedding, including Tenant B's, before the filter is applied. A never sees B's documents, but where the index exposes them, timing differences, result counts, and score-distribution gaps can reveal the existence and approximate topic of B's content. Over many queries, A builds a useful map of B's data.

#### Scenario #3: Embedding Inversion from a Leaked Vector Store

A cloud misconfiguration exposes a backup of a production vector database. The underlying documents (customer conversation logs containing PII) are encrypted separately and not exposed, so the incident is initially classified as low-severity: "only the embeddings leaked." The attacker runs a zero-shot inversion attack against the stolen embeddings and reconstructs a substantial fraction of the source content, including PII, without access to the original encoder. The incident is reclassified as equivalent to a source-document breach and notification obligations are reassessed. "Embeddings only" is not a safe-harbor classification.
