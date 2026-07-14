## LLM07:2026 Misinformation

### Description

Misinformation occurs when an LLM or LLM-enabled application produces incorrect, incomplete, unsupported, or misleading information that appears credible enough to influence a human decision, an automated workflow, or an agent action. The core risk is not simply that the model is wrong, but that the incorrect output is trusted and acted upon.

In modern systems, model outputs drive tool calls, generate code, infer system state, authorize actions, and coordinate across agents. This makes misinformation a system-level failure that can lead to financial loss, security incidents, safety risks, or operational disruption.

In agentic systems, misinformation often manifests as incorrect state, reasoning, or evidence that is consumed by downstream components, leading directly to unintended actions.

Misinformation can arise from hallucination, incomplete or stale context, weak grounding, ambiguous prompts, biased or corrupted data, misleading summaries, or unvalidated tool outputs. It can also be deliberately induced by attackers. Where the root cause is prompt injection, poisoning, or supply chain compromise, those risks should be referenced separately. This entry focuses on the resulting failure mode: a false representation that drives a harmful decision or action.

Overreliance remains a key factor. Humans and systems often treat fluent, confident, or well-structured outputs as authoritative. In agentic architectures, this overreliance is frequently embedded in system design.

### Common Examples of Risk

1. Unsupported or False Decision Support: Incorrect or unsupported information influences business, legal, healthcare, financial, or operational decisions.
2. Incorrect State Inference in Workflows: An LLM infers that a condition has been met when it has not, triggering unintended actions.
3. Incorrect or Fabricated Code and Dependencies: The model produces incorrect code recommendations or references non-existent (hallucinated) packages (Spracklen et al., 2025).
4. Misleading Summaries and Critical Omissions: Summaries omit key constraints, exceptions, timestamps, or risks.
5. Adversarially Induced Misinformation: Attackers craft inputs that cause false claims or omission of critical facts.
6. Cross-Agent Misinformation Propagation: Incorrect outputs propagate across agents and workflows.
7. Forged or Misattributed Evidence: Fabricated or manipulated content is presented as authoritative evidence.

### Prevention and Mitigation Strategies

1. Ground Claims Before Action: Require outputs to be grounded in authoritative and current sources.
2. Implement Claim–Check–Act Patterns: Separate generation from execution and verify claims before acting.
3. Validate Tool Calls: Check arguments, authorization, preconditions, and current state before execution.
4. Use Verification Signals (Not Just Confidence): Incorporate groundedness and consistency checks.
5. Enforce Runtime Verification for High-Impact Actions: Introduce approval workflows and system checks.
6. Detect and Prevent Omission Failures: Require structured outputs with mandatory fields.
7. Limit Blast Radius: Apply least privilege, sandboxing, and rate limits.
8. Monitor and Test for Misinformation: Log claims, evidence, and outcomes; test adversarial scenarios.
9. Calibrate Human and System Trust: Distinguish verified facts from assumptions.
10. Adversarial Evaluation and Continuous Testing: Regularly test workflows against misleading scenarios.

### Example Attack Scenarios

#### Scenario #1: Hallucinated Dependency Recommendation

A coding assistant recommends a plausible but non-existent package, which an attacker has pre-registered under the hallucinated name, so a developer who trusts the suggestion installs attacker-controlled code (Spracklen et al., 2025).

#### Scenario #2: Incorrect Policy Decision by Agent

A customer-service agent misreads a policy and approves a refund that violates the terms, resulting in financial loss.

#### Scenario #3: Omission in Safety-Critical Summary

A clinical summary omits a drug contraindication, and a clinician acts on the incomplete recommendation.

#### Scenario #4: Adversarially Induced False Reasoning

An attacker seeds a support forum with false remediation steps that a troubleshooting agent retrieves and repeats as a trusted recommendation.

#### Scenario #5: False Alert Triggers Automated Response

A security agent misclassifies normal traffic as an intrusion and automatically blocks a production network segment, causing an outage.

#### Scenario #6: Cross-Agent Trust Failure

A retrieval agent reports a customer as identity-verified when it is not, and a downstream payment agent trusts that state and releases funds.

#### Scenario #7: Fabricated Task Completion

An agent reports that a nightly database backup completed when it never ran, and a later restore fails because no backup exists.
