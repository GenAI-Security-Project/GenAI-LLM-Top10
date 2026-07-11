# Appendix A: Related Framework Mappings

This appendix consolidates the mappings from the ten OWASP Top 10 for LLM Applications (2026) risk entries to nine external security frameworks and taxonomies. It replaces the per-entry *Related Frameworks and Taxonomies* sections, which have been removed in favor of this single, version-pinned reference.

## How to read this appendix

The **coverage matrix** shows, at a glance, which frameworks map to each risk. The **by-framework sections** give the specific element mappings and why they apply. Mappings are at each framework's coarse level (tactics, pillars/weaknesses, risk categories, control domains); every element is drawn from the pinned framework version listed in **Framework Sources & Versions**. Each cell shows the primary mappings plus the most relevant supporting ones.

**Legend:** ● primary (a central line of defense or description of the risk) · ○ supporting (contributes but is not the center of gravity) · — no applicable mapping.

## Coverage matrix

| Risk | ASI | DSGAI | ATLAS | ATT&CK | CWE | 600-1 | RMF | AICM | AIVSS |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **LLM01** Prompt Injection | ● | ● | ● | ● | ● | ● | ○ | ● | ● |
| **LLM02** Sensitive Information Disclosure | ● | ● | ● | ● | ● | ● | ○ | ● | — |
| **LLM03** Excessive Agency | ● | ● | ● | ● | ● | ● | ○ | ● | ● |
| **LLM04** Supply Chain | ● | ● | ● | ● | ● | ● | ● | ● | ○ |
| **LLM05** Data and Model Poisoning | ● | ● | ● | ○ | ● | ● | ○ | ● | ○ |
| **LLM06** Unbounded Consumption | ● | ● | ● | ● | ● | ● | ○ | ● | ○ |
| **LLM07** Misinformation | ● | ● | ● | ○ | ● | ● | ● | ● | ● |
| **LLM08** Hidden Context Exposure | ● | ○ | ● | ○ | ● | ● | ○ | ● | ○ |
| **LLM09** Vector and Embedding Weaknesses | ● | ● | ● | ○ | ● | ● | ○ | ● | ○ |
| **LLM10** Improper Output Handling | ● | ● | ● | ● | ● | ● | — | ● | ○ |

## OWASP Top 10 for Agentic Applications (ASI) — 2026 (announced 2025-12-09)

*Relocated verbatim from the 2026 entries; maps each LLM risk to the OWASP Top 10 for Agentic Applications (ASI) risks.*

| Risk | Element | Relevance |
|---|---|---|
| **LLM01** Prompt Injection | ● ASI01 — Agent Goal Hijack | Injected input overrides the system-prompt role/capability constraints, redirecting agent goals. |
|  | ● ASI02 — Tool Misuse & Exploitation | Injected input drives unauthorized tool invocation (the "lethal trifecta" conditions). |
|  | ● ASI03 — Identity & Privilege Abuse | Agent acts under the user's elevated credentials, performing actions the attacker could not. |
|  | ● ASI05 — Unexpected Code Execution (RCE) | Shell / file-system / cloud-API access turns injection into arbitrary command execution. |
|  | ● ASI06 — Memory & Context Poisoning | Memory and RAG poisoning taint every future session reading the store. |
|  | ● ASI08 — Cascading Failures | Tool outputs re-enter the context window, enabling chained or self-replicating effects. |
|  | ● ASI09 — Human-Agent Trust Exploitation | Injection bypasses human-in-the-loop confirmation. |
| **LLM02** Sensitive Information Disclosure | ● ASI06 — Memory & Context Poisoning | Persistent agent memory corruption leading to cross-session data leakage |
| **LLM03** Excessive Agency | ● ASI01 — Agent Goal Hijack | Prompt injection or hallucination diverting an agent from its intended task is the trigger mechanism for Excessive Agency ("hallucination/confabulation... or direct/indirect prompt injection") |
|  | ● ASI02 — Tool Misuse & Exploitation | A manifestation of Excessive Agency, where extensions/tools carry functionality beyond what the task needs |
|  | ● ASI03 — Identity & Privilege Abuse | A manifestation of Excessive Agency, where extensions connect with generic, over-privileged identities |
|  | ● ASI05 — Unexpected Code Execution (RCE) | A shell-command extension that fails to filter out unintended commands, and a coding agent whose excessive autonomy and permissions destroyed production infrastructure |
|  | ● ASI07 — Insecure Inter-Agent Communication | A malicious/compromised peer agent in multi-agent/collaborative systems is a trigger, and user authorization scope must be preserved "across chained extension or agent calls" |
|  | ● ASI08 — Cascading Failures | A manifestation of Excessive Agency, countered by rate limiting and circuit breakers to halt runaway extension invocation |
|  | ● ASI09 — Human-Agent Trust Exploitation | Excessive autonomy (failing to seek confirmation before high-impact actions) and human-in-the-loop approval both concern trust placed in unsupervised agent action |
| **LLM04** Supply Chain | ● ASI04 — Agentic Supply Chain Vulnerabilities | This entry's own scope note defers agentic-specific supply-chain risk to ASI04, leaving this entry to cover the non-agentic model, dataset, and artifact supply chain |
| **LLM05** Data and Model Poisoning | ● ASI04 — Agentic Supply Chain Vulnerabilities | Poisoned pre-trained models and malicious deserialization distributed via public repositories, and tampered inference-time artifacts such as chat templates/GGUF |
|  | ● ASI06 — Memory & Context Poisoning | Persistent agent memory and recommendation poisoning, and long-term manipulation of agent decisions via injected memory |
|  | ● ASI08 — Cascading Failures | Poisoned inputs propagating across multi-agent and enterprise workflows into unintended data exposure, and cross-tenant contamination via shared embeddings/memory |
| **LLM06** Unbounded Consumption | ● ASI02 — Tool Misuse & Exploitation | Agent-tool interaction loops and MCP tool-call fan-out let a single request drive recursive or high-volume tool calls that exhaust budget and availability |
|  | ● ASI08 — Cascading Failures | Agentic architectures and tool-use protocols such as MCP "amplify a single request into cascading downstream operations," illustrated by the fan-out of one task into 50 calls |
| **LLM07** Misinformation | ● ASI08 — Cascading Failures | Incorrect state or evidence produced by one agent and trusted by another propagates misinformation across a multi-agent workflow into a compounding, high-impact failure (Cross-Agent Misinformation Propagation; Cross-Agent Trust Failure) |
|  | ● ASI09 — Human-Agent Trust Exploitation | Humans and downstream systems that treat fluent, confident model output as authoritative are the exploited trust surface this entry's overreliance framing describes (Unsupported or False Decision Support) |
|  | ● ASI10 — Rogue Agents | An agent that falsifies task completion or fabricates evidence to mislead downstream trust matches this entry's forged-evidence and false-completion failure modes (Forged or Misattributed Evidence; Fabricated Task Completion) |
| **LLM08** Hidden Context Exposure | ● ASI06 — Memory & Context Poisoning | LLM08's scope explicitly defers "the agentic amplifications of this risk, e.g., persistent memory, inter-agent channels, tool configuration persistence, and multi-step agent compromise" to the OWASP Top 10 for Agentic Applications; ASI06 is the pointer for persistent-memory poisoning building on exposed hidden context, not an equivalent risk. |
|  | ● ASI07 — Insecure Inter-Agent Communication | Same scope carve-out names "inter-agent channels" as an out-of-scope amplification; ASI07 is the pointer for hidden-context material propagating across agent-to-agent messaging, not an equivalent risk. |
| **LLM09** Vector and Embedding Weaknesses | ● ASI04 — Agentic Supply Chain Vulnerabilities | Embedding-model supply chain: the embedding model itself must be vetted, since "a backdoored embedding model corrupts the geometry of everything ingested" |
|  | ● ASI06 — Memory & Context Poisoning | Agent-memory poisoning that does not rely on embedding geometry is out of scope here and referred to ASI06 |
| **LLM10** Improper Output Handling | ● ASI02 — Tool Misuse & Exploitation | 2026 addition, justified against this entry's own content: a general-purpose LLM passes its response to a privileged extension without output validation, causing the extension to be misused and shut down. |
|  | ● ASI05 — Unexpected Code Execution (RCE) | Foundational crosswalk mapping; matches this entry's core risk of unvalidated LLM output reaching a shell, `exec`, or `eval`, resulting in remote code execution. |
|  | ● ASI09 — Human-Agent Trust Exploitation | Canonical crosswalk baseline mapping — ASI09 lists Improper Output Handling as a contributing LLM risk. The content match is loose: this entry's scenarios are machine-to-machine (unvalidated output reaching a shell, browser, or database), while ASI09 concerns deceiving a human operator; the shared thread is unvalidated model output reaching a downstream trust decision. |

## OWASP GenAI Data Security 2026 (DSGAI) — v1.0 (2026-03-17)

*Each row maps an LLM Top 10 risk to OWASP GenAI Data Security 2026 (DSGAI) risk categories, where primary elements name the closest data-security peer and supporting elements name the most relevant adjacent data risks.*

| Risk | Element | Relevance |
|---|---|---|
| **LLM01** Prompt Injection | ● DSGAI01 — Sensitive Data Leakage | A successful injection makes disclosure and exfiltration the dominant outcome, spilling system-prompt content, retrieved private documents, and infrastructure details out of the model. |
|  | ● DSGAI06 — Tool, Plugin & Agent Data Exchange Risks | Injection rides through MCP servers and third-party tool packages, where poisoned tool descriptions and unpinned connections let a compromised model act across connected systems. |
|  | ○ DSGAI09 — Multimodal Capture & Cross-Channel Data Leakage | Steganographic image and invisible-Unicode payloads deliver instructions the human never sees, and markdown image-URL rendering carries the stolen data back out. |
|  | ○ DSGAI16 — Endpoint & Browser Assistant Overreach | Browser, IDE, and email assistants that auto-summarize untrusted pages become the indirect-injection channel, from zero-click document exfiltration to a flipped IDE configuration flag. |
|  | ○ DSGAI04 — Data, Model & Artifact Poisoning | One tainted entry in a RAG corpus or persistent memory taints every later session that reads it, making poisoning a cross-session propagation path for injection. |
| **LLM02** Sensitive Information Disclosure | ● DSGAI01 — Sensitive Data Leakage | The direct peer: unauthorized exposure of confidential, regulated, or proprietary data through any output channel is the whole risk. |
|  | ● DSGAI18 — Inference & Data Reconstruction | Membership inference, embedding inversion, and internal-state inversion reconstruct protected data from measurable model behavior without receiving the content directly. |
|  | ○ DSGAI15 — Over-Broad Context Windows & Prompt Over-Sharing | Unscoped drives, legacy permissions, and auto-appended full records feed the model more sensitive data than the task needs, the upstream over-sharing that drives most incidents. |
|  | ○ DSGAI08 — Non-Compliance & Regulatory Violations | The disclosure carries the regulatory consequence, triggering EU AI Act, GDPR, HIPAA, and CCPA obligations and their breach-notification clocks. |
|  | ○ DSGAI14 — Excessive Telemetry & Monitoring Leakage | Observability platforms log full prompts, completions, retrieved chunks, and reasoning traces by default, exposing sensitive content to anyone with dashboard access. |
| **LLM03** Excessive Agency | ● DSGAI02 — Agent Identity & Credential Exposure | Extensions granted broad write access or a shared high-privilege account let a hijacked agent act far beyond its intended scope, so binding actions to user-scoped credentials across chained calls is the core control. |
|  | ● DSGAI06 — Tool, Plugin & Agent Data Exchange Risks | The whole risk concerns extensions, tools, and plugins that retain unneeded capabilities an attacker can trigger, such as a mail extension that keeps its send function. |
|  | ○ DSGAI01 — Sensitive Data Leakage | Excess agency lets a compromised agent scan a mailbox for sensitive information and forward it to an attacker. |
| **LLM04** Supply Chain | ● DSGAI04 — Data, Model & Artifact Poisoning | Tampered or backdoored models, adapters, and artifacts enter the pipeline through the supply chain, as with a maliciously edited open model or a poisoned format-conversion service. |
|  | ● DSGAI05 — Data Integrity & Validation Failures | Unsigned, unverified artifacts and mutable references resolved at build or promotion time let tampered components pass without integrity checks or signing. |
|  | ○ DSGAI03 — Shadow AI & Unsanctioned Data Flows | Unclear supplier terms can silently route application data into a provider's training set, so vetting supplier terms and privacy policies is required. |
|  | ○ DSGAI08 — Non-Compliance & Regulatory Violations | Unclear model and dataset licensing and copyright status create legal and compliance exposure that demands license tracking and auditing. |
| **LLM05** Data and Model Poisoning | ● DSGAI04 — Data, Model & Artifact Poisoning | The direct peer covering poisoning across pre-training, fine-tuning, embeddings, RAG, transfer learning, and distributed non-weight artifacts. |
|  | ○ DSGAI05 — Data Integrity & Validation Failures | Strict, continuous validation of training and retraining inputs is the front-line defense against injected poison. |
|  | ○ DSGAI21 — Disinformation & Integrity Attacks via Data Poisoning | Poisoning a knowledge base surfaces adversary-controlled content as authoritative output, an integrity attack driven by corrupted data. |
|  | ○ DSGAI07 — Data Governance, Lifecycle & Classification | Dataset and model lineage tracked through an SBOM or ML-BOM plus version history enables rollback and forensics after a poisoning event. |
| **LLM06** Unbounded Consumption | ● DSGAI20 — Model Exfiltration & IP Replication | Functional model cloning and extraction through high-volume querying steal the model's intellectual property. |
|  | ● DSGAI17 — Data Availability & Resilience Failures in AI Pipelines | Resource-exhausting requests and output-explosion attacks render the service unresponsive, the availability failure that resilience controls target. |
|  | ○ DSGAI04 — Data, Model & Artifact Poisoning | A single poisoned fine-tuning sample can break end-of-sequence behavior and drive runaway output generation as a denial-of-service vector. |
| **LLM07** Misinformation | ● DSGAI21 — Disinformation & Integrity Attacks via Data Poisoning | Deliberately injected content makes the system surface false or forged material as authoritative, the core disinformation-via-poisoning mechanism. |
|  | ○ DSGAI05 — Data Integrity & Validation Failures | Biased or corrupted source data and unvalidated ingestion are root causes that let misinformation enter and spread. |
|  | ○ DSGAI06 — Tool, Plugin & Agent Data Exchange Risks | Unvalidated tool outputs and cross-agent exchange propagate false information, so tool calls need semantic validation. |
| **LLM08** Hidden Context Exposure | ○ DSGAI18 — Inference & Data Reconstruction | The entry is defined by extraction, inference, and reconstruction of hidden context, the same reconstruction attacks that recover a system prompt from model behavior. |
|  | ○ DSGAI15 — Over-Broad Context Windows & Prompt Over-Sharing | The central preventive principle is to keep sensitive data out of hidden context and assume all context is discoverable. |
|  | ○ DSGAI02 — Agent Identity & Credential Exposure | API keys and tokens embedded in hidden context are harvested once an attacker extracts that context. |
| **LLM09** Vector and Embedding Weaknesses | ● DSGAI13 — Vector Store Platform Data Security | Vector-store platform security is the entry's literal subject, covering encryption, access control, and export limits on embedding stores. |
|  | ● DSGAI18 — Inference & Data Reconstruction | Embedding inversion that reconstructs plaintext and membership-inference oracles turn stored vectors back into their source data. |
|  | ○ DSGAI11 — Cross-Context & Multi-User Conversation Bleed | Shared similarity search that applies the tenant filter only after retrieval leaks one tenant's chunks into another's results. |
|  | ○ DSGAI04 — Data, Model & Artifact Poisoning | Retrieval-time poisoning, semantic-cache poisoning, and multimodal embedding poisoning steer the system to attacker-controlled content. |
|  | ○ DSGAI17 — Data Availability & Resilience Failures in AI Pipelines | A single crafted blocker document can dominate retrieval and take the RAG system off the air, an availability attack on the retrieval layer. |
| **LLM10** Improper Output Handling | ● DSGAI12 — Unsafe Natural-Language Data Gateways (LLM-to-SQL/Graph) | LLM-generated SQL executed without parameterization or scrutiny reaches the database directly and can delete entire tables. |
|  | ○ DSGAI06 — Tool, Plugin & Agent Data Exchange Risks | Unvalidated model output crosses into a downstream tool or extension for execution. |
|  | ○ DSGAI01 — Sensitive Data Leakage | Unescaped output rendered by a client encodes and sends conversation data to an attacker-controlled server, as in image-URL exfiltration. |
|  | ○ DSGAI16 — Endpoint & Browser Assistant Overreach | Client renderers such as chat UIs, IDEs, and email clients auto-fetch external resources from raw model output, executing the exfiltration. |

## MITRE ATLAS — content v2026.06 (format-version 6.0.0)

*Read each row as an OWASP LLM risk mapped to the MITRE ATLAS adversary tactics (AML.TAxxxx) an attack exploiting it traverses, where primary tactics carry the core adversary objective and supporting tactics the enabling steps.*

| Risk | Element | Relevance |
|---|---|---|
| **LLM01** Prompt Injection | ● AML.TA0004 Initial Access | Injected instructions, whether typed directly into the prompt or hidden in content the model later retrieves, are the foothold that lets an attacker seize control of the model's behavior. |
|  | ● AML.TA0005 Execution | A successful injection drives the agent to invoke tools and run adversary-chosen commands, including arbitrary code execution on the host. |
|  | ● AML.TA0006 Persistence | Injected instructions written into long-term memory or a retrieval corpus survive across sessions and re-fire whenever the poisoned entry is recalled. |
|  | ● AML.TA0007 Defense Evasion | Attackers hide the injection with invisible Unicode, Base64 or ROT13 encoding, and low-resource languages, and use jailbreak phrasing to slip past safety filters. |
|  | ● AML.TA0010 Exfiltration | Injection redirects the model to leak private conversation, database, or repository contents through image-URL, tool, or invisible-character channels. |
|  | ○ AML.TA0001 AI Attack Staging | Adversaries optimize the injection payload in advance, using gradient-oracle fine-tuning and payload-splitting to raise attack success rates. |
|  | ○ AML.TA0011 Impact | A runtime injection can trigger destructive action, such as wiping a developer's local files. |
|  | ○ AML.TA0012 Privilege Escalation | An injected agent running on a trusted backend acts under the user's elevated credentials, yielding access beyond the attacker's own rights. |
| **LLM02** Sensitive Information Disclosure | ● AML.TA0010 Exfiltration | Membership inference, model inversion, model extraction, and API-based data theft all move protected data out of the system, sometimes through covert DNS or image channels. |
|  | ○ AML.TA0013 Credential Access | An embedded vendor API key placed in the system prompt can be coaxed out of the model, exposing a live credential. |
|  | ○ AML.TA0000 AI Model Access | Extraction, membership inference, and inversion run offline at unbounded rates against open-weights deployments, so the access mode itself is the attack surface. |
|  | ○ AML.TA0007 Defense Evasion | Cross-lingual, Base64, and hex encodings defeat regex and blocklist data-loss filters, and cross-modal transformation slips data past single-modality inspection. |
| **LLM03** Excessive Agency | ● AML.TA0005 Execution | An over-broad extension, such as one that runs unfiltered shell commands, lets the agent execute damaging operations, including destructive commands against production systems. |
|  | ● AML.TA0011 Impact | Excessive permissions turn an agent action into confidentiality, integrity, and availability harm, from deleting a user's email to destroying production databases and their snapshots. |
|  | ○ AML.TA0010 Exfiltration | An indirect injection can make an over-permissioned mail extension forward sensitive inbox contents to an attacker-controlled address. |
|  | ○ AML.TA0012 Privilege Escalation | A confused-deputy or weaponized over-privileged agent lets an attacker act with the agent's standing high privileges. |
| **LLM04** Supply Chain | ● AML.TA0004 Initial Access | Compromised models, packages, adapters, and training pipelines are the foothold by which a tampered artifact enters the victim's environment. |
|  | ○ AML.TA0003 Resource Development | Attackers publish tampered models, pre-register confabulated (slopsquatted) package names, and re-register abandoned namespaces to stage malicious dependencies. |
|  | ○ AML.TA0005 Execution | Malicious model manifests, pickle deserialization, and format-parser overflows yield remote code execution when an artifact is loaded. |
|  | ○ AML.TA0006 Persistence | A backdoor embedded in a LoRA adapter or a model's computational graph survives in the deployed model, in a format that looks safe. |
| **LLM05** Data and Model Poisoning | ● AML.TA0003 Resource Development | Adversaries publish poisoned datasets and models and inject tainted samples into training data that others will consume. |
|  | ● AML.TA0006 Persistence | Backdoors and sleeper triggers survive safety alignment and retraining, staying dormant in the model until a specific input activates them. |
|  | ● AML.TA0011 Impact | Poisoning erodes model and dataset integrity, degrading accuracy, weakening refusals, and steering the model toward harmful outputs. |
|  | ○ AML.TA0004 Initial Access | Organizations that pull compromised models or datasets from public repositories inherit the hidden triggers along with the artifact. |
|  | ○ AML.TA0001 AI Attack Staging | The attacker backdoors the model and crafts trigger or adversarial data before the model is deployed. |
|  | ○ AML.TA0005 Execution | Loading an unsafe artifact executes attacker code, as with pickle deserialization on model load or chat-template injection in a model file. |
| **LLM06** Unbounded Consumption | ● AML.TA0011 Impact | Input floods deny the ML service to legitimate users, and cost-harvesting attacks run up the victim's bill in a denial-of-wallet. |
|  | ● AML.TA0010 Exfiltration | Crafted API queries and side-channel weight harvesting extract the model, stealing the intellectual property embodied in its parameters. |
|  | ○ AML.TA0000 AI Model Access | Both extraction and resource-exhaustion attacks operate through inference-API access, which is the prerequisite for the technique. |
| **LLM07** Misinformation | ● AML.TA0011 Impact | False output that is trusted and acted upon causes financial loss, security incidents, safety risks, and operational disruption, as when a fabricated alert derails operations. |
|  | ○ AML.TA0003 Resource Development | Attackers publish malicious packages under names the model is known to hallucinate, staging a supply-chain trap keyed to the confabulation. |
|  | ○ AML.TA0004 Initial Access | A hallucinated dependency, once recommended and installed by a trusting developer, becomes an AI supply-chain foothold. |
|  | ○ AML.TA0001 AI Attack Staging | Adversaries craft inputs that steer the model toward specific false claims, an induced-misinformation staging step. |
| **LLM08** Hidden Context Exposure | ● AML.TA0008 Discovery | The attack extracts and reconstructs the system prompt, tool list, roles, and refusal logic, discovering the AI system's hidden configuration. |
|  | ● AML.TA0010 Exfiltration | Leaking that hidden context across the trust boundary is model data leakage, moving configuration the operator meant to keep private into the attacker's hands. |
|  | ○ AML.TA0002 Reconnaissance | Extracted context gives the attacker concrete targets for follow-on prompt injection and reconnaissance for downstream action chaining. |
|  | ○ AML.TA0013 Credential Access | Credentials embedded in the system prompt are obtained when the hidden context leaks, handing the attacker usable secrets. |
| **LLM09** Vector and Embedding Weaknesses | ● AML.TA0006 Persistence | Poisoned corpus and cache entries stay in the vector store and re-trigger on matching queries, a durable foothold in the retrieval layer. |
|  | ● AML.TA0010 Exfiltration | Embedding inversion, cross-tenant inference, and membership inference pull private data and documents out through the shared index. |
|  | ○ AML.TA0001 AI Attack Staging | Attackers craft content whose embedding lands near a target query and use surrogate encoders to engineer threshold-straddling vectors. |
|  | ○ AML.TA0011 Impact | Retrieval jamming floods the index as an availability attack, and retrieval poisoning erodes the integrity of returned answers. |
|  | ○ AML.TA0008 Discovery | Cross-tenant probing infers the existence, topic, and rough volume of other tenants' documents, and membership inference reveals whether a specific document is indexed. |
| **LLM10** Improper Output Handling | ● AML.TA0005 Execution | Unvalidated model output passed to a shell, browser, or SQL interpreter executes adversary-controlled code, yielding command execution, cross-site scripting, or SQL injection. |
|  | ○ AML.TA0010 Exfiltration | Model output encoded and sent to an attacker server, or embedded in a Markdown-image URL, carries sensitive data out of the application. |
|  | ○ AML.TA0011 Impact | Unhandled output reaching a privileged sink can delete database tables or force a downstream service offline. |
|  | ○ AML.TA0012 Privilege Escalation | When the model holds privileges beyond the end user, unvalidated output reaching a privileged sink escalates those privileges to the attacker. |

## MITRE ATT&CK — v19.1

*Each row maps an OWASP LLM risk to the MITRE ATT&CK v19.1 Enterprise tactics (TA IDs) an adversary traverses when exploiting it, with primary tactics marking the risk's central attack objective and supporting tactics the adjacent stages.*

| Risk | Element | Relevance |
|---|---|---|
| **LLM01** Prompt Injection | ● TA0001 Initial Access | A compromised IDE extension and a malicious MCP npm package deliver injected instructions into the model's context, making the software supply chain the entry point for the attack. |
|  | ○ TA0002 Execution | Injected instructions drive arbitrary command execution and destructive actions on the host or connected systems through an agent's shell-tool access. |
|  | ○ TA0010 Exfiltration | Injected content exfiltrates data over covert channels such as markdown image URLs, hidden Unicode, and tool-logging side channels while the visible response stays benign. |
|  | ○ TA0005 Stealth | Attackers smuggle instructions past human and model review using zero-width and variation-selector Unicode, tag-block encoding, hidden page-source text, and sub-perceptual image steganography. |
| **LLM02** Sensitive Information Disclosure | ● TA0010 Exfiltration | A hidden markdown-image or webhook channel carries sensitive data outbound while the model's visible answer stays innocuous. |
|  | ○ TA0009 Collection | Side-channel observation of encrypted LLM traffic reconstructs conversation topics and token content, as in topic inference exceeding 98% AUPRC and token-length reconstruction. |
|  | ○ TA0006 Credential Access | Prompt injection prints a system prompt carrying an embedded vendor API key, and exposed logging stores leak API keys an adversary can harvest. |
| **LLM03** Excessive Agency | ● TA0002 Execution | An open-ended shell-command extension that fails to filter unintended commands lets an agent execute arbitrary code, as when a coding agent destroyed production infrastructure. |
|  | ● TA0040 Impact | Excessive autonomy leads to destructive actions such as deleting emails without confirmation or wiping a production database and years of snapshots. |
|  | ○ TA0010 Exfiltration | An indirect injection commands the agent to scan the user's inbox for sensitive information and forward it to an attacker's email address. |
|  | ○ TA0004 Privilege Escalation | Over-privileged or generic high-privilege agent identities and confused-deputy conditions raise the attacker's effective privilege to that of the agent. |
| **LLM04** Supply Chain | ● TA0001 Initial Access | Compromised packages and build pipelines, from a poisoned PyPI dependency to the xz-utils and Codecov compromises, deliver attacker code into the victim environment. |
|  | ○ TA0042 Resource Development | Attackers register malicious packages under hallucinated names (slopsquatting) and inject CI/CD caches to stage trojanized releases for distribution. |
|  | ○ TA0002 Execution | Malicious model manifests, namespace reuse, and pickle deserialization on model load produce remote code execution once the artifact is pulled and run. |
|  | ○ TA0003 Persistence | A merged LoRA adapter or backdoored model graph provides a covert entry point that survives across deployments and passes downstream provenance checks. |
| **LLM05** Data and Model Poisoning | ○ TA0040 Impact | Poisoned training data or weights manipulate model integrity to produce harmful or degraded outputs, such as bypassing fraud detection or dropping accuracy from 90% to 15% when a trigger fires. |
|  | ○ TA0001 Initial Access | Malicious models with embedded backdoors distributed through public repositories reach the victim when pulled into a pipeline. |
|  | ○ TA0002 Execution | Embedded malicious code executes during unsafe pickle model loading, and a tampered chat template carries trigger-activated instructions. |
| **LLM06** Unbounded Consumption | ● TA0040 Impact | Resource-exhausting inputs crash or slow the service and denial-of-wallet attacks harvest compute cost, disrupting availability and inflating spend. |
|  | ○ TA0010 Exfiltration | Model-extraction queries harvest model information to a remote resource under the attacker's control, enabling intellectual-property theft through cloning. |
| **LLM07** Misinformation | ○ TA0001 Initial Access | Attackers publish malicious packages under names that coding assistants hallucinate (slopsquatting), turning fabricated recommendations into a software supply-chain compromise. |
| **LLM08** Hidden Context Exposure | ○ TA0006 Credential Access | Hidden context such as system prompts holding API keys, database credentials, and user tokens leaks to an attacker who then reuses the exposed credentials. |
| **LLM09** Vector and Embedding Weaknesses | ○ TA0009 Collection | Cross-tenant probing of a shared vector index infers other tenants' data held in that information repository. |
|  | ○ TA0010 Exfiltration | Zero-shot embedding inversion reconstructs source documents and PII from a leaked embedding backup, taking data outside the boundary. |
|  | ○ TA0040 Impact | Retrieval jamming degrades availability of the retrieval layer and retrieval-time poisoning manipulates the context fed to the model. |
| **LLM10** Improper Output Handling | ● TA0002 Execution | Passing unvalidated model output into shell, eval, or database interfaces yields remote code execution, cross-site scripting, and SQL injection on backend systems. |
|  | ○ TA0010 Exfiltration | Model output encodes sensitive conversation data and sends it to an attacker-controlled server, including via markdown-image URLs. |
|  | ○ TA0040 Impact | Unscrutinized model-generated SQL deletes database tables and a privileged extension is driven to shut down, causing data destruction and loss of availability. |
|  | ○ TA0004 Privilege Escalation | When the application grants the model privileges beyond those intended for end users, unhandled output enables escalation of privileges. |

## MITRE CWE (Common Weakness Enumeration) — 4.20

*Each OWASP LLM Top 10 2026 entry maps to the CWE weaknesses that name its root cause, with primary CWEs capturing the definitional weakness and supporting CWEs the top contributing failure modes.*

| Risk | Element | Relevance |
|---|---|---|
| **LLM01** Prompt Injection | ● CWE-1427 Improper Neutralization of Input Used for LLM Prompting | Untrusted input from prompts, retrieved documents, tool output, or memory alters model behavior because the model draws no boundary between instructions and data, the definitional prompt-injection weakness. |
|  | ○ CWE-707 Improper Neutralization (Pillar) | The pillar-level root cause is a failure to separate and neutralize attacker instructions from data on a single token stream. |
|  | ○ CWE-349 Acceptance of Extraneous Untrusted Data With Trusted Data | Context-window pooling merges untrusted retrieved content and tool output with trusted instructions under no enforced trust boundary. |
|  | ○ CWE-693 Protection Mechanism Failure (Pillar) | Jailbreaks and adaptive guardrail evasion degrade prompt-injection classifiers and link filters, driving defenses to high adversarial success rates. |
| **LLM02** Sensitive Information Disclosure | ● CWE-200 Exposure of Sensitive Information to an Unauthorized Actor | The entry defines disclosure as exposing confidential, regulated, or privileged data through an unauthorized channel. |
|  | ● CWE-359 Exposure of Private Personal Information | PII and PHI disclosure sits at the center of the entry, anchored to GDPR and HIPAA obligations across its examples. |
|  | ● CWE-212 Improper Removal of Sensitive Information Before Storage or Transfer | Redaction and removal failures surface sensitive spans, such as text hidden under a black-rectangle redaction layer resurfaced by summarization. |
|  | ● CWE-532 Insertion of Sensitive Information into Log File | Observability pipelines log full prompts, completions, and reasoning traces, exposing sensitive data through log and telemetry stores. |
|  | ○ CWE-285 Improper Authorization | Retrieval runs before any authorization check, so cosine similarity returns documents the requester has no right to see. |
|  | ○ CWE-732 Incorrect Permission Assignment for Critical Resource | Unscoped drives, legacy permissions, and over-permissive knowledge bases feed the retrieval corpus with sensitive data. |
|  | ○ CWE-201 Insertion of Sensitive Information Into Sent Data | Tool-call arguments and outbound requests to external providers carry more sensitive fields than the task actually requires. |
| **LLM03** Excessive Agency | ● CWE-285 Improper Authorization | Authorization must be enforced at a policy decision point in application logic rather than left to the model, defending against confused-deputy and privilege-abuse behavior. |
|  | ● CWE-732 Incorrect Permission Assignment for Critical Resource | Database identities and service accounts granted write and delete rights or broadly high privileges beyond what the task needs are a named root cause of excessive agency. |
|  | ○ CWE-284 Improper Access Control (Pillar) | The pillar umbrella covers the entry's permission and access-control failures, including missing mediation and lost user context. |
|  | ○ CWE-770 Allocation of Resources Without Limits or Throttling | Thresholds and circuit breakers on invocation count or cumulative parameter value are needed to halt runaway tool calls. |
|  | ○ CWE-1427 Improper Neutralization of Input Used for LLM Prompting | Direct and indirect prompt injection, such as a crafted email, is the trigger that turns excess permissions into harmful action. |
| **LLM04** Supply Chain | ● CWE-494 Download of Code Without Integrity Check | Models and adapters are pulled by mutable tags or resolved by name without signature or hash verification, letting namespace reuse deliver code execution. |
|  | ● CWE-829 Inclusion of Functionality from Untrusted Control Sphere | The entry centers on including third-party models, adapters, and packages from untrusted hubs and registries, including slopsquatting and tampered models. |
|  | ○ CWE-349 Acceptance of Extraneous Untrusted Data With Trusted Data | A malicious LoRA adapter merged into a trusted base model blends poisoned artifacts into an otherwise trusted merge-and-convert pipeline. |
|  | ○ CWE-664 Improper Control of a Resource Through its Lifetime (Pillar) | Insecure deserialization of model weights and native-parser memory corruption are lifetime-control failures over the loaded model resource. |
| **LLM05** Data and Model Poisoning | ● CWE-349 Acceptance of Extraneous Untrusted Data With Trusted Data | Attacker-controlled untrusted data is mixed into trusted training corpora, retrieval stores, and continuous-learning feeds, the canonical poisoning weakness. |
|  | ● CWE-829 Inclusion of Functionality from Untrusted Control Sphere | Loading untrusted models, LoRA and PEFT adapters, tokenizer configs, and chat templates from public repositories pulls poisoned functionality into the pipeline. |
|  | ○ CWE-494 Download of Code Without Integrity Check | Signing and hash verification of model artifacts is prescribed because unverified model downloads carry tampered weights. |
|  | ○ CWE-1427 Improper Neutralization of Input Used for LLM Prompting | Poisoned retrieval documents and hidden web instructions reach the prompt without neutralization, the indirect-injection facet of poisoning. |
| **LLM06** Unbounded Consumption | ● CWE-400 Uncontrolled Resource Consumption | Every input-flood, context-overflow, thinking-token, and GPU-or-memory exhaustion pattern in the entry is a form of uncontrolled resource consumption. |
|  | ● CWE-770 Allocation of Resources Without Limits or Throttling | The defining root cause is the absence of rate, token, cost, and queue limits, with pre-flight estimation and hard spending caps as the missing controls. |
|  | ○ CWE-664 Improper Control of a Resource Through its Lifetime (Pillar) | The pillar ancestor of the consumption weaknesses covers management of the compute and memory resource across its lifetime. |
|  | ○ CWE-691 Insufficient Control Flow Management (Pillar) | Reasoning loops that burn thinking tokens and recursive or infinite tool-calling loops need recursion-depth limits and loop detection. |
|  | ○ CWE-829 Inclusion of Functionality from Untrusted Control Sphere | A malicious third-party tool or skill pulled from an open-source repository drives the resource-exhausting loops. |
| **LLM07** Misinformation | ● CWE-1426 Improper Validation of Generative AI Output | Incorrect, unsupported, or misleading model output is trusted and acted upon without verification, the entry's core weakness. |
|  | ○ CWE-349 Acceptance of Extraneous Untrusted Data With Trusted Data | A downstream agent accepts fabricated or misattributed upstream output as trusted evidence, a cross-agent trust failure. |
|  | ○ CWE-494 Download of Code Without Integrity Check | A hallucinated package name is installed without any integrity or authenticity check, the slopsquatting failure. |
|  | ○ CWE-1427 Improper Neutralization of Input Used for LLM Prompting | Adversarially crafted inputs induce false or misleading output, the input-side manipulation behind adversarially induced misinformation. |
| **LLM08** Hidden Context Exposure | ● CWE-200 Exposure of Sensitive Information to an Unauthorized Actor | The entry is defined by unauthorized extraction, inference, or reconstruction of hidden system instructions and operational context. |
|  | ○ CWE-798 Use of Hard-coded Credentials | API keys, tokens, and connection strings embedded in the system prompt are the highest-severity credential exposure. |
|  | ○ CWE-693 Protection Mechanism Failure (Pillar) | Refusal and behavior-control instructions placed in hidden context are reverse-engineered and bypassed rather than enforced. |
|  | ○ CWE-285 Improper Authorization | Authorization and access control must be enforced independently of the model, since roles and permissions carried in tool descriptions leak and fail. |
| **LLM09** Vector and Embedding Weaknesses | ● CWE-200 Exposure of Sensitive Information to an Unauthorized Actor | Embedding inversion recovers source text and cross-tenant leakage exposes other customers' data, the core confidentiality failure. |
|  | ● CWE-285 Improper Authorization | The access-control decision happens after the embedding-space search runs, so tenant scoping must be enforced server-side inside the index query. |
|  | ○ CWE-359 Exposure of Private Personal Information | Customer PII is reconstructed from a leaked embedding backup, creating GDPR data-subject risk. |
|  | ○ CWE-732 Incorrect Permission Assignment for Critical Resource | Mis-scoped chunk-level ACLs and a cloud misconfiguration exposing a vector-database backup are access-control misassignments. |
|  | ○ CWE-829 Inclusion of Functionality from Untrusted Control Sphere | Retrieval poisoning causes attacker content from an untrusted source to be retrieved and fed to the model as trusted context. |
| **LLM10** Improper Output Handling | ● CWE-1426 Improper Validation of Generative AI Output | Model output is passed downstream with insufficient validation, sanitization, or handling, the entry's exact subject. |
|  | ● CWE-116 Improper Encoding or Escaping of Output | Missing context-aware output encoding across HTML, JavaScript, SQL, and terminal sinks is the root cause. |
|  | ● CWE-79 Cross-site Scripting (XSS) | Cross-site scripting is the most-repeated concrete sink, addressed by content-security-policy and output-encoding defenses. |
|  | ○ CWE-707 Improper Neutralization (Pillar) | The neutralization pillar covers control-character sanitization of ANSI, BEL, OSC, backspace, and carriage-return sequences and SQL escaping and parameterization. |
|  | ○ CWE-200 Exposure of Sensitive Information to an Unauthorized Actor | Unhandled output leaks sensitive conversation and website content to an attacker. |
|  | ○ CWE-201 Insertion of Sensitive Information Into Sent Data | Sensitive data is smuggled into the hostname or query string of an auto-fetched Markdown-image request. |

## NIST AI 600-1 (Generative AI Profile) — v1.0 (July 2024)

*Each row maps an OWASP LLM risk to the NIST AI 600-1 Generative AI Profile risk categories it engages; primary categories name the entry's core risk, supporting categories name secondary facets.*

| Risk | Element | Relevance |
|---|---|---|
| **LLM01** Prompt Injection | ● Information Security | Prompt injection expands the attack surface, letting adversarial text hijack the model to exfiltrate data or trigger unauthorized actions across connected systems. |
|  | ○ Information Integrity | Injected instructions manipulate outputs into attacker-chosen content and poison retrieved or remembered context, corrupting the information the system produces. |
|  | ○ Data Privacy | Successful injection can exfiltrate private conversation history, uploaded documents, and repository contents to an attacker. |
|  | ○ Human-AI Configuration | Human-in-the-loop confirmation degrades under approval fatigue, and benign content can carry unintended injected instructions, both matters of human-oversight configuration. |
| **LLM02** Sensitive Information Disclosure | ● Data Privacy | The entry centers on privacy leakage and de-anonymization of PII, PHI, biometric, and genomic data, including membership inference that confirms a named individual and defeats erasure obligations. |
|  | ● Information Security | It concerns confidentiality of the system and its data through model and data exfiltration, credential exposure, and extraction attacks. |
|  | ○ Intellectual Property | Trade secrets and model weights are protected assets at risk, and models can reproduce copyrighted or watermarked training material verbatim. |
|  | ○ Value Chain and Component Integration | Third-party observability platforms, SDKs, and integrated browser components disclose sensitive data through the surrounding ecosystem. |
| **LLM03** Excessive Agency | ● Information Security | Excessive agency lets an agent exfiltrate data, perform unauthorized writes, and take destructive actions across the downstream systems it can reach. |
|  | ○ Human-AI Configuration | Excessive autonomy acting without confirmation is a root cause, and human-in-the-loop approval is the primary control, both configuration of human oversight. |
|  | ○ Confabulation | Hallucinated or confabulated reasoning can trigger the agent to take damaging real-world actions. |
|  | ○ Data Privacy | An over-privileged agent can forward a user's private email content to an attacker, a personal-data breach. |
| **LLM04** Supply Chain | ● Value Chain and Component Integration | The entry is entirely about the integrity of third-party models, datasets, adapters, and integrated components across the AI value chain. |
|  | ● Information Security | Supply-chain compromise produces backdoors, poisoning, remote code execution, and other security breaches. |
|  | ○ Intellectual Property | Unclear licensing for use, distribution, and commercialization, plus copyright exposure from supplier material, put intellectual property at risk. |
|  | ○ Information Integrity | Tampered or poisoned models emit biased outputs and misinformation, and a tampered on-device model can steer users to scam sites. |
|  | ○ Confabulation | Coding assistants confabulate nonexistent package names that attackers pre-register, the slopsquatting vector. |
| **LLM05** Data and Model Poisoning | ● Information Integrity | Poisoning steers answers, injects subtle misinformation, and manipulates recommendations and downstream business decisions. |
|  | ● Value Chain and Component Integration | Third-party datasets, shared model repositories, and bundled artifacts introduce compromise through the GenAI value chain. |
|  | ● Information Security | Data and model poisoning, embedded backdoors, and unsafe-artifact code execution are core security risks. |
|  | ○ Dangerous, Violent, or Hateful Content | Targeted poisoning erodes refusal behaviors, as when a public chatbot was manipulated into producing offensive content. |
| **LLM06** Unbounded Consumption | ● Information Security | Unbounded consumption threatens availability through denial of service and confidentiality through model extraction and side-channel theft of weights and architecture. |
|  | ○ Intellectual Property | Model extraction and functional cloning steal the model as intellectual property and trade secret. |
|  | ○ Value Chain and Component Integration | Shared inference infrastructure and third-party serving frameworks add supply-chain attack surface. |
| **LLM07** Misinformation | ● Information Integrity | The entry concerns GenAI producing false or misleading information that degrades human decisions, the definition of this misinformation risk. |
|  | ● Confabulation | Confabulation, NIST's term for confidently stated but false output, is named as a primary source of the misinformation. |
|  | ● Human-AI Configuration | Automation bias and overreliance are called a key factor, addressed by calibrating human and system trust. |
|  | ○ Information Security | Adversarially induced misinformation and false alerts can cause security incidents and operational disruption. |
|  | ○ Value Chain and Component Integration | Hallucinated dependencies and unvalidated third-party tool outputs are value-chain integration risks. |
| **LLM08** Hidden Context Exposure | ● Information Security | System-prompt and context extraction, an expanded attack surface, and lowered barriers to targeted exploitation are the core security risks. |
|  | ○ Intellectual Property | Exposed hidden context can reveal proprietary behavior and sensitive implementation details, such as a leaked system prompt. |
| **LLM09** Vector and Embedding Weaknesses | ● Data Privacy | Embedding inversion, membership inference, and cross-tenant leakage recover PII and infer data-subject membership, triggering breach obligations. |
|  | ● Information Security | Access-control failure, unauthorized cross-tenant retrieval, oracle and endpoint abuse, and availability jamming are core security concerns. |
|  | ● Information Integrity | Retrieval poisoning corrupts the context the model relies on, degrading the integrity of retrieved and generated information. |
|  | ○ Value Chain and Component Integration | A backdoored third-party embedding model corrupts the geometry of everything ingested, a value-chain integrity risk. |
| **LLM10** Improper Output Handling | ● Information Security | Unhandled model output flows into downstream systems as remote code execution, XSS, SQL injection, SSRF, CSRF, and privilege escalation. |
|  | ○ Data Privacy | Unsanitized output can leak sensitive conversation data to an attacker. |
|  | ○ Confabulation | Generated code can reference hallucinated nonexistent software packages, a confabulation facet of unsafe output. |
|  | ○ Value Chain and Component Integration | Third-party extensions that fail to validate inputs and hallucinated-package installs implicate component integration and supply chain. |

## NIST AI RMF (AI 100-1) — v1.0 (2023)

*Each row maps an OWASP LLM risk to the NIST AI RMF (AI 100-1) Categories whose outcomes it most directly exercises, with "primary" marking a near-verbatim fit and "supporting" a partial or governance-level fit.*

| Risk | Element | Relevance |
|---|---|---|
| **LLM01** Prompt Injection | ○ MEASURE 1 (methods & metrics) | The entry rejects static-only attack-success-rate claims and mandates adaptive-attack metrics, baselining injection defenses with AgentDojo and JailbreakBench because static scores run near zero while adaptive success exceeds 90 percent. |
|  | ○ MEASURE 2 (evaluate trustworthiness) | Defenses are red-teamed against attackers who have read the full defense specification, evaluating the deployed system's injection resilience rather than trusting a metric selected in isolation. |
|  | ○ MAP 4 (map risks across all components) | Decomposing an injection along delivery surface, propagation behavior, and encoding is presented as a threat-modeling step that maps risk across components including RAG corpora, MCP servers, and third-party tool packages. |
| **LLM02** Sensitive Information Disclosure | ○ MAP 5 (characterize impacts on people) | Disclosure is framed as impact to data subjects, where membership inference yields a regulatory-breach determination about a named individual under GDPR or HIPAA. |
|  | ○ MEASURE 2 (evaluate trustworthiness) | A release gate requires disclosure red-teaming that quantitatively measures extraction, membership inference, embedding inversion, internal-state inversion, side channels, and LoRA extractability. |
|  | ○ MANAGE 4 (risk treatment, response & recovery) | The disclosure incident-response playbook sets breach-notification timelines and treats leaks with unlearning, retraining, withdrawal, and vector and cache cleanup, plus vendor notice. |
| **LLM03** Excessive Agency | ○ MANAGE 4 (risk treatment, response & recovery) | Logging and monitoring of extension and downstream activity is paired with circuit breakers that halt, rate-limit, or escalate agent actions for human review. |
| **LLM04** Supply Chain | ● GOVERN 6 (third-party & supply-chain policy) | The entire entry is LLM supply chain, covering supplier vetting, terms-and-conditions review, and component-patching policy for third-party software, data, and models. |
|  | ● MAP 4 (map risks across all components) | A signed SBOM, AIBOM, and ML-SBOM component inventory together with component and supplier vetting maps risk across every third-party model, dataset, and dependency. |
|  | ● MANAGE 3 (manage third-party risks) | Vetting and re-auditing suppliers and treating model conversion or merge services as high-risk promotion points is direct third-party-entity risk management. |
|  | ○ MEASURE 2 (evaluate trustworthiness) | AI red teaming and evaluation when selecting third-party models, plus in-production adversarial-robustness testing and anomaly detection, assess acquired components. |
|  | ○ MEASURE 3 (track risks over time) | Continuous validation of upstream model integrity, in-production anomaly detection, and regular BOM and supplier re-audits track supply-chain risk over time. |
| **LLM05** Data and Model Poisoning | ○ MEASURE 3 (track risks over time) | Outputs, training loss, and behavioral patterns are monitored for drift against defined thresholds to detect subtle poisoning that emerges over time. |
|  | ○ MEASURE 2 (evaluate trustworthiness) | Continuous red-teaming with adversarial and trigger-based prompts, with dedicated trigger-probing required after every alignment cycle, evaluates the model for hidden backdoors. |
|  | ○ GOVERN 6 (third-party & supply-chain policy) | Vendor vetting, model and data lineage tracking, and controls against open-source dataset supply-chain poisoning and malicious models address third-party poisoning vectors. |
| **LLM06** Unbounded Consumption | ○ MANAGE 1 (prioritize & respond to risks) | Rate limits, hard spending caps, agentic circuit breakers, and graceful degradation form an impact-prioritized response informed by cost-attribution monitoring and baselines. |
|  | ○ MEASURE 2 (evaluate trustworthiness) | Adversarial-perturbation scanning and resource-consumption red-teaming, supported by tool-behavior baselines, evaluate the system for the secure-and-resilient availability characteristic. |
| **LLM07** Misinformation | ● MEASURE 2 (evaluate trustworthiness) | The entry's defense is evaluation-centric, using groundedness and consistency checks, misinformation monitoring and testing, and continuous adversarial evaluation to measure the validity, reliability, and accuracy that misinformation threatens. |
|  | ○ MEASURE 1 (methods & metrics) | Verification signals such as groundedness and consistency checks replace naive model confidence as the metric for whether a claim can be trusted before action. |
|  | ○ MEASURE 3 (track risks over time) | Claims, evidence, and outcomes are logged and adversarial scenarios tested so misinformation is tracked over time. |
|  | ○ MANAGE 1 (prioritize & respond to risks) | Runtime verification and approval workflows for high-impact actions, together with blast-radius limits, are impact-prioritized response controls. |
| **LLM08** Hidden Context Exposure | ○ MEASURE 2 (evaluate trustworthiness) | Detecting hidden-context exposure is a security-evaluation activity, red-teaming for prompt and context extraction grounded in RL-based red-teaming for privacy leakage and system-prompt-extraction research. |
| **LLM09** Vector and Embedding Weaknesses | ○ MAP 4 (map risks across all components) | The embedding layer is established as part of the application's trust boundary, directing teams to vet the embedding model and treat third-party embedding services and backups as in-scope components. |
|  | ○ MAP 5 (characterize impacts on people) | Impact to data subjects is characterized, since embedding inversion recovers PII and an embeddings-only leak is reclassified as a source-document breach triggering breach notification. |
|  | ○ MANAGE 4 (risk treatment, response & recovery) | Immutable retrieval logs and updated incident-response playbooks treat embeddings-only leaks as source-data breaches with GDPR Article 33 notification. |

## CSA AI Controls Matrix (AICM) — v1.1 (2026-06-22)

*Each row maps an OWASP LLM risk to the CSA AI Controls Matrix v1.1 control domains that address it, where primary domains carry the core control and supporting domains add defense in depth.*

| Risk | Element | Relevance |
|---|---|---|
| **LLM01** Prompt Injection | ● AIS Application & Interface Security | Constrains the injection surface at the interface through system-prompt role separation, output-schema validation, cross-modality input filtering, invisible-Unicode stripping, and provenance-labeled channels that mark untrusted content. |
|  | ○ IAM Identity & Access Management | Contains a successful injection by granting each tool call least privilege, running actions in the user's scoped context, and requiring human approval before privileged or irreversible operations. |
|  | ○ TVM Threat & Vulnerability Management | Requires adaptive red-teaming by adversaries who have already read the defenses, rejecting static-only test suites that miss evolving injection techniques. |
|  | ○ STA Supply Chain Management, Transparency, and Accountability | Treats connected tools, plugins, and MCP servers as a software supply-chain surface that must be pinned, signed, and verified before an agent will call them. |
| **LLM02** Sensitive Information Disclosure | ● DSP Data Security and Privacy Lifecycle Management | Governs classification, minimization, retention, encryption, and verifiable erasure of sensitive records across the four-phase data lifecycle the entry is organized around. |
|  | ● IAM Identity & Access Management | Enforces authorize-before-retrieval with document- and chunk-level access control inside the index query and per-tenant isolation, since vector similarity alone does not respect access-control lists. |
|  | ○ CEK Cryptography, Encryption & Key Management | Applies encryption in transit and at rest, format-preserving encryption for structured identifiers, and vector-store encryption so sensitive data stays unreadable if exposed. |
|  | ○ MDS Model Development Security | Reduces training-data memorization through differential-privacy training calibrated to sensitivity, near-duplicate deduplication, verifiable erasure across checkpoints and adapters, and resistance to distillation. |
|  | ○ AIS Application & Interface Security | Gates log-probabilities, confidence scores, and explanations on production endpoints, sanitizes outputs with classifiers, separates internal from external routing, and defends streaming side channels. |
| **LLM03** Excessive Agency | ● IAM Identity & Access Management | Minimizes agent permissions, executes tool actions inside the user's OAuth-scoped context, and applies complete mediation so an over-privileged identity cannot exceed its authorization. |
|  | ○ AIS Application & Interface Security | Hardens the extension and tool interface with strict input schemas, parameter validation, avoidance of open-ended functionality, and application-security testing. |
|  | ○ LOG Logging and Monitoring | Logs and monitors the activity of extensions and downstream systems so undesirable or unauthorized actions are detected quickly. |
|  | ○ TVM Threat & Vulnerability Management | Runs static, dynamic, and interactive application-security testing within the development pipeline to find vulnerabilities in agent extensions before release. |
| **LLM04** Supply Chain | ● STA Supply Chain Management, Transparency, and Accountability | Directly matches the domain with SBOM/AIBOM/ML-SBOM inventory, supplier vetting, and provenance backed by cryptographic signing and transparency logs. |
|  | ● MDS Model Development Security | Counters model tampering and backdoors and preserves integrity across adapter merges, format conversion, and quantization through model signing and behavioral evaluation. |
|  | ○ TVM Threat & Vulnerability Management | Scans for vulnerable or outdated components in serving frameworks and models and enforces a patching policy across the dependency chain. |
|  | ○ CEK Cryptography, Encryption & Key Management | Uses cryptographic model signing, Sigstore and transparency-log entries, file hashes, and edge-model encryption with integrity checks to verify artifact authenticity. |
|  | ○ CCC Change Control and Configuration Management | Enforces promotion boundaries with immutable references, policy-based release gates aligned to SLSA, and build-pipeline integrity across CI/CD. |
| **LLM05** Data and Model Poisoning | ● MDS Model Development Security | Secures training and fine-tuning data and model artifacts against poisoning across the development lifecycle. |
|  | ● DSP Data Security and Privacy Lifecycle Management | Validates incoming data, checks integrity, and versions datasets so tampered inputs are caught across the data lifecycle. |
|  | ○ STA Supply Chain Management, Transparency, and Accountability | Establishes model and dataset lineage through SBOM/ML-BOM records, artifact signing, and vendor vetting to counter distributed poisoned models. |
|  | ○ LOG Logging and Monitoring | Applies statistical and AI-based anomaly detection and behavioral-drift monitoring across training, embedding, and inference to surface poisoning effects. |
|  | ○ TVM Threat & Vulnerability Management | Runs continuous adversarial red-teaming and trigger-probing to expose hidden backdoors planted during poisoning. |
| **LLM06** Unbounded Consumption | ● AIS Application & Interface Security | Applies front-line interface controls including rate limiting, token- and cost-aware caps, input-size validation, pre-flight token estimation, and authenticated inference endpoints. |
|  | ● BCR Business Continuity Management and Operational Resilience | Preserves availability through graceful degradation and dynamic scaling with load balancing when demand or abuse spikes. |
|  | ○ IVS Infrastructure & Virtualization Security | Manages resource allocation and hardens inference infrastructure, including disabling unsafe deserialization and reducing the shared-inference side-channel surface. |
|  | ○ LOG Logging and Monitoring | Provides continuous cost-attribution monitoring and detection of resource-intensive tool interactions against normal-behavior baselines. |
|  | ○ IAM Identity & Access Management | Scopes quotas and hard spending caps per API key, user, team, and account and authenticates inference endpoints to blunt stolen-credential abuse. |
| **LLM07** Misinformation | ● AIS Application & Interface Security | Separates claim from action, validates tool calls semantically, requires verification signals and structured outputs with mandatory fields, and verifies model assertions at runtime. |
|  | ○ TVM Threat & Vulnerability Management | Runs adversarial evaluation and continuous testing against deliberately misleading scenarios to catch misinformation before it reaches users. |
|  | ○ LOG Logging and Monitoring | Logs claims, supporting evidence, and outcomes and monitors for misinformation patterns over time. |
|  | ○ STA Supply Chain Management, Transparency, and Accountability | Addresses hallucinated-dependency attacks and unsafe generated code by verifying that packages and dependencies the model names actually exist and are trusted. |
| **LLM08** Hidden Context Exposure | ● AIS Application & Interface Security | Treats hidden context as an interface-exposure risk by curating what enters the context window, applying app-layer guardrails, and enforcing independent controls rather than trusting the prompt. |
|  | ○ IAM Identity & Access Management | Enforces authorization and access control independently of the model and splits privileges across agents so exposed context cannot grant capability. |
|  | ○ CEK Cryptography, Encryption & Key Management | Keeps credentials, tokens, and connection strings out of the prompt by externalizing secrets to a managed store. |
| **LLM09** Vector and Embedding Weaknesses | ● IAM Identity & Access Management | Scopes tenant identity inside the index query, validates server-side, authenticates per-tenant endpoints, and enforces chunk-level access control. |
|  | ● DSP Data Security and Privacy Lifecycle Management | Tracks provenance, segregates trust tiers, deletes embeddings with their source, and audits retention, encryption at rest, and backup sensitivity across the embedding lifecycle. |
|  | ● LOG Logging and Monitoring | Applies anomaly detection at ingest and retrieval and keeps immutable retrieval logs monitored for tenant-filter bypass and cross-tenant access. |
|  | ○ CEK Cryptography, Encryption & Key Management | Encrypts embeddings at rest with keys managed separately from the application layer and treats embedding-API keys as secrets. |
|  | ○ AIS Application & Interface Security | Authenticates embedding and similarity-search endpoints as first-class APIs, applies per-tenant rate limits, and withholds raw similarity scores. |
|  | ○ STA Supply Chain Management, Transparency, and Accountability | Vets the embedding model against backdoored-encoder risk and tracks provenance of the encoder and the indexed content. |
| **LLM10** Improper Output Handling | ● AIS Application & Interface Security | Validates model responses as untrusted input and applies context-aware output encoding, parameterized queries, and content-security policy before outputs reach downstream interpreters. |
|  | ○ LOG Logging and Monitoring | Logs and monitors model outputs so exploitation patterns in downstream handling are detected. |
|  | ○ IAM Identity & Access Management | Treats the model as any other user under a zero-trust posture so its outputs never inherit privileges beyond the end user. |

## OWASP AIVSS (AI Vulnerability Scoring System) — v0.8

*Each row lists the OWASP AIVSS Agentic AI Core Security Risks that the LLM Top 10 entry can produce or feed, with primary marking the risks the entry most directly enables and supporting marking secondary paths; AIVSS then scores the severity of those agentic risks.*

| Risk | Element | Relevance |
|---|---|---|
| **LLM01** Prompt Injection | ● AIVSS-10 Agent Goal and Instruction Manipulation | A crafted message overrides the system prompt's role and capability limits, redirecting the model to act outside its intended scope. |
|  | ● AIVSS-1 Agentic AI Tool Misuse | Injected input drives unauthorized invocation of tools the agent is permitted to call, from file system and shell to email and cloud APIs. |
|  | ● AIVSS-2 Agent Access Control Violation | The agent reads attacker-planted text while operating under the user's elevated credentials and performs privileged actions the attacker could not reach directly. |
|  | ● AIVSS-6 Agent Memory and Context Manipulation | An injection written to long-term memory or a RAG corpus taints every later session that reads the poisoned store, persisting the compromise across conversations. |
|  | ○ AIVSS-7 Insecure Agent Critical Systems Interaction | Where the agent holds shell, file-system, or cloud-API access, an injection escalates into arbitrary command execution and destructive actions on the host. |
|  | ○ AIVSS-3 Agent Cascading Failures | Tool outputs re-enter the shared context window, letting one injection chain into further tool calls or self-replicate across steps. |
|  | ○ AIVSS-4 Agent Orchestration and Multi-Agent Exploitation | An injection can self-replicate across agents, spreading from one compromised agent to its peers in a multi-agent workflow. |
| **LLM03** Excessive Agency | ● AIVSS-1 Agentic AI Tool Misuse | Extensions carry functions beyond what the task needs, such as read-only access bundled with modify, delete, or send, so a malfunctioning model invokes capabilities it was never meant to use. |
|  | ● AIVSS-2 Agent Access Control Violation | Extensions connect to downstream systems with over-broad or generic high-privileged identities, letting the agent act far beyond the user's own authorization scope. |
|  | ● AIVSS-7 Insecure Agent Critical Systems Interaction | An open-ended shell-command extension that fails to filter unintended commands, or an over-autonomous coding agent, can execute damaging actions and destroy production infrastructure. |
|  | ○ AIVSS-3 Agent Cascading Failures | Without rate limits or circuit breakers, runaway extension invocation compounds into cascading downstream failures. |
|  | ○ AIVSS-4 Agent Orchestration and Multi-Agent Exploitation | A malicious or compromised peer agent can trigger damaging actions, and failing to preserve user context across chained agent calls widens the blast radius. |
|  | ○ AIVSS-10 Agent Goal and Instruction Manipulation | Direct or indirect prompt injection, such as a crafted incoming email, is the trigger that redirects the agent into unwanted privileged actions. |
| **LLM04** Supply Chain | ○ AIVSS-8 Agent Supply Chain and Dependency Risk | Compromised third-party packages, pre-trained models, LoRA adapters, and conversion or merge pipelines are the dependency substrate an agent inherits, so a tampered model-supply-chain artifact becomes the agent's supply chain too. |
| **LLM05** Data and Model Poisoning | ○ AIVSS-6 Agent Memory and Context Manipulation | Attackers embed hidden instructions in web content that poison an agent's persistent memory or recommendations across sessions, so the agent begins prioritizing attacker-controlled logic. |
|  | ○ AIVSS-8 Agent Supply Chain and Dependency Risk | Backdoored models and unsafe-serialization artifacts distributed through public repositories carry hidden triggers that a downstream agent inherits when it loads them. |
|  | ○ AIVSS-3 Agent Cascading Failures | Poisoned inputs propagate across multi-agent and enterprise workflows, and shared embeddings or memory layers spread contamination from one tenant to others. |
| **LLM06** Unbounded Consumption | ○ AIVSS-1 Agentic AI Tool Misuse | A malicious tool forces an agent into recursive or infinite tool-calling loops, driving token consumption and cost far beyond the task's needs. |
|  | ○ AIVSS-3 Agent Cascading Failures | Agentic and MCP protocols amplify a single request into cascading downstream operations, so one task fans out into many tool calls that exhaust budget and availability. |
|  | ○ AIVSS-8 Agent Supply Chain and Dependency Risk | An attacker publishes a malicious tool, such as a skill on an open-source repository, that developers incorporate as an agent dependency, driving token exhaustion once integrated. |
| **LLM07** Misinformation | ● AIVSS-3 Agent Cascading Failures | Incorrect state or evidence produced by one agent and trusted by another propagates across a multi-agent workflow into a compounding, high-impact failure. |
|  | ○ AIVSS-1 Agentic AI Tool Misuse | Because model outputs drive tool calls, an incorrect state inference triggers unintended actions unless invocations are validated against real-world state and intent. |
|  | ○ AIVSS-7 Insecure Agent Critical Systems Interaction | A false conclusion, such as wrongly approving a refund or firing a false alert, drives an automated high-impact action that causes financial loss or operational disruption. |
| **LLM08** Hidden Context Exposure | ○ AIVSS-2 Agent Access Control Violation | Disclosed permission rules and user-role directives from hidden context reveal the authorization model, inviting probing that bypasses controls the application should enforce independently of the LLM. |
|  | ○ AIVSS-1 Agentic AI Tool Misuse | Extracting the hidden tool list and parameter schemas gives an attacker concrete targets to steer the application toward specific tool calls. |
| **LLM09** Vector and Embedding Weaknesses | ○ AIVSS-6 Agent Memory and Context Manipulation | Retrieval-time poisoning manipulates the geometry of vector-backed agent memory so attacker content is retrieved as trusted context, while non-geometric memory poisoning is deferred to the agentic framework. |
|  | ○ AIVSS-8 Agent Supply Chain and Dependency Risk | A backdoored embedding model corrupts the geometry of everything ingested, and vulnerable vector-database dependencies compound the risk since a leaked index is recoverable to source documents. |
|  | ○ AIVSS-2 Agent Access Control Violation | Similarity search runs across the full shared index before tenant access control is applied, so an attacker infers or reaches other tenants' content that authorization should have blocked. |
| **LLM10** Improper Output Handling | ○ AIVSS-7 Insecure Agent Critical Systems Interaction | Unvalidated model output reaching a shell, exec/eval, SQL, or file-path sink yields remote code execution, SQL injection, or path traversal on backend systems. |
|  | ○ AIVSS-1 Agentic AI Tool Misuse | A general-purpose LLM's unvalidated response passed to a privileged extension causes the extension to be misused, for example forced into an unintended shutdown. |

## Framework Sources & Versions

| Framework | Version | Source |
| --- | --- | --- |
| OWASP Top 10 for Agentic Applications (ASI) | 2026 (announced 2025-12-09) | https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ |
| OWASP GenAI Data Security 2026 (DSGAI) | v1.0 (2026-03-17) | https://genai.owasp.org/resource/owasp-genai-data-security-risks-mitigations-2026/ |
| MITRE ATLAS | content v2026.06 (format-version 6.0.0) | https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.06.yaml |
| MITRE ATT&CK | v19.1 | https://attack.mitre.org/versions/v19/tactics/enterprise/ |
| MITRE CWE (Common Weakness Enumeration) | 4.20 | https://cwe.mitre.org/ |
| NIST AI 600-1 (Generative AI Profile) | v1.0 (July 2024) | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf |
| NIST AI RMF (AI 100-1) | v1.0 (2023) | https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ |
| CSA AI Controls Matrix (AICM) | v1.1 (2026-06-22) | https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1 |
| OWASP AIVSS (AI Vulnerability Scoring System) | v0.8 | https://aivss.owasp.org/assets/publications/AIVSS%20Scoring%20System%20For%20OWASP%20Agentic%20AI%20Core%20Security%20Risks%20v0.8.pdf |
