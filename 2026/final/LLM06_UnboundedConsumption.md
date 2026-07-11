## LLM06:2026 Unbounded Consumption

### Description

Unbounded Consumption occurs when an LLM application allows excessive and uncontrolled inferences, enabling attackers to disrupt service availability, inflict unsustainable financial costs, or steal intellectual property through model cloning, all by exploiting a common class of vulnerability: the absence of adequate controls over how resources are consumed. 

The high computational demands of LLMs, particularly in cloud and pay-per-token environments, make them inherently susceptible to resource exploitation and unauthorized usage. A defining characteristic of this threat is cost asymmetry. Attackers can trigger disproportionately expensive computation at negligible cost to themselves, whether through crafted prompts, stolen credentials, or manipulated workflows. 

This risk is compounded by the growing adoption of extended-thinking and reasoning models with unbounded token generation, multi-modal models that dramatically expand per-request compute costs, agentic architectures and tool-use protocols (such as MCP) that amplify a single request into cascading downstream operations, and shared inference infrastructure that introduces new side-channel and supply-chain attack surfaces. Traditional request-rate limiting alone is no longer sufficient; effective defense demands token-aware cost controls, hard spending caps, agent-level circuit breakers, and continuous cost-attribution monitoring.


### Common Examples of Risk

#### 1. Variable-Length Input Flood and Output Explosion
  Attackers can overload the LLM with numerous inputs of varying lengths, exploiting processing inefficiencies. This can deplete resources and potentially render the system unresponsive, significantly impacting service availability. This also includes output explosion via fine-tuning poisoning where a single malicious training sample breaks the model’s end-of-sequence behavior, pushing output to maximum tokens on every request (Gao et al., 2024).

#### 2. Denial of Wallet (DoW)
  By initiating a high volume of operations, attackers exploit the cost-per-use model of cloud-based AI services, leading to unsustainable financial burdens on the provider and risking financial ruin.

#### 3. Continuous Input Overflow
  Continuously sending inputs that exceed the LLM’s context window can lead to excessive computational resource use, resulting in service degradation and operational disruptions.

#### 4. Reasoning-Loop and Thinking-Token Exhaustion
  Attackers craft short, benign-looking prompts that result in resource exhaustion by forcing extended-thinking models into prolonged or non-terminating reasoning loops, consuming massive thinking-token budgets while bypassing input-size filters (Li et al., 2025). Because these prompts are small and appear legitimate, standard input validation provides no protection.

#### 5. Adversarial Inputs Optimized for Resource Overconsumption
  Attackers use optimization techniques to craft inputs that maximize computational cost. This is distinct from simply asking the model to perform a resource-intensive task and includes sponge examples (Shumailov et al., 2020) and adversarial visual perturbations. This includes optimization of adversarial input with gradient-based and gradient-free techniques. Unlike reasoning-loop attacks these require explicit optimization over the input space rather than prompt design alone. 

#### 6. Multimodal Inputs and Outputs
  For multi-modal models that are more cost-intensive than the text-only services, the extent of the computation cost is exacerbated. In many cases, this can result in 10 to 100 times the cost of text-based models.

#### 7. Model Extraction and Distillation Theft
  Attackers query the model API with crafted inputs to collect sufficient outputs to replicate a partial model or fine-tune a functional equivalent. Exposure of logits and log-probabilities significantly accelerates extraction (Carlini et al., 2024).

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

#### 3. Resource Allocation Management
  Monitor and manage resource allocation dynamically to prevent any single user or request from consuming excessive resources.

#### 4. Sandbox Techniques
  Restrict the LLM’s access to network resources, internal services, and APIs. This is particularly significant for all common scenarios as it encompasses insider risks and threats. Furthermore, it governs the extent of access the LLM application has to data and resources, thereby serving as a crucial control mechanism to mitigate or prevent side-channel attacks.

#### 5. Graceful Degradation
  Design the system to degrade gracefully under heavy load, maintaining partial functionality rather than complete failure.

#### 6. Limit Queued Actions and Scale Robustly
  Implement restrictions on the number of queued actions and total actions, while incorporating dynamic scaling and load balancing to handle varying demands and ensure consistent system performance.

#### 7. Scan for Adversarial Perturbations
  Scan model inputs, particularly visual inputs to LVLMs (large visual language models) for evidence of adversarial perturbations that could cause model resource overconsumption.

#### 8. Detect Resource-Intensive Tool Interactions
  Monitor agent-tool interactions to identify if a particular session appears to be causing a recursive or resource-intensive action without a clear end state. Establish baselines of normal tool behavior in order to detect if a particular tool is deviating from standard token consumption patterns.
  
#### 9. Agentic Circuit Breakers
  Enforce step limits, recursion depth limits, time limits, and per-run cost ceilings on all agent executions. Use state hashing to detect recursive loops.
  
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

#### Scenario #8: Bypassing System Input Filtering
  A malicious attacker bypasses input filtering techniques and preambles of the LLM to perform a side-channel attack and retrieve model information to a remote controlled resource under their control.

#### Scenario #9: Growing LLM Context in Agentic Sessions
  An attacker or a benign user maintains an open agentic session, gradually injecting content. After some 100 turns, each inference re-processes full context. Turn 1: $0.001. Turn 100: $0.50. In aggregate, this results in hundreds of dollars of spend. No single request triggers rate limits because each is individually within budget.
