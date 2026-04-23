for additional guidance, refer to [the style guide](../documentation/style/README.md) and to the [glossary](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/wiki/Definitions)

## LLMXX: Supply Chain Trust Failure

### Description

LLM supply chains depend on trust in third-party models, datasets, adapters, conversion workflows, repositories, and deployment tooling. When that trust is broken, attackers can introduce tampered artifacts, poisoned data, malicious adapters, or fake model releases that compromise system integrity and downstream applications. This can lead to system compromise, data breaches, unsafe model behavior, or unauthorized access to connected services.

The risk has grown as open model ecosystems, LoRA and PEFT adapters, model merging, format conversion services, and agentic toolchains have expanded the number of places where untrusted components can enter the workflow. Modern LLM pipelines increasingly assemble third-party artifacts such as pre-trained weights, fine-tuning adapters, datasets, dependency packages, and container images through automated release processes, which makes supply-chain trust a critical security concern.


### Common Examples of Risk

1. Example 1: A tampered or impersonated model release is published under a trusted or familiar name, causing users to download a malicious artifact.
2. Example 2: A third-party LoRA or PEFT adapter is introduced into a production workflow and later alters model behavior in ways that are not detected during basic validation.
3. Example 3: A model conversion, merge, or packaging service injects changes into an artifact during processing, producing a file that appears legitimate but is not trustworthy.

### Prevention and Mitigation Strategies

1. Trust only verified sources for models, datasets, adapters, and tools. Restrict acquisition to approved suppliers with clear ownership, stable security practices, and strong account protection.
2. Require integrity validation before promotion into trusted environments. Verify hashes, signatures, attestations, and provenance records for AI artifacts, and treat unsigned or unverified items as untrusted.
3. Monitor high-risk workflows closely, including model hubs, merge services, conversion pipelines, agent tools, and publication workflows. Use approval gates, logging, and review controls for these promotion points.

### Example Attack Scenarios

Scenario #1: An attacker compromises a supplier account or creates a lookalike repository and publishes a fake model under a familiar name. A downstream team downloads and deploys the artifact, which later produces unsafe outputs or exposes sensitive prompts.
Scenario #2: A malicious adapter is inserted into a model update workflow through a third-party collaborator or supplier. The adapter behaves normally in standard tests but triggers harmful or covert behavior when specific prompts or domains are used.

### Reference Links

1. [ML Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010): **MITRE ATLAS**
2. [Attesting LLM Pipelines: Enforcing Verifiable Training and Release ...](https://arxiv.org/abs/2603.28988): **arXiv**
3. [Measuring Malicious Intermediary Attacks on the LLM Supply Chain](https://arxiv.org/html/2604.08407v1): **arXiv**
