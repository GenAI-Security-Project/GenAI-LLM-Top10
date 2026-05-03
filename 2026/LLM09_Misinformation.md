## LLM09: Misinformation

### Description

Misinformation occurs when an LLM or LLM-enabled application produces incorrect, incomplete, unsupported, or misleading information that appears credible enough to influence a human decision, an automated workflow, or an agent action. The core risk is not simply that the model is wrong, but that the incorrect output is trusted and acted upon.

In modern systems, model outputs drive tool calls, generate code, infer system state, authorize actions, and coordinate across agents. This makes misinformation a system-level failure that can lead to financial loss, security incidents, safety risks, or operational disruption.

In agentic systems, misinformation often manifests as incorrect state, reasoning, or evidence that is consumed by downstream components, leading directly to unintended actions.

Misinformation can arise from hallucination, incomplete or stale context, weak grounding, ambiguous prompts, biased or corrupted data, misleading summaries, or unvalidated tool outputs. It can also be deliberately induced by attackers. Where the root cause is prompt injection, poisoning, or supply chain compromise, those risks should be referenced separately. This entry focuses on the resulting failure mode: a false representation that drives a harmful decision or action.

Overreliance remains a key factor. Humans and systems often treat fluent, confident, or well-structured outputs as authoritative. In agentic architectures, this overreliance is frequently embedded in system design.

### Common Examples of Risk

1. Unsupported or False Decision Support: Incorrect or unsupported information influences business, legal, healthcare, financial, or operational decisions.
2. Incorrect State Inference in Workflows: An LLM infers that a condition has been met when it has not, triggering unintended actions.
3. Unsafe Code and Dependency Generation: The model generates insecure code, hallucinated packages, or invalid configurations.
4. Misleading Summaries and Critical Omissions: Summaries omit key constraints, exceptions, timestamps, or risks.
5. Adversarially Induced Misinformation: Attackers craft inputs that cause false claims or omission of critical facts.
6. Cross-Agent Misinformation Propagation: Incorrect outputs propagate across agents and workflows.
7. Forged or Misattributed Evidence: Fabricated or manipulated content is presented as authoritative evidence.

### Prevention and Mitigation Strategies

1. Ground Claims Before Action: Require outputs to be grounded in authoritative and current sources.
2. Implement Claim–Check–Act Patterns: Separate generation from execution and verify claims before acting.
3. Validate Tool Calls Semantically: Ensure alignment with intent, permissions, and real-world state.
4. Use Verification Signals (Not Just Confidence): Incorporate groundedness and consistency checks.
5. Enforce Runtime Verification for High-Impact Actions: Introduce approval workflows and system checks.
6. Detect and Prevent Omission Failures: Require structured outputs with mandatory fields.
7. Limit Blast Radius: Apply least privilege, sandboxing, and rate limits.
8. Monitor and Test for Misinformation: Log claims, evidence, and outcomes; test adversarial scenarios.
9. Calibrate Human and System Trust: Distinguish verified facts from assumptions.
10. Adversarial Evaluation and Continuous Testing: Regularly test workflows against misleading scenarios.

### Example Attack Scenarios

Scenario #1: Hallucinated Dependency Supply Chain Attack  
Attackers publish malicious packages under hallucinated names used by coding assistants, leading to compromise.

Scenario #2: Incorrect Policy Decision by Agent  
An agent incorrectly approves a refund or exception, resulting in financial loss.

Scenario #3: Omission in Safety-Critical Summary  
A summary omits a critical constraint, leading to harmful action.

Scenario #4: Adversarially Induced False Reasoning  
Misleading inputs cause incorrect recommendations that are accepted.

Scenario #5: False Alert Triggers Automated Response  
A system incorrectly detects an attack and disrupts operations.

Scenario #6: Cross-Agent Trust Failure  
One agent passes incorrect state that another trusts, leading to high-impact failure.

Scenario #7: Fabricated Task Completion  
An agent falsely reports task completion, leading to downstream failure.

### Reference Links

1. [LLM09: Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/): **OWASP GenAI Project**
2. [Hallucination Risks in Language Models](https://www.usenix.org/system/files/usenixsecurity25-spracklen.pdf): **USENIX Security Symposium**
3. [PoisonedRAG: Data Poisoning Attacks](https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf): **USENIX Security Symposium**
4. [Why Language Models Hallucinate](https://openai.com/index/why-language-models-hallucinate/): **OpenAI**
5. [Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf): **National Institute of Standards and Technology (NIST)**
6. [AI Hallucinations in the Real World](https://www.bbc.com/news/world-us-canada-68569397): **BBC News**
