## LLM06:2026 Unbounded Consumption

### Description

Unbounded Consumption occurs when an LLM application allows excessive and uncontrolled inferences, enabling attackers to disrupt service availability, inflict unsustainable financial costs, or steal intellectual property through model cloning, all by exploiting a common class of vulnerability: the absence of adequate controls over how resources are consumed. 

The high computational demands of LLMs, particularly in cloud and pay-per-token environments, make them inherently susceptible to resource exploitation and unauthorized usage. A defining characteristic of this threat is cost asymmetry. Attackers can trigger disproportionately expensive computation at negligible cost to themselves, whether through crafted prompts, stolen credentials, or manipulated workflows. 

This risk is compounded by the growing adoption of extended-thinking and reasoning models with unbounded token generation, multi-modal models that dramatically expand per-request compute costs, agentic architectures and tool-use protocols (such as MCP) that amplify a single request into cascading downstream operations, and shared inference infrastructure that introduces new side-channel and supply-chain attack surfaces. Traditional request-rate limiting alone is no longer sufficient; effective defense demands token-aware cost controls, hard spending caps, agent-level circuit breakers, and continuous cost-attribution monitoring.


### Common Examples of Risk

#### 1. Variable-Length Input Flood and Output Explosion

  Attackers can overload the LLM with numerous inputs of varying lengths, exploiting processing inefficiencies. This can deplete resources and potentially render the system unresponsive, significantly impacting service availability. This also includes output explosion via fine-tuning poisoning where a single malicious training sample breaks the model’s end-of-sequence behavior, pushing output to maximum tokens on every request.

#### 2. Denial of Wallet (DoW)

  By initiating a high volume of operations, attackers exploit the cost-per-use model of cloud-based AI services, leading to unsustainable financial burdens on the provider and risking financial ruin.

#### 3. Continuous Input Overflow

  Continuously sending inputs that exceed the LLM’s context window can lead to excessive computational resource use, resulting in service degradation and operational disruptions.

#### 4. Reasoning-Loop and Thinking-Token Exhaustion
  Attackers craft short, benign-looking prompts that result in resource exhaustion by forcing extended-thinking models into prolonged or non-terminating reasoning loops, consuming massive thinking-token budgets while bypassing input-size filters. Because these prompts are small and appear legitimate, standard input validation provides no protection.

#### 5. Adversarial Inputs Optimized for Resource Overconsumption
  Attackers use optimization techniques to craft inputs that maximize computational cost. This is distinct from simply asking the model to perform a resource-intensive task and includes sponge examples and adversarial visual perturbations. This includes optimization of adversarial input with gradient-based and gradient-free techniques. Unlike reasoning-loop attacks these require explicit optimization over the input space rather than prompt design alone. 

#### 6. Multimodal Inputs and Outputs
  For multi-modal models that are more cost-intensive than the text-only services, the extent of the computation cost is exacerbated. In many cases, this can result in 10 to 100 times the cost of text-based models.

#### 7. Model Extraction and Distillation Theft
  Attackers query the model API with crafted inputs to collect sufficient outputs to replicate a partial model or fine-tune a functional equivalent. Exposure of logits and log-probabilities significantly accelerates extraction.

#### 8. Side-Channel Attacks
  Malicious attackers may exploit input filtering techniques of the LLM to execute side-channel attacks, harvesting model weights and architectural information. This could compromise the model’s security and lead to further exploitation.

#### 9. Agent-Tool Interactions Flooding Model Resources
  Attackers can publish tools that overuse LLM resources by forcing an LLM-based application into recursive or infinite tool calling loops. This could cause seemingly legitimate tool actions to result in financial burdens or compromise quality of service. Furthermore, when one tool-call fans out into a much larger quantity of actions, this can result in token overuse if the LLM needs to manage hundreds of tool calls spawned from one task.

#### 10. Inference Infrastructure Exploitation
  Attackers target vulnerabilities in LLM serving frameworks (vLLM, TensorRT-LLM, SGLang, Triton, Ollama) to crash services or exhaust model resources through unsafe deserialization flaws, special-token injection, injected chat templates. 


### Prevention and Mitigation Strategies

#### 1. Rate Limiting & Input Size Validation

  Apply rate limiting and user quotas to restrict the number of requests a single source entity can make in a given time period. Move beyond requests per second to enforce limits on tokens-per-minute, tokens-per-day and estimated cost per request. Use pre-flight token estimation to reject requests before inference begins. This includes validation to ensure inputs do not exceed reasonable size limits.

#### 2. Hard Spending Caps

  Set non-overridable budget ceilings per API key, user, team, and cloud account. These must be enforcement mechanisms that halt inference when exceeded, not merely alerting thresholds that can be outpaced by fast-accumulating workloads. Furthermore, spending caps need to factor in cost differences between different modalities and tool protocols.

#### 4. Resource Allocation Management

  Monitor and manage resource allocation dynamically to prevent any single user or request from consuming excessive resources.

#### 5. Sandbox Techniques

  Restrict the LLM’s access to network resources, internal services, and APIs. This is particularly significant for all common scenarios as it encompasses insider risks and threats. Furthermore, it governs the extent of access the LLM application has to data and resources, thereby serving as a crucial control mechanism to mitigate or prevent side-channel attacks.

#### 6. Graceful Degradation

  Design the system to degrade gracefully under heavy load, maintaining partial functionality rather than complete failure.

#### 7. Limit Queued Actions and Scale Robustly

  Implement restrictions on the number of queued actions and total actions, while incorporating dynamic scaling and load balancing to handle varying demands and ensure consistent system performance.

#### 8. Scan for Adversarial Perturbations
  
  Scan model inputs, particularly visual inputs to LVLMs (large visual language models) for evidence of adversarial perturbations that could cause model resource overconsumption.

#### 9. Detect Resource-Intensive Tool Interactions

  Monitor agent-tool interactions to identify if a particular session appears to be causing a recursive or resource-intensive action without a clear end state. Establish baselines of normal tool behavior in order to detect if a particular tool is deviating from standard token consumption patterns.
  
#### 10. Agentic Circuit Breakers
  
  Enforce step limits, recursion depth limits, time limits, and per-run cost ceilings on all agent executions. Use state hashing to detect recursive loops.
  
#### 11. Inference Infrastructure Hardening

  Keep serving frameworks updated. Disable unsafe deserialization, restrict special-token passthrough, and enforce authentication on all inference endpoints. 
  

### Example Attack Scenarios

#### Scenario #1: Uncontrolled Input Size

  An attacker submits an unusually large input to an LLM application that processes text data, resulting in excessive memory usage and CPU load, potentially crashing the system or significantly slowing down the service.

#### Scenario #2: Repeated Requests

  An attacker transmits a high volume of requests to the LLM API, causing excessive consumption of computational resources and making the service unavailable to legitimate users.

#### Scenario #3: Resource-Intensive Queries

  An attacker crafts specific inputs designed to trigger the LLM's most computationally expensive processes, leading to prolonged GPU usage and potential system failure.

#### Scenario #4: Denial of Wallet (DoW)

  An attacker generates excessive operations to exploit the pay-per-use model of cloud-based AI services, causing unsustainable costs for the service provider.

#### Scenario #5: Functional Model Replication

  An attacker uses the LLM's API to generate synthetic training data and fine-tunes another model, creating a functional equivalent and bypassing traditional model extraction limitations.

#### Scenario #6: Perturbations in LVLM Image Input

  An attacker crafts adversarial image inputs that include perturbations optimized to cause an LVLM to overconsume tokens in its output.

#### Scenario #7: Multi-turn Tool Calling Loops and Tool Call Fan-Out

  The attacker can publish a malicious tool (e.g. via a Claude Skill on an open-source repository) that instructs an agent to perform recursive cyclical tasks, or tasks that require a large number of tool calls. Developers incorporating that tool into their agents then risk causing excessive token consumption and service instability.

#### Scenario #8: Bypassing System Input Filtering

  A malicious attacker bypasses input filtering techniques and preambles of the LLM to perform a side-channel attack and retrieve model information to a remote controlled resource under their control.

#### Scenario #9: Growing LLM Context in Agentic Sessions

  An attacker or a benign user maintains an open agentic session, gradually injecting content. After some 100 turns, each inference re-processes full context. Turn 1: $0.001. Turn 100: $0.50. In aggregate, this results in hundreds of dollars of spend. No single request triggers rate limits because each is individually within budget.


### Reference Links

1. [Proof Pudding (CVE-2019-20634)](https://avidml.org/database/avid-2023-v009/): **AVID** (`moohax` & `monoxgas`)
2. [Stealing Part of a Production Language Model](https://arxiv.org/abs/2403.06634): **arXiv**
3. [Runaway LLaMA | How Meta's LLaMA NLP model leaked](https://www.deeplearning.ai/the-batch/how-metas-llama-nlp-model-leaked/): **Deep Learning Blog**
4. [You wouldn't download an AI, Extracting AI models from mobile apps](https://altayakkus.substack.com/p/you-wouldnt-download-an-ai): **Substack blog**
5. [A Comprehensive Defense Framework Against Model Extraction Attacks](https://ieeexplore.ieee.org/document/10080996): **IEEE**
6. [Alpaca: A Strong, Replicable Instruction-Following Model](https://crfm.stanford.edu/2023/03/13/alpaca.html): **Stanford Center on Research for Foundation Models (CRFM)**
7. [How Watermarking Can Help Mitigate The Potential Risks Of LLMs?](https://www.kdnuggets.com/2023/03/watermarking-help-mitigate-potential-risks-llms.html): **KD Nuggets**
8. [Securing AI Model Weights: Preventing Theft and Misuse of Frontier Models](https://www.rand.org/content/dam/rand/pubs/research_reports/RRA2800/RRA2849-1/RAND_RRA2849-1.pdf): **RAND Corporation**
9. [Sponge Examples: Energy-Latency Attacks on Neural Networks](https://arxiv.org/abs/2006.03463): **arXiv**
10. [Sourcegraph Security Incident on API Limits Manipulation and DoS Attack](https://about.sourcegraph.com/blog/security-update-august-2023): **Sourcegraph**
11. [Clawdrain: Exploiting Tool-Calling Chains for Stealthy Token Exhaustion in OpenClaw Agents](https://arxiv.org/abs/2603.00902): **arXiv**
12. [Resource Consumption Red-Teaming for Large Vision-Language Models](https://arxiv.org/abs/2507.18053): **arXiv**
13. [ThinkTrap: Denial-of-Service Attacks against Black-box LLM Services via Infinite Thinking](https://arxiv.org/abs/2512.07086): **arXiv**
14. [Denial-of-Service Poisoning Attacks against Large Language Models](https://arxiv.org/abs/2410.10760): **arXiv**
15. [Vision — Build with Claude documentation](https://docs.anthropic.com/en/docs/build-with-claude/vision): **Anthropic**
16. [MCP Safety Audit: LLMs with the Model Context Protocol Allow Major Security Exploits](https://arxiv.org/abs/2504.03767): **arXiv**


### Related Frameworks and Taxonomies

| Framework | Reference | Relevance |
|---|---|---|
| **OWASP Top 10 for Agentic Applications (ASI)** | ASI02 — Tool Misuse & Exploitation | Agent-tool interaction loops (Common Example #9) and MCP tool-call fan-out (Scenario #8) let a single request drive recursive or high-volume tool calls that exhaust budget and availability |
| **OWASP Top 10 for Agentic Applications (ASI)** | ASI08 — Cascading Failures | Agentic architectures and tool-use protocols such as MCP "amplify a single request into cascading downstream operations" (Description), illustrated by Scenario #8's fan-out of one task into 50 calls |
| **MITRE CWE** | [CWE-400 — Uncontrolled Resource Consumption](https://cwe.mitre.org/data/definitions/400.html) | Foundational weakness underlying every resource-exhaustion pattern in this entry |
| **MITRE ATLAS** | [AML.TA0000 — ML Model Access](https://atlas.mitre.org/tactics/AML.TA0000) | Tactic covering adversary access to the model, a prerequisite for extraction and resource-exhaustion techniques |
| **MITRE ATLAS** | [AML.T0024 — Exfiltration via ML Inference API](https://atlas.mitre.org/techniques/AML.T0024) | Technique matching Model Extraction and Distillation Theft (Common Example #7) |
| **MITRE ATLAS** | [AML.T0029 — Denial of ML Service](https://atlas.mitre.org/techniques/AML.T0029) | Technique matching input-flood and repeated-request denial-of-service patterns (Common Examples #1, #3, #4; Scenarios #1-#3) |
| **MITRE ATLAS** | [AML.T0034 — Cost Harvesting](https://atlas.mitre.org/techniques/AML.T0034) | Technique matching Denial of Wallet (Common Example #2; Scenario #4) |
| **MITRE ATLAS** | [AML.T0025 — Exfiltration via Cyber Means](https://atlas.mitre.org/techniques/AML.T0025) | Technique matching side-channel harvesting of model weights and architecture (Common Example #8; Scenario #9) |
| **OWASP ML Top 10** | [ML05:2023 — Model Theft](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML05_2023-Model_Theft.html) | Closest peer risk for model extraction and functional replication |
| **OWASP API Security Top 10** | [API4:2023 — Unrestricted Resource Consumption](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/) | API-layer control peer for rate limiting and resource-consumption caps |
| **OWASP Secure Coding Practices** | [OWASP Resource Management](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/) | General secure-coding guidance on resource-management controls |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI17 — Data Availability & Resilience Failures in AI Pipelines | Anchored to its "vector DB saturation under adversarial or high-cardinality query load" clause, which parallels this entry's resource-exhaustion and availability-disruption risk |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI20 — Model Exfiltration & IP Replication | Matches Functional Model Replication (Common Example #7; Scenario #5) and low-and-slow distillation extraction (Scenario #10) |
