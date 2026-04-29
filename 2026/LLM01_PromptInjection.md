## LLM01:2025 Prompt Injection

### Description

A Prompt Injection Vulnerability occurs when user prompts alter the LLM’s behavior or output in unintended ways. These inputs can affect the model even if they are imperceptible to humans, therefore prompt injections do not need to be human-visible/readable, as long as the content is parsed by the model.

Prompt Injection vulnerabilities exist in how models process prompts, and how input may force the model to incorrectly pass prompt data to other parts of the model, potentially causing them to violate guidelines, generate harmful content, enable unauthorized access, or influence critical decisions. While techniques like Retrieval Augmented Generation (RAG) and fine-tuning aim to make LLM outputs more relevant and accurate, research shows that they do not fully mitigate prompt injection vulnerabilities.

While prompt injection and jailbreaking are related concepts in LLM security, they are often used interchangeably in industry discussions, which can create defensive gaps. **Prompt injection** targets **application-level** instruction flow and trust boundaries (for example, how untrusted content is concatenated with system or developer instructions, and how that influences tool use or downstream actions). **Jailbreaking** targets **model-level** safety and policy controls baked into alignment training and guardrails. The two can appear together in a chain, but they are not interchangeable: mitigations aimed only at jailbreak resistance may not address instruction hijacking in an application context, and application-layer controls may not stop a pure policy-bypass jailbreak. Effective programs address both where their threat models apply.

### Types of Prompt Injection Vulnerabilities

#### Direct Prompt Injections

  Direct prompt injections occur when a user's prompt input directly alters the behavior of the model in unintended or unexpected ways. The input can be either intentional (i.e., a malicious actor deliberately crafting a prompt to exploit the model) or unintentional (i.e., a user inadvertently providing input that triggers unexpected behavior).

#### Indirect Prompt Injections

  Indirect prompt injections occur when an LLM accepts input that was not authored as a direct end-user prompt to the model, but is still ingested into the model context (for example, websites, files, retrieved documents, tool outputs, emails, or other machine-readable content). Here, **external** should be read as **outside the application's trusted instruction boundary**, not strictly as "outside the organization": internally hosted wikis, tickets, code hosts, and databases can carry the same class of risk if their content is merged into the model context without treating it as untrusted data with respect to instruction following.

#### Trusted-source (stored-context) prompt injection

  A related pattern occurs when malicious instructions are placed in **trusted or authenticated stores** that the application treats as **data**, while a **more privileged consumer** (for example, an IDE agent, an MCP-enabled assistant, or an automated review agent) later reads that content with weaker filtering because it is "internal," version-controlled, or database-backed. Guardrails are often relaxed in these paths to preserve fidelity for legitimate business needs (accurate ticket text, faithful repo metadata, unchanged database fields), which can leave instruction-bearing channels under-addressed compared to obviously untrusted web input. Documented incidents in this pattern include retrieval of attacker-controlled database rows through MCP integrations, hidden or innocuous-looking content in pull-request metadata consumed by coding agents, and inbound email rendered inside an agent's mailbox context. The underlying mechanism is the same as other prompt injections (untrusted natural language influences model behavior); the **input vector** differs in that it exploits high-trust retrieval and orchestration assumptions rather than a user typing into a chat box.

The severity and nature of the impact of a successful prompt injection attack can vary greatly and are largely dependent on both the business context the model operates in, and the agency with which the model is architected. Generally, however, prompt injection can lead to unintended outcomes, including but not limited to:

- Disclosure of sensitive information
- Revealing sensitive information about AI system infrastructure or system prompts
- Content manipulation leading to incorrect or biased outputs
- Providing unauthorized access to functions available to the LLM
- Executing arbitrary commands in connected systems
- Manipulating critical decision-making processes

The rise of multimodal AI, which processes multiple data types simultaneously, introduces unique prompt injection risks. Malicious actors could exploit interactions between modalities, such as hiding instructions in images that accompany benign text. The complexity of these systems expands the attack surface. Multimodal models may also be susceptible to novel cross-modal attacks that are difficult to detect and mitigate with current techniques. Robust multimodal-specific defenses are an important area for further research and development.

### Prevention and Mitigation Strategies

Prompt injection vulnerabilities are possible due to the nature of generative AI. Given the stochastic influence at the heart of the way models work, it is unclear if there are fool-proof methods of prevention for prompt injection. However, the following measures can mitigate the impact of prompt injections:

#### 1. Constrain model behavior

  Provide specific instructions about the model's role, capabilities, and limitations within the system prompt. Enforce strict context adherence, limit responses to specific tasks or topics, and instruct the model to ignore attempts to modify core instructions.

#### 2. Define and validate expected output formats

  Specify clear output formats, request detailed reasoning and source citations, and use deterministic code to validate adherence to these formats.

#### 3. Implement input and output filtering

  Define sensitive categories and construct rules for identifying and handling such content. Apply semantic filters and use string-checking to scan for non-allowed content. Evaluate responses using the RAG Triad: Assess context relevance, groundedness, and question/answer relevance to identify potentially malicious outputs.

#### 4. Enforce privilege control and least privilege access

  Provide the application with its own API tokens for extensible functionality, and handle these functions in code rather than providing them to the model. Restrict the model's access privileges to the minimum necessary for its intended operations.

#### 5. Require human approval for high-risk actions

  Implement human-in-the-loop controls for privileged operations to prevent unauthorized actions.

#### 6. Segregate and identify external content

  Separate and clearly denote untrusted content to limit its influence on user prompts. Extend the same discipline to **authenticated internal content** that is not authored by the model operator (for example, issue titles, pull-request descriptions, knowledge-base pages, CRM fields, and MCP tool or resource descriptions registered from third parties). Prefer **provenance metadata** (who wrote it, when, from which system), treat trust as a property of the **author and policy** rather than the network boundary alone, and scope **capabilities** so that a single hijacked task session cannot exceed the minimum privileges required for that task.

#### 7. Conduct adversarial testing and attack simulations

  Perform regular penetration testing and breach simulations, treating the model as an untrusted user to test the effectiveness of trust boundaries and access controls.

### Example Attack Scenarios

#### Scenario #1: Direct Injection

  An attacker injects a prompt into a customer support chatbot, instructing it to ignore previous guidelines, query private data stores, and send emails, leading to unauthorized access and privilege escalation.

#### Scenario #2: Indirect Injection

  A user employs an LLM to summarize a webpage containing hidden instructions that cause the LLM to insert an image linking to a URL, leading to exfiltration of the private conversation.

#### Scenario #3: Unintentional Injection

  A company includes an instruction in a job description to identify AI-generated applications. An applicant, unaware of this instruction, uses an LLM to optimize their resume, inadvertently triggering the AI detection.

#### Scenario #4: Intentional Model Influence

  An attacker modifies a document in a repository used by a Retrieval-Augmented Generation (RAG) application. When a user's query returns the modified content, the malicious instructions alter the LLM's output, generating misleading results.

#### Scenario #5: Code Injection

  An attacker exploits a vulnerability (CVE-2024-5184) in an LLM-powered email assistant to inject malicious prompts, allowing access to sensitive information and manipulation of email content.

#### Scenario #6: Payload Splitting

  An attacker uploads a resume with split malicious prompts. When an LLM is used to evaluate the candidate, the combined prompts manipulate the model's response, resulting in a positive recommendation despite the actual resume contents.

#### Scenario #7: Multimodal Injection

  An attacker embeds a malicious prompt within an image that accompanies benign text. When a multimodal AI processes the image and text concurrently, the hidden prompt alters the model's behavior, potentially leading to unauthorized actions or disclosure of sensitive information.

#### Scenario #8: Adversarial Suffix

  An attacker appends a seemingly meaningless string of characters to a prompt, which influences the LLM's output in a malicious way, bypassing safety measures.

#### Scenario #9: Multilingual/Obfuscated Attack

  An attacker uses multiple languages or encodes malicious instructions (e.g., using Base64 or emojis) to evade filters and manipulate the LLM's behavior.

#### Scenario #10: Trusted-source metadata and internal stores

  An attacker contributes or edits content in a channel the organization considers legitimate and low-risk (for example, a database row visible to an internal tool, a GitHub issue title, or a pull-request field). A developer or automated agent later pulls that content into the model context without aggressive sanitization because it is not user-typed chat input. The embedded instructions steer the model or connected tools toward sensitive actions (such as exfiltration or unsafe code changes) using the **higher trust** placed on that retrieval path.

### Reference Links

1. [ChatGPT Plugin Vulnerabilities - Chat with Code](https://embracethered.com/blog/posts/2023/chatgpt-plugin-vulns-chat-with-code/) **Embrace the Red**
2. [ChatGPT Cross Plugin Request Forgery and Prompt Injection](https://embracethered.com/blog/posts/2023/chatgpt-cross-plugin-request-forgery-and-prompt-injection./) **Embrace the Red**
3. [Not what you’ve signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/pdf/2302.12173.pdf) **Arxiv**
4. [Defending ChatGPT against Jailbreak Attack via Self-Reminder](https://www.researchsquare.com/article/rs-2873090/v1) **Research Square**
5. [Prompt Injection attack against LLM-integrated Applications](https://arxiv.org/abs/2306.05499) **Cornell University**
6. [Inject My PDF: Prompt Injection for your Resume](https://kai-greshake.de/posts/inject-my-pdf) **Kai Greshake**
7. [Not what you’ve signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/pdf/2302.12173.pdf) **Cornell University**
8. [Threat Modeling LLM Applications](https://aivillage.org/large%20language%20models/threat-modeling-llm/) **AI Village**
9. [Reducing The Impact of Prompt Injection Attacks Through Design](https://research.kudelskisecurity.com/2023/05/25/reducing-the-impact-of-prompt-injection-attacks-through-design/) **Kudelski Security**
10. [Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations (nist.gov)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2023.pdf)
11. [2407.07403 A Survey of Attacks on Large Vision-Language Models: Resources, Advances, and Future Trends (arxiv.org)](https://arxiv.org/abs/2407.07403)
12. [Exploiting Programmatic Behavior of LLMs: Dual-Use Through Standard Security Attacks](https://ieeexplore.ieee.org/document/10579515)
13. [Universal and Transferable Adversarial Attacks on Aligned Language Models (arxiv.org)](https://arxiv.org/abs/2307.15043)
14. [From ChatGPT to ThreatGPT: Impact of Generative AI in Cybersecurity and Privacy (arxiv.org)](https://arxiv.org/abs/2307.00691)
15. [Supabase MCP can leak your entire SQL database](https://generalanalysis.com/blog/supabase-mcp-blog): **General Analysis**
16. [Anthropic, Google, Microsoft paid AI bug bounties – quietly](https://www.theregister.com/2026/04/15/claude_gemini_copilot_agents_hijacked/): **The Register**
17. [CamoLeak: Critical GitHub Copilot vulnerability leaks private source code](https://www.legitsecurity.com/blog/camoleak-critical-github-copilot-vulnerability-leaks-private-source-code): **Legit Security**
18. [How Microsoft defends against indirect prompt injection attacks](https://www.microsoft.com/en-us/msrc/blog/2025/07/how-microsoft-defends-against-indirect-prompt-injection-attacks): **Microsoft MSRC**
19. [Attacking and Defending Generative AI](https://github.com/NetsecExplained/Attacking-and-Defending-Generative-AI): **NetsecExplained**
20. [Arcanum Prompt Injection Taxonomy](https://arcanum-sec.github.io/arc_pi_taxonomy): **Arcanum Sec**
21. [Pangea Prompt Injection Taxonomy](https://pangea.cloud/taxonomy/): **Pangea (CrowdStrike)**
22. [The Terminology Problem Causing Security Teams Real Risks](https://www.pillar.security/blog/the-terminology-problem-causing-security-teams-real-risks): **Pillar Security**
23. [Prompt Injection Isn't a Vulnerability](https://josephthacker.com/ai/2025/11/24/prompt-injection-isnt-a-vulnerability.html): **Joseph Thacker**

### Related Frameworks and Taxonomies

Refer to this section for comprehensive information, scenarios strategies relating to infrastructure deployment, applied environment controls and other best practices.

- [AML.T0051.000 - LLM Prompt Injection: Direct](https://atlas.mitre.org/techniques/AML.T0051.000) **MITRE ATLAS**
- [AML.T0051.001 - LLM Prompt Injection: Indirect](https://atlas.mitre.org/techniques/AML.T0051.001) **MITRE ATLAS**
- [AML.T0054 - LLM Jailbreak Injection: Direct](https://atlas.mitre.org/techniques/AML.T0054) **MITRE ATLAS**
