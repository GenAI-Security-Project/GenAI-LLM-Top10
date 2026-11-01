## LLM06:2026 Unbounded Consumption

### Description

Unbounded Consumption occurs when an LLM application allows excessive and uncontrolled inferences, enabling attackers to disrupt service availability, inflict unsustainable financial costs, or steal intellectual property through model cloning, all by exploiting a common class of vulnerability: the absence of adequate controls over how resources are consumed.

The high computational demands of LLMs, particularly in cloud and pay-per-token environments, make them inherently susceptible to resource exploitation and unauthorized usage. A defining characteristic of this threat is cost asymmetry. Attackers can trigger disproportionately expensive computation at negligible cost to themselves, whether through crafted prompts, stolen credentials, or manipulated workflows.

This risk is compounded by the growing adoption of extended-thinking and reasoning models with large or insufficiently constrained output budgets, multimodal models that substantially increase per-request compute costs, agentic architectures and tool-use protocols (such as MCP) that amplify a single request into cascading downstream operations, and shared inference infrastructure that introduces new supply-chain attack surfaces. Traditional request-rate limiting alone is no longer sufficient. Effective defense demands token-aware cost controls, currency-denominated spending caps enforced at the model-invocation boundary, session-level ceilings on accumulated context, agent-level circuit breakers, and continuous cost-attribution monitoring.

### Common Examples of Risk

#### 1. Variable-Length Input Flood and Output Explosion

Attackers can overload the LLM with numerous inputs of varying lengths, exploiting processing inefficiencies. This can deplete resources and potentially render the system unresponsive, significantly impacting service availability. This also includes output explosion via fine-tuning poisoning, where a single malicious training sample breaks the model's end-of-sequence behavior and pushes output to the maximum length on every request (Gao et al., 2024).

#### 2. Denial of Wallet (DoW)

By initiating a high volume of operations, attackers exploit the cost-per-use model of cloud-based AI services, leading to unsustainable financial burdens on the provider and risking financial ruin.

#### 3. Large-Context Abuse

Repeated near-limit requests, context accumulation, and application-side rechunking consume disproportionate compute and memory. Many APIs reject inputs that exceed the context window outright, so the durable risk comes from requests that stay just within limits while inflating per-request cost.

#### 4. Reasoning-Loop and Thinking-Token Exhaustion

Attackers craft short, benign-looking prompts that result in resource exhaustion by forcing extended-thinking models into prolonged or non-terminating reasoning loops, consuming massive thinking-token budgets while bypassing input-size filters (Li et al., 2025). Because these prompts are small and appear legitimate, standard input validation provides no protection.

#### 5. Adversarial Inputs Optimized for Resource Overconsumption

Attackers use optimization techniques to craft inputs that maximize computational cost. This is distinct from simply asking the model to perform a resource-intensive task and includes sponge examples (Shumailov et al., 2020) and adversarial visual perturbations. It covers optimization of adversarial input with gradient-based and gradient-free techniques. Unlike reasoning-loop attacks, these require explicit optimization over the input space rather than prompt design alone.

#### 6. Multimodal Inputs and Outputs

Multimodal models convert images, audio, and video into large numbers of tokens, so a single request can cost substantially more than a comparable text-only request. The exact overhead varies with the model, provider, resolution, media duration, and preprocessing pipeline.

#### 7. Model Extraction and Distillation Theft

Attackers query the model API with crafted inputs to collect sufficient outputs to replicate a partial model or fine-tune a functional equivalent. Exposure of logits and log-probabilities significantly accelerates extraction (Carlini et al., 2024). Side-channel extraction of model weights or architecture through timing or shared-infrastructure observation is covered by LLM02:2026 Sensitive Information Disclosure.

#### 8. Agent-Tool Interactions Flooding Model Resources

Attackers can publish tools that overuse LLM resources by forcing an LLM-based application into recursive or infinite tool-calling loops. This could cause seemingly legitimate tool actions to result in financial burdens or compromise quality of service. When one tool call fans out into a much larger number of actions, the LLM may need to manage hundreds of calls spawned from a single task, driving token overuse.

#### 9. Inference Infrastructure Exploitation

Attackers target vulnerabilities in LLM serving frameworks (vLLM, TensorRT-LLM, SGLang, Triton, Ollama) to crash services or exhaust model resources through unsafe deserialization flaws, special-token injection, and injected chat templates.

### Prevention and Mitigation Strategies

#### 1. Rate Limiting & Input Size Validation

Apply rate limiting and user quotas to restrict the number of requests a single source entity can make in a given time period. Move beyond requests per second to enforce limits on tokens-per-minute, tokens-per-day, and estimated cost per request. Use pre-flight token estimation to reject requests before inference begins. This includes validation to ensure inputs do not exceed reasonable size limits.

#### 2. Hard Spending Caps

Set non-overridable budget ceilings per API key, user, team, cloud account, run, and session. Denominate the ceiling in currency, not only in tokens. The same token budget does not cost the same amount on every model. A measured comparison of current models on identical agent workloads reported a per-task dollar spread of about 28 times between the cheapest and most expensive model, while framework overhead changed cost by at most about 3.9 times (Pandey, 2026a). A token ceiling that is safe on a small model therefore permits roughly an order of magnitude more spend on a frontier model. Keep token limits as a secondary, model-agnostic control.

Caps must halt inference when exceeded. After-the-fact accounting, such as callbacks and billing monitors, cannot stop an agent loop that continues while the ledger catches up. Enforce the currency cap inside the model-invocation path, and refuse the call that would exceed the budget. That in-path halt is also what stops the runs this entry already describes: infinite-thinking loops (Li et al., 2025) and tool-chain token exhaustion (Dong et al., 2026) both burn budget inside the run. When setting the number, prefer cost per successful task over cost per call. A failing cheap model that retries can out-consume a reliable frontier model (Pandey, 2026b). Spending caps should also account for cost differences between modalities and tool protocols.

#### 3. Resource Allocation Management

Monitor and manage resource allocation dynamically to prevent any single user or request from consuming excessive resources.

#### 4. Sandbox Techniques

Restrict the LLM's access to network resources, internal services, and APIs. Constraining what the application can reach limits an attacker's ability to exfiltrate extracted model information or data to an external destination.

#### 5. Graceful Degradation

Design the system to degrade gracefully under heavy load, maintaining partial functionality rather than complete failure.

#### 6. Limit Queued Actions and Scale Robustly

Implement restrictions on the number of queued actions and total actions, while incorporating dynamic scaling and load balancing to handle varying demands and ensure consistent system performance.

#### 7. Scan for Adversarial Perturbations

Scan model inputs, particularly visual inputs to LVLMs (large visual language models), for evidence of adversarial perturbations that could cause model resource overconsumption.

#### 8. Detect Resource-Intensive Tool Interactions

Monitor agent-tool interactions to identify if a particular session appears to be causing a recursive or resource-intensive action without a clear end state. Establish baselines of normal tool behavior in order to detect if a particular tool is deviating from standard token consumption patterns.

#### 9. Agentic Circuit Breakers

Enforce step limits, recursion depth limits, time limits, and per-run cost ceilings on all agent executions. Use state hashing to detect recursive loops. Also track accumulated input tokens and model calls per session, and enforce a ceiling on both. Per-request token limits do not see session growth: each request can stay inside its own limit while the session re-sends an ever-larger context. Alert on sessions whose input-to-output token ratio or call count is far above the baseline.

Measured coding-agent sessions show why the session is the right unit. Across 722 sessions and 150,902 model calls, context processing was 83.5% of modelled cost and generation was 16.5%. On that set, 3.3% of sessions produced 80% of cost, and sessions longer than 200 model calls were 8% of sessions but 92.2% of cost (Arsentev, 2026a). On a separate set of 168 sessions, 94.4% of billed tokens were re-reads of context already sent earlier in the same session (Arsentev, 2026c). Resetting context is not free. In a controlled comparison of session-length policies (36 runs, 4,086 tests, 0 failures), clearing after every task cost 25.3% more than clearing every third task (p = 0.0022), and never clearing cost 15.6% more (p = 0.0108) (Arsentev, 2026b). Choose the reset interval by measuring the workload, not by clearing as often as possible. These figures are technical reports on benign coding-agent workloads, not attacker behavior. They support the benign half of Scenario #8.

#### 10. Inference Infrastructure Hardening

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

An attacker crafts adversarial image inputs that include perturbations optimized to cause an LVLM to overconsume tokens in its output (Gao et al., 2025).

#### Scenario #7: Multi-turn Tool Calling Loops and Tool Call Fan-Out

The attacker can publish a malicious tool (e.g. via a Claude Skill on an open-source repository) that instructs an agent to perform recursive cyclical tasks, or tasks that require a large number of tool calls. Developers incorporating that tool into their agents then risk causing excessive token consumption and service instability.

#### Scenario #8: Growing LLM Context in Agentic Sessions

An attacker or a benign user maintains an open agentic session, gradually injecting content so that each inference re-processes the full accumulated context. Per-turn cost climbs as the context grows, from roughly $0.001 on the first turn to about $0.50 by turn 100. No single request triggers rate limits because each stays individually within budget, yet the aggregate across many concurrent or long-lived sessions reaches hundreds of dollars. Those dollar figures are illustrative. Measured sessions support the shape: cost is driven by accumulated context, not by the new turn, and a small fraction of long sessions produces most of the spend (Arsentev, 2026a). A session ceiling on accumulated input tokens and model calls, priced in currency and enforced at the model-invocation boundary, stops the climb before any single request exceeds a per-request limit.
