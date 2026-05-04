## Inference-Time Side-Channel Disclosure

### Description

Modern LLM serving infrastructure uses speculative decoding and streaming token emission to optimize throughput and latency. These optimizations produce observable, input-dependent patterns in network packet sizes and response timing. An adversary with passive network visibility between a client and an inference server can measure these patterns and recover private information without interacting with the model, without decrypting any payload, and without triggering any application-layer security control. Affected deployments include any LLM served over a network where an on-path observer can collect packet-size or timing metadata: shared cloud tenancy, co-located infrastructure, and network segments accessible to traffic inspection. Published research demonstrated query-topic fingerprinting accuracy exceeding 90% and retrieval-datastore content exfiltration at rates above 25 tokens per second against production inference frameworks.

### Common Examples of Risk

1. Query-topic fingerprinting: an observer classifies the subject matter of user queries (medical, legal, financial, security-related) by measuring the speculative-decoding accept/reject rhythm in network packet metadata, without reading any encrypted payload.
2. System prompt reconstruction: an observer uses timing differences produced by speculative decoding to binary-search the token sequence of a confidential system prompt, recovering it incrementally without any direct model access.
3. RAG datastore content leakage: an observer exploits speculative-decoding accept-rate variations in an LLM with a confidential retrieval datastore to recover datastore contents at measurable token-per-second rates, bypassing all access controls on the datastore itself.

### Prevention and Mitigation Strategies

1. Packet-size normalization: pad all inference API responses to a fixed packet size at the MTU boundary before transmission, and apply iteration-wise token aggregation so responses are delivered in fixed-size batches rather than as individual token emissions. Both controls eliminate the size-variation signal that side-channel classifiers require.
2. Constant-time response delivery for sensitive deployments: configure the inference serving layer to deliver responses at fixed time intervals independent of internal token generation cadence. Disable or restrict streaming APIs in deployments where query-topic correlation via timing presents an unacceptable risk, including healthcare, legal, financial, and government classified environments.
3. Inference infrastructure threat modeling: apply the same adversarial analysis to LLM serving systems that conventional application security applies to database query timing oracles. Require TLS with traffic shaping on all inference API connections. Classify co-tenant visibility on shared cloud inference platforms as a confidentiality risk requiring explicit acceptance.

### Example Attack Scenarios

**Scenario #1: Query-topic fingerprinting via speculative decoding packet analysis**

A financial services company runs a customer LLM assistant on a multi-tenant cloud inference platform using vLLM with speculative decoding enabled. An attacker operating as a co-tenant on the same physical host monitors network metadata at the hypervisor layer. No application traffic is decrypted.

Steps:

1. The attacker captures a packet-size time series for 48 hours of inference traffic from the target tenant's endpoint.
2. The attacker constructs a labeled training set by sending known queries -- account balance inquiries, fraud dispute descriptions, loan application questions -- through a separate test endpoint on the same infrastructure and recording the resulting packet-size and timing signatures.
3. The attacker trains a query-topic classifier on the labeled set. The classifier uses the accept/reject rhythm of speculative decoding iterations as its primary feature: accepted draft tokens produce smaller correction packets; rejected drafts produce larger regeneration packets, with distributions that vary by query topic.
4. The classifier is applied to the live traffic capture and achieves greater than 90% accuracy in identifying whether a given user session involves account balance queries, fraud disputes, or loan applications.
5. The attacker uses the classified session metadata to construct targeted phishing messages for identified high-value users -- without decrypting a single payload packet or interacting with the application.

**Scenario #2: System prompt reconstruction via timing oracle**

An attacker has read access to round-trip time (RTT) measurements between a client and an LLM inference server using speculative decoding. All HTTP payloads are encrypted.

Steps:

1. The attacker sends a series of completion requests with varying prefix strings using a monitored account, each with a different candidate token at position n.
2. When the prefix matches the actual system prompt content at position n, the speculative draft tokens are accepted at a higher rate, producing lower RTT. When the prefix does not match, drafts are rejected and regenerated, producing higher RTT.
3. The attacker performs a binary search over the token vocabulary at each position, using RTT as an oracle signal. For a vocabulary of 50,000 tokens, 17 probes per position distinguish the correct token.
4. At a recovery rate of 25 tokens per second, a 500-token system prompt requires 20 seconds. A 2,000-token system prompt requires under 90 seconds.
5. The recovered system prompt contains proprietary business logic, internal API endpoints, user data access patterns, and any credentials embedded by the application developer.

The attack requires no exploit of the application, no elevated network access, and no model credentials -- only the ability to measure RTT to the inference endpoint.

### Reference Links

1. [When Speculation Spills Secrets: Side Channels via Speculative Decoding in LLMs](https://openreview.net/forum?id=zq40cmz1JD): **OpenReview** (Wei, Abdulrazzag, Zhang, Muursepp, Saileshwar, 2025; ICLR 2026 submission)
2. [Timing Side Channels via Output Token Count](https://security.csl.toronto.edu/wp-content/uploads/2025/08/tzhang_mascthesis_2025.pdf): **University of Toronto** (Zhang, T., M.Sc. thesis, 2025)
3. [Whisper Leak: A Novel Side-Channel Cyberattack on Remote Language Models](https://www.microsoft.com/en-us/security/blog/2025/11/07/whisper-leak-a-novel-side-channel-cyberattack-on-remote-language-models): **Microsoft Security Blog**
4. [Unveiling Timing Side Channels in LLM Serving Systems](https://ieeexplore.ieee.org/document/11206380/): **IEEE**
5. [Side Channels via Speculative Decoding in LLMs](https://arxiv.org/abs/2411.01076): **arXiv** (2024; cite as: arXiv:2411.01076)
