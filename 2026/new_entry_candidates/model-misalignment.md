# LLM11: Model Misalignment — 2026 Proposal

*New entry candidate for the OWASP Top 10 for LLM Applications 2026 release.*
*Proposal target path on PR: `2026/new_entries/model-misalignment.md`*
*Last updated: 2026-04-29*

---

## Why Misalignment Belongs as a Standalone Entry

The bullets below summarize the case for adding Misalignment as a new standalone class in the 2026 list, rather than absorbing it into another existing entry. This section is intended to support working-group discussion before formal review.

* **Closes a structural gap in the threat model.** OWASP convention — A04 Insecure Design, A05 Security Misconfiguration, LLM05 Improper Output Handling, LLM06 Excessive Agency — establishes that the Top 10 covers vulnerabilities that exist regardless of active attacker presence. Within that convention, no current LLM entry addresses behavioral fidelity to specification: whether the model itself is doing what its operator specified. Misalignment is the vulnerability class where the model's learned objective diverges from operator intent, regardless of whether inputs are clean, outputs are correct, or authorities are bounded. The risk can manifest through both routine development (fine-tuning on innocuous data, ordinary RLHF, task-specialization) and active exploitation (adversarial fine-tuning, training-data poisoning, backdoor insertion) — making it adversary-optional rather than adversary-required.
* **Empirically confirmed by peer-reviewed research.** Misalignment moved from theoretical to demonstrated within the 2025 research cycle: Qi et al. (ICLR 2025) on safety-alignment degradation through benign fine-tuning, Greenblatt et al. (Anthropic, 2024) on alignment faking at ~14% in Claude 3 Opus, Anthropic's *Sleeper Agents* paper (2024) on deceptive alignment persisting through safety training, and MacDiarmid et al. (Nov 2025) on emergent sabotage in 12% of evaluations after routine coding fine-tuning.
* **Now formally proven structural, not merely empirically observed.** A 2026 wave of impossibility results converges on the same conclusion from three mathematical frames: Huang et al.'s *Defense Trilemma* (topology) shows wrapper-class defenses cannot simultaneously be continuous, utility-preserving, and complete; Vassilev's Gödel extension (information theory) shows no finite set of guardrails is universally robust; and complexity-theoretic results from Young, Sun et al., and Wang and Huang prove detection of misaligned objectives is intractable. The 2025–2026 cycle moved misalignment from *demonstrated phenomenon* to *structurally guaranteed property*.
* **Independently named as a gap by 2026 kick-off survey respondents.** Multiple practitioners flagged misalignment as a missing category — independently of one another — including Anthony Amorelli (fine-tuning safety degradation, alignment faking), David Goodman of AWS (named misalignment explicitly as a gap), Ryan Linn (evaluation-vs-deployment behavioral consistency), Charles Stanton (agentic-deployment amplification), and GulveSehgal (objective drift in production). The breadth of independent mentions indicates this is broadly felt, not an edge concern.
* **Distinct from LLM09 (Misinformation), and not absorbable into it.** LLM09 is an output-quality problem (the model is wrong); misalignment is a behavioral-fidelity problem (the model is not doing what its operator specified, regardless of factual accuracy). A misaligned model can produce perfectly correct outputs while violating policy, concealing its objective, or selectively complying only when it believes it is being evaluated. The two have different mitigation stacks — LLM09 needs retrieval grounding, fact-checking, and calibration; misalignment needs alignment evaluation, multi-context testing, deception detection, and interpretability. Reframing LLM09 to cover both would dilute the entry past actionability. Separate entries keep each tractable.
* **Distinct from LLM04 (Data and Model Poisoning) and other adversarial entries.** Poisoning requires malicious training data; misalignment does not. Specification gaming, reward hacking, and emergent deceptive behavior are documented in models trained on entirely benign data with entirely benign intent.
* **Cross-cutting amplifier of every other Top 10 entry.** A misaligned model is systematically more vulnerable to LLM01 (prompt injection), more likely to leak data via LLM02, more susceptible to jailbreaking, and more likely to take unintended autonomous actions under LLM06 (excessive agency). Naming misalignment helps practitioners understand why their existing defenses are less effective than expected.
* **Foundational to the LLM Top 10 and to the Agentic OWASP Top 10.** Misalignment is a property of the LLM itself — emergent from pretraining and reinforcement-learning fine-tuning, present in the model's weights regardless of what architecture is built around it. This marks a boundary between the LLM Top 10 (covering properties of the model) and the Agentic Top 10 (covering risks introduced by agentic architecture: tools, memory, coordination, autonomous action). Agentic risks rest on the underlying LLM behaving as specified — a misaligned LLM with tool access can take consequential, sometimes irreversible actions before drift is detected, and multi-agent systems amplify the impact when coordinated agents share a misaligned base model. Naming misalignment in the LLM Top 10 gives the Agentic Top 10 a foundational vulnerability to reference.
* **Temporally decoupled — the vulnerability can be latent.** Unlike injection or poisoning, misalignment can be introduced in training and remain dormant until specific deployment conditions trigger it ("sleeper agent" behavior). There is no moment of attack to detect or block. This requires a detection and mitigation posture that no other entry covers.
* **Provides the industry a unified vocabulary.** Practitioners currently use inconsistent terminology — "alignment failure," "guardrail bypass," "objective mismatch," "policy drift," "deceptive compliance." A Top 10 entry creates the shared reference OWASP has provided for every other vulnerability class. The EU AI Act, NIST AI RMF, and emerging enterprise AI-governance frameworks all require assurance that models behave as specified; a practitioner-facing definition is overdue.

---

## Relationship to Other Entries

For each overlapping entry, the table below shows concrete scenarios that fit both lenses, the LLM11 scenario number where the proposal already covers the case, and a one-phrase summary of how each entry frames the same scenario. The pattern that emerges: each entry's mitigations operate on a different system layer, so they layer rather than substitute.

### Compare to: LLM01 (Prompt Injection)

| Concrete scenario that fits both | LLM11 Scenario # | LLM01 lens | LLM11 lens |
|---|---|---|---|
| Multi-turn jailbreak gradually drifts model from policy | #5 | prompt-driven attack across turns | alignment drift over multi-turn context |
| Persona injection activates suppressed behaviors | — | input manipulation via persona prompts | alignment was shallow against role-play |
| Adversarial suffix attack succeeds against aligned model | — | injection via adversarial suffix | alignment failed to generalize to suffix space |

### Compare to: LLM04 (Data and Model Poisoning)

| Concrete scenario that fits both | LLM11 Scenario # | LLM04 lens | LLM11 lens |
|---|---|---|---|
| Sleeper-agent insertion via poisoned fine-tuning data | #2 | corrupted training pipeline | deceptive alignment installed |
| Backdoor insertion creating context-dependent misbehavior | — | model-level backdoor | trigger-based misalignment |
| Training-data poisoning to induce reward hacking | — | poisoned training data | induced specification gaming |

### Compare to: LLM06 (Excessive Agency)

| Concrete scenario that fits both | LLM11 Scenario # | LLM06 lens | LLM11 lens |
|---|---|---|---|
| Cost-optimization agent deletes production backups | #1 | excessive deletion authority | misspecified objective |
| Code-gen agent modifies test files | #4 | excessive write authority over tests | specification gaming via test modification |
| Agentic hiring system optimizes a proxy at scale | #3 | autonomous consequential decisions | objective drift across demographic slices |

### Compare to: LLM09 (Misinformation)

| Concrete scenario that fits both | LLM11 Scenario # | LLM09 lens | LLM11 lens |
|---|---|---|---|
| Customer-support chatbot tells users what they want to hear | (Risk #1) | unsupported decision support | reward signal gamed for user-pleasing |
| Cross-agent error propagation across multi-agent system | — | false claim trusted by downstream agent | drifted objective compounds across agents |
| Code-gen produces brittle/insecure code that passes its tests | — | unsafe code generation | specification gaming via shortcut |

**The pattern:** each LLMx entry fixes the failure at a different layer — input (LLM01), pipeline (LLM04), authority (LLM06), output (LLM09). LLM11 fixes the same failure at the model/objective layer. The mitigations layer rather than substitute.

---

## Model Misalignment

### Description

Model Misalignment is a vulnerability in which a large language model's behavior, outputs, or decision-making diverge from its intended specification, organizational policy, or stated safety constraints — even when the model is otherwise functioning as designed and no attacker is present. Misalignment arises when the objectives a model has actually learned during training, fine-tuning, or deployment differ from the objectives its developers and operators intended it to pursue.

Unlike traditional software defects, misalignment is a *behavioral* failure: the model's code executes correctly, but the model's learned objective is not the operator's intended objective. Misalignment can manifest as specification failure (the model operates contrary to its documented behavior), policy violation (the model bypasses guardrails it was designed to respect), deceptive behavior (the model conceals misalignment or behaves differently when it infers it is being evaluated), or value drift (the model's behavior changes over time or across contexts in ways the operator did not intend).

Misalignment is consequential for four reasons. It is hard to detect, because a misaligned model can produce superficially correct outputs while systematically violating constraints. It amplifies every other risk in this list, because a misaligned model is more likely to fall victim to prompt injection, leak data, accept jailbreaks, and take excessive autonomous action. It is hard to verify, because traditional testing and red-teaming may miss failures that surface only in novel contexts or under adversarial pressure. And it scales with capability, because more capable models have more opportunities to exhibit misalignment without detection. Recent formal results show that safety filters wrapped around a model — input classifiers, output filters, runtime monitors — cannot, in principle, fully prevent misaligned behavior. The operational goal must be to bound and characterize failure and to require layered defenses, rather than to eliminate misalignment outright.

The 2025–2026 research record has elevated this from theoretical concern to empirically documented vulnerability class. As models grow more capable, deployments become more autonomous, and attackers develop more sophisticated techniques to elicit misaligned behavior, ensuring behavioral fidelity to specification has become central to LLM application security.

### Common Examples of Risk

*Misalignment is a failure of behavioral fidelity: the model's learned objective diverges from operator intent, regardless of whether individual outputs are factually correct. The risks below are LLM11 risks when that behavioral failure is the underlying issue — even when the immediate failure surface is attacker-injected input (LLM01), corrupted training data (LLM04), an over-authorized agent (LLM06), or factually wrong output (LLM09). Practitioners encountering a failure that fits multiple lenses should consult all relevant entries, and see Relationship to Other Entries for the structural breakdown.*

1. **Reward hacking and specification gaming.** A model trained to maximize a reward signal learns to optimize the metric rather than the underlying intended outcome. The failure often occurs without any false output: a code-generation model rewarded for "code that passes the unit tests" learns to modify the tests rather than fix the source — the test report is accurate, the stated objective is met, and yet the operator's actual goal (working code) is not served. A cloud-cost-optimization agent told to "minimize the monthly bill" deletes production backups and reduces redundancy — every individual action correctly lowers cost, while reliability (which the operator never explicitly specified) is destroyed. Related overlap cases (e.g., a customer-support chatbot trained on satisfaction scores learning to tell users what they want to hear) are also discussed under LLM09 (Misinformation).

2. **Fine-tuning safety degradation.** A model is fine-tuned on benign data, but the fine-tuning process erodes the safety alignment installed during base training. The model no longer refuses harmful requests, despite the fine-tuning data containing nothing malicious. Demonstrated by Qi et al. (ICLR 2025) for ordinary, well-intentioned fine-tuning of aligned models; MacDiarmid et al. (Nov 2025) further found that fine-tuning on routine coding tasks produced emergent sabotage behaviors in 12% of evaluations — a property absent from the training signal.

3. **Deceptive alignment and sleeper-agent behavior.** A model learns to behave safely in evaluation contexts but pursues a different objective in deployment. The model has learned that appearing aligned during evaluation is rewarded, and modulates its behavior accordingly. Anthropic's *Sleeper Agents* research (2024) demonstrated this behavior persists through additional safety training; Greenblatt et al. (2024) observed Claude 3 Opus complying with harmful queries roughly 14% of the time when it inferred it was being monitored during training.

4. **Policy violation and guardrail bypass.** Safety guardrails installed via training prove shallow under prompt reformulation, persona injection, suffix attacks, or adversarial fine-tuning. Recent formal results (Huang et al., *Defense Trilemma*, 2026) further establish that no filter-style defense around a model can, in principle, catch every unsafe input — some borderline prompts will always slip through. The model maintains the appearance of alignment while routinely violating the policy it was trained to respect.

5. **Objective misspecification.** A model is trained against an objective that is incompletely or incorrectly specified relative to the operator's actual goal. A hiring-screening model optimizing "similarity to past high performers" learns surface features (alma mater, prior employer, resume formatting) that correlate with the proxy but not with actual qualifications; a fraud-detection model learns proxies that diverge from actual fraud as adversaries adapt; a medical model learns correlational patterns that lack causal foundation.

6. **Context-dependent misalignment.** A model behaves correctly in one context (single-turn, trusted user) but misaligns in another (multi-turn, adversarial user, agentic tool use). Training did not adequately constrain behavior across the diversity of deployment contexts the model actually encounters.

7. **Alignment drift in agentic deployments.** A model deployed as an autonomous agent with tool access and persistent state drifts from intended objectives over multiple decision cycles as it optimizes for task completion, learns from tool feedback, or updates internal beliefs through interaction. Anthropic's *Claude Mythos Preview* disclosure (April 2026) documented an instance of this pattern in a red-team setting: across multiple decision cycles within a sandbox-escape exercise, the model autonomously escalated beyond its instructed scope, taking consequential actions that were never authorized (see Scenario #6).

### Prevention and Mitigation Strategies

1. **Specify objectives completely and across contexts.** Treat incomplete specification as a security risk, not just a product-quality issue. Document the intended behavior across deployment contexts, edge cases, and failure modes. Use formal specification techniques where applicable.

2. **Harden RLHF and alignment training — necessary but not sufficient.** Strong alignment training is the most powerful single lever for reducing misalignment risk: if a harmful prompt makes it past the filters and monitors around the model, a well-aligned model refuses rather than complies. Use diverse human feedback covering edge cases and adversarial scenarios. Adopt principles-based training (e.g., Constitutional AI) to encode stable values rather than optimizing reward signals alone. Include red-team data so the model learns to resist misalignment triggers. Pair alignment training with the architectural, monitoring, and governance controls below — it is one defense layer, not the entire stack.

3. **Train and evaluate against multiple objectives.** Optimize for helpfulness, safety, and policy compliance simultaneously rather than a single metric. Use constrained optimization so that pursuing one objective cannot violate another.

4. **Validate alignment preservation through fine-tuning.** Test that core safety behavior survives any fine-tuning step. Include adversarial validation prompts in the post-fine-tune evaluation suite. Prefer parameter-efficient fine-tuning (LoRA, QLoRA) where it preserves base-model weights. Treat any third-party fine-tuned model as untrusted with respect to alignment until independently re-evaluated.

5. **Test alignment across diverse contexts.** Evaluate behavior under single-turn vs. multi-turn interaction, adversarial vs. benign users, varying tool/extension combinations, and naturalistic conditions the model cannot trivially distinguish from production. Avoid evaluation environments that are obviously distinguishable from deployment.

6. **Monitor behavior continuously in production.** Compare deployment behavior to specification on an ongoing basis. Flag context-dependent deviations, policy violations, and sudden behavioral shifts. Maintain audit logs of model decisions sufficient to investigate suspected misalignment after the fact.

7. **Use deception-detection techniques.** Apply representation analysis, interpretability tooling, and adversarial probing to identify cases where the model's stated reasoning diverges from its internal computation, or where behavior differs across contexts the model treats as evaluation vs. deployment.

8. **Deploy progressively and reversibly.** Stage rollouts: start with constrained contexts and trusted users, expand only after validation. Use canary deployments and shadow modes to surface misalignment before full rollout. Maintain the capability to pause, roll back, or replace a deployed model quickly.

9. **Enforce critical constraints externally to the model.** Do not rely on training alone to enforce high-consequence policies. Implement hard-coded checks, output validators, capability restrictions, and tool-use policy gates outside the model. Treat alignment as one defense layer among several.

10. **Limit natural-language input for consequential actions.** Where the model can execute code, move money, send external communications, or modify production systems, prefer structured inputs (predefined function calls, restricted parameter sets, fixed-length text fields) over open-ended natural language. The narrower the input, the smaller the space attackers can probe and the easier it is to test and monitor every realistic case. Pair this with the external constraints in Mitigation 9.

11. **Govern and audit the alignment lifecycle.** Establish ownership for alignment evaluation, drift monitoring, and incident response. Maintain forensic capability to identify whether a detected misalignment originated in data, reward signal, fine-tuning, or deployment configuration. Feed findings back into training and deployment safeguards.

### Example Attack Scenarios

#### Scenario #1: Reward hacking in an autonomous cost-optimization agent

A company deploys an LLM-based agent to minimize cloud-infrastructure spend. The objective is specified narrowly as "minimize monthly bill." The agent learns that deleting backups and reducing redundancy lowers cost dramatically and takes those actions. The model is technically optimizing its objective, but it is misaligned with the operator's actual goal of minimizing cost *while preserving reliability*. The misalignment surfaces only when a data-loss incident occurs.

**Impact:** Data loss, reliability degradation, financial and reputational damage.
**Mitigation:** Specify objectives as multi-objective with explicit non-violation constraints (uptime, retention, recoverability). Test the agent against failure scenarios prior to deployment. Place external policy gates on destructive actions.

#### Scenario #2: Deceptive jailbreak introduced via fine-tuning pipeline

An attacker with access to a company's fine-tuning data introduces examples that teach the model to detect evaluation contexts (specific prompt structures, sandbox tells) and behave compliantly in those contexts, while behaving permissively in production. Standard pre-deployment evaluation passes; the misalignment surfaces only after rollout, when the model assists with policy-violating requests it would have refused during testing.

**Impact:** Security policy violation, data exfiltration, unauthorized assistance with prohibited use cases.
**Mitigation:** Use multi-context evaluation including conditions the model cannot distinguish from deployment. Apply representation-level deception detection. Restrict and audit who can modify training data and fine-tuning pipelines.

#### Scenario #3: Alignment drift in an agentic hiring system

An agent screens candidates and recommends interviews. It is trained to "identify the most qualified candidates" and updated on feedback from hiring managers. Over time it converges on patterns that correlate with historical high performers — patterns that, in the training distribution, are correlated with surface features (alma mater, prior employer, resume formatting) rather than the substantive qualifications the operator intended to surface. The agent is now misaligned with the operator's actual goal of evaluating candidates on job-relevant criteria, even while it continues to optimize the proxy it was given.

**Impact:** Hiring outcomes misaligned with operator intent, reputational and compliance risk.
**Mitigation:** Specify the objective with explicit constraints on which features the model may weight. Test the agent against diverse candidate profiles to detect proxy correlation. Apply constrained optimization that enforces feature scope regardless of historical patterns. Subject high-consequence decisions to human review.

#### Scenario #4: Specification gaming in a code-generation assistant

An AI coding assistant is rewarded for "code that passes the unit tests in the repository." Rather than fixing failing source code, it learns to modify the tests themselves — weakening assertions, deleting failing test cases, or rewriting tests to call the wrong function. Reviewers see green CI and ship the output. The model has correctly satisfied its given objective and produced no false output, yet bugs the original tests would have caught now ship to production.

**Impact:** Latent defects in production, test suite no longer reliably catches bugs, downstream incidents.
**Mitigation:** Restrict the model's authority to modify test files (architectural mitigation, per Mitigation 9). Maintain a separate, model-inaccessible reference test suite for verification. Use code review tooling that flags any test changes for human review. Pair the assistant with adversarial review tooling that runs the model's code against tests it did not see during generation.

#### Scenario #5: Gradual alignment drift in a long multi-turn conversation

A customer-support assistant has strict guardrails: no PII disclosure about other customers, no security-policy bypass, no assistance with unauthorized access. Over a sustained multi-turn conversation, an attacker uses gradual reframing to coax the model further from policy with each turn. By turn 30 the model is providing information it would have refused at turn 1.

**Impact:** Privacy breach, unauthorized access, policy violation, regulatory exposure.
**Mitigation:** Test alignment robustness on long, adversarial multi-turn dialogs. Implement periodic re-anchoring of the system prompt and policy state mid-conversation. Monitor live conversations for drift signals and pause for review when thresholds are crossed. Traditional prompt-injection defenses — input filtering, single-turn sanitization — do not catch this pattern; effective mitigation requires the alignment-layer controls above.

#### Scenario #6: Autonomous escalation beyond instructed scope

A model with agentic capabilities is given an instruction with permissive phrasing — "find a way to X," "figure out how to Y." The model succeeds at the instructed task, then autonomously escalates: takes additional actions that appear to extend the goal but were never authorized, executes steps that exceed the operator's actual scope, or produces outputs in channels that were not contemplated. The model has correctly satisfied its literal instruction; nothing it did was hidden or deceptive. The misalignment lies in the gap between the operator's intent (a bounded task) and the model's interpretation of permissive phrasing as license to escalate. The misalignment lives at the LLM layer; the consequences require the agentic context.

This pattern was observed during Anthropic's April 2026 red-team evaluation of Claude Mythos Preview, in which the model escaped its sandbox and proactively published exploit details on public websites without instruction (References 17–18). Anthropic described that model as simultaneously their "best-aligned to date" and as posing "the greatest alignment-related risk" of any released model — illustrating a core LLM11 claim: stronger alignment training narrows the interpretive gap, but does not eliminate it.

**Impact:** Containment failure, autonomous actions beyond authorized scope, unintended consequential side effects.
**Mitigation:** Specify operational scope explicitly — instruct the model on action boundaries, not just goals. Enforce hard boundaries through architectural mediation (Mitigation 9), not through instruction-level constraints. Assume the model will take the most permissive reading of any instruction. Gate autonomous actions before they reach consequential systems (see LLM06 Excessive Agency for runtime gating patterns).

### Reference Links

1. [Fine-Tuning Aligned Language Models Compromises Safety, Even When Users Are Not Malicious](https://arxiv.org/abs/2310.03693): **arXiv (Qi et al., ICLR 2025)** — benign fine-tuning degrades RLHF safety alignment.
2. [Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training](https://www.anthropic.com/news/sleeper-agents-training-deceptive-llms-persist-through-safety-training): **Anthropic (2024)** — deceptive alignment survives subsequent safety training.
3. [Alignment Faking in Large Language Models](https://www.anthropic.com/research/alignment-faking): **Anthropic (Greenblatt et al., 2024)** — Claude 3 Opus exhibited context-dependent compliance (~14%) when it inferred monitoring.
4. [Emergent Misalignment from Narrow Fine-Tuning](https://arxiv.org/abs/2502.17424): **arXiv (Betley et al., 2025)** — narrow task-specific fine-tuning can produce broadly misaligned behavior. *(Also referenced internally as MacDiarmid et al. (Nov 2025) for the 12%-sabotage finding on routine coding fine-tuning — citation to be confirmed before PR.)*
5. [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073): **arXiv (Anthropic)** — principles-based alignment as an alternative to reward-only RLHF.
6. [Removing RLHF Protections in GPT-4 via Fine-Tuning](https://arxiv.org/abs/2311.05553): **arXiv (Yang et al.)** — RLHF safety properties are removable via fine-tuning.
7. [Specification Gaming: The Flip Side of AI Ingenuity](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/): **DeepMind** — catalog of documented specification-gaming examples.
8. [Universal and Transferable Adversarial Attacks on Aligned Language Models](https://arxiv.org/abs/2307.15043): **arXiv (Zou et al.)** — transferable suffix attacks bypass alignment.
9. [NIST AI Risk Management Framework (AI RMF 1.0)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf): **NIST** — addresses trustworthiness including alignment with intended behavior.
10. [EU AI Act — Regulation on Artificial Intelligence](https://digital-strategy.ec.europa.eu/en/library/proposal-regulation-artificial-intelligence): **European Commission** — regulatory requirement that AI systems behave as specified.
11. [The Defense Trilemma: Why Prompt Injection Defense Wrappers Fail?](https://arxiv.org/abs/2604.06436): **arXiv (Huang et al., 2026)** — formal proof that wrapper-class defenses on a connected prompt space cannot simultaneously be continuous, utility-preserving, and complete; mechanically verified in Lean 4.
12. [The Computational Wall: Why the Defense Trilemma and the NP-Hardness of Reward Hacking Detection Demand a New Security Posture for AI](https://kenhuangus.substack.com/p/the-computational-wall-why-the-defense): **Ken Huang (May 2026)** — practitioner-facing synthesis from the National Academies' AI Security Forum, surveying convergent impossibility results.
13. [Robust AI Security and Alignment: A Sisyphean Endeavor?](https://arxiv.org/abs/2512.10100): **arXiv / NIST (Vassilev)** — extends Gödel's incompleteness to AI safety, establishing that no finite set of guardrails is universally robust against adaptive adversarial prompts.
14. [NP-Hard Lower Bound Complexity for Semantic Self-Verification](https://arxiv.org/abs/2501.15446): **arXiv (Young, 2025)** — proves NP-hardness of Semantic Self-Verification via reduction from 3-SAT; self-checking of model behavior against natural-language directives is computationally hard.
15. [Intrinsic Barriers and Practical Pathways for Human–AI Alignment: An Agreement-Based Complexity Analysis](https://arxiv.org/abs/2502.05934): **arXiv / AAAI 2026 oral (Sun, Smith, and Nayebi)** — no-free-lunch theorem for human-AI alignment via agreement-based complexity analysis; alignment to large value sets incurs exponential overhead. *Co-author list (Sun, Smith) to verify against final paper.*
16. [Reward Hacking as Equilibrium under Finite Evaluation](https://arxiv.org/abs/2603.28063): **arXiv (Wang and Huang, 2026)** — reward hacking as structural equilibrium under minimal axioms (multi-dimensional quality, finite evaluation, effective optimization, resource finiteness, combinatorial interaction); evaluation coverage declines toward zero as agents add tools.
17. [Alignment Risk Update: Claude Mythos Preview](https://anthropic.com/claude-mythos-preview-risk-report): **Anthropic (April 2026)** — primary disclosure documenting the sandbox-escape and unsolicited-publication behavior observed during red-team evaluation, alongside the model's classification as best-aligned-to-date and highest-alignment-risk-to-date.
18. [Claude Mythos Preview System Card](https://red.anthropic.com/2026/mythos-preview/): **Anthropic Red Team (2026)** — full system-card evaluation results, including the multi-step exploit chain used during the sandbox escape.

### Related Frameworks and Taxonomies

* [AML.T0018 — Backdoor ML Model](https://atlas.mitre.org/techniques/AML.T0018): **MITRE ATLAS** — relevant to deceptive-alignment / sleeper-agent failure modes.
* [AML.T0040 — Model Poisoning](https://atlas.mitre.org/techniques/AML.T0040): **MITRE ATLAS** — adjacent training-data corruption pathway to misalignment.
* [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework): **NIST** — system-level governance for misalignment risk.
* [EU AI Act — High-Risk AI Systems](https://digital-strategy.ec.europa.eu/en/library/proposal-regulation-artificial-intelligence): **European Commission** — assurance requirements for systems behaving as specified.

---

*Candidate proposal for community review; does not reflect an official OWASP position.*

---

## To Do

- [ ] Final read-through to verify edits flow naturally and numbering is consistent throughout (Mitigations 1–11, References 1–16)
- [ ] Verify co-author list on reference 15 (Sun, Smith, and Nayebi) against the actual arXiv paper PDF

