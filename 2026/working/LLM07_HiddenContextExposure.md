## LLM07:2026 Hidden Context Exposure

### Description

Hidden Context Exposure is the unauthorized extraction, inference, or reconstruction of hidden, non-user-facing system instructions or operational context placed in a model's context. It becomes security-relevant when that hidden context contains or reveals secrets, policy logic, tools, trust boundaries, workflow criteria, proprietary behavior, or other sensitive implementation details that materially increase attacker capability.

In an LLM application, hidden context typically includes the system prompt, developer instructions, retrieved policy text (from RAG knowledge bases, configuration stores, or user-profile services), the schemas of tools and functions the application exposes to the model, and other rules, directives, and materials the application assembles into the model's context window. The common thread is that this hidden context is not intended to be visible to end users but is accessible to the model.

Practitioners should design under the assumption that hidden context is discoverable and that any contents of the context should not be considered a secret. Application developers should ensure that its full disclosure would have no or minimal direct security impact. Sensitive data such as credentials, connection strings, and tokens should not be embedded in it, nor should hidden context be solely relied upon as a security boundary for authorization, privilege separation, policy enforcement, or content filtering.

Severity tracks what is placed in hidden context and how the application relies on it. Findings range from **informational** (no secrets, no security-relevant logic, no reliance on confidentiality) through **medium** (internal rules, filtering criteria, role descriptions, or workflow logic that meaningfully aids an attacker but does not gate critical decisions) to **high** (embedded credentials or tokens, or reliance on hidden-context secrecy for authorization or content policy) and **critical** (where disclosure chains to remote code execution, broad data exfiltration, or privilege escalation in a connected system).

While Hidden Context Exposure introduces risks on its own, it also frequently amplifies risks in adjacent categories: disclosed rules or logic enable more targeted prompt injection (LLM01); embedded credentials constitute sensitive information disclosure (LLM02); revealed tool permissions and schemas expand the surface for excessive agency (LLM06); leaked output-formatting rules can facilitate improper output handling (LLM05).

In summary, LLM07 covers the foundational risk that hidden LLM control context is exposed, inferred, or reconstructed in a way that materially increases attacker capability. LLM07 does not cover:

* The leakage of regulated user or training data (LLM02:2025 Sensitive Information Disclosure).
* The agentic amplifications of this risk, e.g., persistent memory, inter-agent channels, tool configuration persistence, and multi-step agent compromise (the OWASP Top 10 for Agentic Applications).
* Generic application-security concerns inherited by LLM-integrated systems, e.g., server-side log leakage, client-side bundle inspection, and infrastructure-layer side channels.

### Common Examples of Risk

#### 1. Exposure of Sensitive Functionality, Tool and Function Schemas

The system prompt or hidden context of the application may reveal sensitive information or functionality that is intended to be kept confidential, such as sensitive system architecture, available tools and functions, API keys, database credentials, or user tokens. While exposure of these would likely cause harm, the real risk is that sensitive credentials are placed in the hidden context in the first place. Since the hidden context should be considered discoverable, any information that could be used for further attacks should be removed.

#### 2. Exposure of Behavioral Control Logic

The context of the application includes information on internal decision-making processes that should be kept confidential. This information allows attackers to gain insights into how the application works, which they could use to exploit weaknesses or bypass controls in the application.

#### 3. Reverse Engineering of Safety and Refusal Mechanisms

System prompts can define the conditions under which a model should refuse or filter content. When these instructions are exposed through system prompt leakage, attackers gain visibility into the rules that govern refusal behavior. While a typical user may only observe responses such as "Sorry, I can't do that," leakage reveals the underlying triggers, conditions, and exceptions that led to that decision. This allows attackers to craft inputs that intentionally avoid known refusal patterns or exploit gaps in enforcement, increasing the likelihood of obtaining responses that would otherwise be restricted.

#### 4. Disclosure of Permissions and User Roles

Instruction context could include directives or information related to authorization and permissions. For example, a tool description provided through an internal-facing MCP server may indicate that a user must have the developer role in order to use it, or that a user with a certain role can access a list of documents to search with RAG. The disclosure of such information could invite other types of probing through directed conversation and prompt injection (LLM01) and could potentially reveal additional sensitive information (LLM02).

#### 5. Exposure of Output Structure and Formatting Rules

System prompts frequently define how responses should be structured, including required formats such as JSON schemas, templates, or validation constraints. When these instructions are exposed, attackers gain insight into how outputs are constructed and what assumptions downstream systems rely on. This knowledge can be used to generate responses that conform to expected formats while embedding unintended or manipulated values, potentially leading to incorrect parsing or unintended system behavior.

### Prevention and Mitigation Strategies

#### 1. Do Not Put Sensitive Data in Hidden Context

Do not embed any sensitive information (e.g., API keys, auth keys, database names, user roles, permission structure of the application) directly in the system prompts or hidden context. Assume all context available to the LLM could also be available to users. Instead, externalize such information to the systems that the model does not directly access and avoid letting the model handle sensitive data itself.

#### 2. Use Deterministic Methods for Behavior Control

Because LLMs can be vulnerable to attacks such as prompt injection, hidden context should not be relied on as the primary mechanism for controlling model behavior. Instead, enforce critical behaviors through deterministic systems outside the model. For example, harmful content detection and prevention should be handled by external safeguards rather than by instructions embedded in hidden context.

#### 3. Validate Model Inputs and Outputs with External Guardrails

Implement external guardrails that inspect user inputs, model outputs, and tool calls for policy violations or unexpected behavior. While training particular behavior into a model can be effective, such as training it not to reveal its system prompt, it does not guarantee consistent compliance. An independent system that can inspect the output to determine if the model is in compliance with expectations is preferable to system prompt instructions.

#### 4. Enforce Authorization and Access Control Independently from the LLM

Critical controls such as privilege separation, authorization bounds checks, and similar must not be delegated to the LLM, whether through the system prompt or another mechanism. These controls should be enforced in a deterministic and auditable manner, which LLMs are not well suited to provide. In cases where an agent is performing tasks, if those tasks require different levels of access, then multiple agents should be used, each configured with the least privileges needed to perform the desired tasks.

#### 5. Adopt Context Obfuscation

For context the application must process, avoid relying on common system prompt templates, section names, or predictable instruction structures. Varying how instructions are named, written and structured so that they are less directly identifiable or reusable could provide an additional layer of complexity for attackers. Mitigations such as these should only be used as a minor supporting measure, not a primary defense. The best defense is to avoid extraneous and sensitive context and assume all context is discoverable.

### Example Attack Scenarios

#### Scenario #1

An LLM has a system prompt that contains a set of credentials used for a tool that it has been given access to. The system prompt is leaked to an attacker, who is then able to use these credentials for other purposes.

#### Scenario #2

An attacker extracts the hidden context that contains the tool list and parameter schemas through conversational probing and uses the information to craft inputs that steer the application toward specific tool calls. No credential is disclosed and no policy is overtly bypassed, but the attacker now has concrete targets for subsequent prompt injection attempts and reconnaissance for downstream action chaining.

#### Scenario #3

An LLM has a system prompt prohibiting the generation of offensive content, external links, and code execution. An attacker extracts this system prompt and then uses a prompt injection attack to bypass these instructions, facilitating a remote code execution attack.

### Reference Links

1. [System Prompt Poisoning: Persistent Attacks on Large Language Models Beyond User Injection](https://arxiv.org/abs/2505.06493): Li, Guo, & Cai, **arXiv:2505.06493** (2025).
2. [You Can't Steal Nothing: Mitigating Prompt Leakages in LLMs via System Vectors](https://arxiv.org/abs/2509.21884): Cao, Li, Cao, Ge, Wang, & Chen, **arXiv:2509.21884**.
3. [PLeak: Prompt Leaking Attacks against Large Language Model Applications](https://arxiv.org/abs/2405.06823): Hui, Yuan, Gong, Burlina, & Cao, **arXiv:2405.06823** (2025).
4. [LeakAgent: RL-based Red-teaming Agent for LLM Privacy Leakage](https://arxiv.org/abs/2412.05734): Nie, Wang, Yu, Wu, Zhao, Guo, & Song, **arXiv:2412.05734** (2025).
5. [Proof of Concept: Dangers of System Prompt Leakage](https://resk.fr/pdf/resk-enterprise-ai-security-guide.pdf): Jeremy Goffin, **Resk.fr**, July 2025.
6. [Just Ask: Curious Code Agents Reveal System Prompts in Frontier LLMs](https://doi.org/10.48550/arXiv.2601.21233): Zheng, Wu, Huang, Li, Ma, Li, Jiang, & Wang, **arXiv:2601.21233** (2026).
7. [System Prompt Extraction Attacks and Defenses in Large Language Models](https://arxiv.org/abs/2505.23817): Das, Amini, & Wu, **arXiv:2505.23817** (2025).
8. [Leaked System Prompts (GitHub repository)](https://github.com/jujumilk3/leaked-system-prompts): **jujumilk3** (2025).
9. [LeakHub](https://leakhub.ai/): **LeakHub**.

### Related Frameworks and Taxonomies

Refer to this section for comprehensive information, scenarios, and strategies relating to infrastructure deployment, applied environment controls, and other best practices.

MITRE ATLAS

* AML.T0051.000 — LLM Prompt Injection: Direct (Meta Prompt Extraction)
* AML.T0057 — LLM Data Leakage
