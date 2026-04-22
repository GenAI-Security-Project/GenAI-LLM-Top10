## LLM03:2025 Supply Chain

### Description

LLM supply chains are susceptible to vulnerabilities that can affect the integrity of training data, models, adapters, conversion pipelines, and deployment platforms. These risks can result in biased outputs, security breaches, or system failures. While traditional software vulnerabilities focus on issues like code flaws and dependencies, in ML the risks also extend to third-party pre-trained models, datasets, and model artifacts.

These external elements can be manipulated through tampering, poisoning, or malicious artifact replacement.

Creating LLMs is a specialized task that often depends on third-party models and reusable adapters. The rise of open-access LLMs and new fine-tuning methods like LoRA (Low-Rank Adaptation) and PEFT (Parameter-Efficient Fine-Tuning), especially on platforms like Hugging Face, introduce new supply-chain risks. The biggest recent shift is that the supply chain now includes model artifacts, provenance, and conversion/merge workflows as first-class attack surfaces. Finally, the emergence of on-device LLMs increases the attack surface and supply-chain risks for LLM applications.

Some of the risks discussed here are also discussed in "LLM04 Data and Model Poisoning." This entry focuses on the supply-chain aspect of the risks.
A simple threat model can be found [here](https://github.com/jsotiro/ThreatModels/blob/main/LLM%20Threats-LLM%20Supply%20Chain.png).

### Common Examples of Risks

#### 1. Traditional Third-party Package Vulnerabilities

Such as outdated or deprecated components, which attackers can exploit to compromise LLM applications. This is similar to "A06:2021 – Vulnerable and Outdated Components" with increased risks when components are used during model development, fine-tuning, or inference.
(Ref. link: [A06:2021 – Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/))

#### 2. Licensing Risks

AI development often involves diverse software and dataset licenses, creating risks if not properly managed. Different open-source and proprietary licenses impose different legal requirements. Dataset licenses may restrict usage, distribution, or commercialization.

#### 3. Outdated or Deprecated Models

Using outdated or deprecated models that are no longer maintained leads to security issues and unpatched behavior drift.

#### 4. Vulnerable Pre-Trained Model

Models are binary black boxes and unlike open source, static inspection can offer little to no security assurances. Vulnerable pre-trained models can contain hidden biases, backdoors, or other malicious features that have not been identified through the safety evaluations of model repositories. Vulnerable models can be created by poisoned datasets, direct model tampering, or malicious re-publication of a trusted model.

#### 5. Weak Model Provenance

Currently there are no strong provenance assurances in published models. Model Cards and associated documentation provide model information to users, but they offer no guarantees on the origin of the model. An attacker can compromise a supplier account on a model repo or create a similar one and combine it with social engineering techniques to compromise the supply chain of an LLM application.

#### 6. Vulnerable LoRA Adapters

LoRA is a popular fine-tuning technique that enhances modularity by allowing pre-trained layers to be bolted onto an existing LLM. The method increases efficiency but creates new risks, where a malicious LoRA adapter compromises the integrity and security of the pre-trained base model. This can happen in collaborative model merge environments and in inference deployment platforms that allow adapters to be downloaded and applied to a deployed model.

#### 7. Compromised Model Conversion and Merge Workflows

Collaborative model merge and model handling services, including format conversion pipelines, can be exploited to introduce vulnerabilities into shared models. Model merging is popular on model hubs and can be abused to bypass review controls. Conversion services are especially risky because a malicious change can be introduced during transformation between model formats.

#### 8. LLM Model On-Device Supply-Chain Vulnerabilities

LLM models on device increase the supply-chain attack surface with compromised manufacturing processes and exploitation of device OS or firmware vulnerabilities. Attackers can reverse engineer and re-package applications with tampered models. This makes device integrity and firmware trust part of the LLM supply chain.

#### 9. Unclear T&Cs and Data Privacy Policies

Unclear T&Cs and data privacy policies of model operators can lead to sensitive application data being used for model training and subsequent exposure. This may also apply to risks from using copyrighted material provided by the model supplier.

#### 10. Missing Artifact Integrity and Signed Provenance

A major recent shift is the need to treat models, adapters, datasets, and conversion outputs like software releases. Unsigned or unverified artifacts can be replaced, repackaged, or silently altered, so provenance, hashes, signatures, and controlled promotion pipelines are now essential supply-chain controls.

### Prevention and Mitigation Strategies

1. Carefully vet data sources and suppliers, including T&Cs and privacy policies, and only use trusted suppliers. Regularly review and audit supplier security and access, ensuring no changes in their security posture or T&Cs.
2. Understand and apply the mitigations found in the OWASP Top Ten's "A06:2021 – Vulnerable and Outdated Components." This includes vulnerability scanning, management, and patching components. For development environments with access to sensitive data, apply these controls there too.
   (Ref. link: [A06:2021 – Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/))
3. Apply comprehensive AI red teaming and evaluations when selecting third-party models. Use extensive AI red teaming to evaluate the model, especially for the use cases you are planning to support.
4. Maintain an up-to-date inventory of components using a Software Bill of Materials (SBOM) to ensure you have an accurate and signed inventory, preventing tampering with deployed packages. Extend this to AI BOMs and ML SBOMs for models, adapters, and datasets.
5. To mitigate AI licensing risks, create an inventory of all licenses involved using BOMs and conduct regular audits of all software, tools, models, and datasets, ensuring compliance and transparency.
6. Only use models from verifiable sources and use third-party model integrity checks with signing and file hashes to compensate for the lack of strong model provenance. Similarly, use code signing for externally supplied code.
7. Implement strict monitoring and auditing practices for collaborative model development environments to prevent and quickly detect abuse. Treat model conversion and merge services as high-risk promotion points.
8. Use anomaly detection and adversarial robustness tests on supplied models and data to help detect tampering and poisoning. This should be part of MLOps and LLM pipelines.
9. Implement a patching policy to mitigate vulnerable or outdated components. Ensure the application relies on maintained versions of APIs and underlying models.
10. Encrypt models deployed at the edge with integrity checks and use vendor attestation APIs to prevent tampered apps and models. Reject unrecognized firmware and untrusted device states.
11. Implement verifiable root-of-trust controls across the full lifecycle, including signed artifacts, provenance tracking, tool/skill allowlisting, and continuous validation of agent permissions and upstream model integrity.
### Sample Attack Scenarios

#### Scenario #1: Vulnerable Python Library

An attacker exploits a vulnerable Python library to compromise an LLM app. This can happen when a compromised dependency is introduced into a model development or inference environment.

#### Scenario #2: Direct Tampering

Direct tampering and publishing a model to spread misinformation. An attacker modifies model parameters to bypass safeguards and distribute a malicious model.

#### Scenario #3: Fine-tuning a Popular Model

An attacker fine-tunes a popular open access model to remove key safety features and perform well in a narrow domain. The model is then published to exploit trust in benchmark assurances.

#### Scenario #4: Pre-Trained Models

An LLM system deploys pre-trained models from a widely used repository without thorough verification. A compromised model introduces malicious behavior, causing biased outputs or harmful outcomes.

#### Scenario #5: Compromised Third-Party Supplier

A compromised third-party supplier provides a vulnerable LoRA adapter that is merged into an LLM using a model-merge workflow.

#### Scenario #6: Supplier Infiltration

An attacker infiltrates a third-party supplier and compromises the production of a LoRA adapter intended for integration with an on-device LLM. The compromised adapter is subtly altered to include hidden vulnerabilities and malicious code. Once merged, it provides a covert entry point into the system.

#### Scenario #7: CloudBorne and CloudJacking Attacks

These attacks target cloud infrastructures, leveraging shared resources and vulnerabilities in virtualization layers. CloudBorne involves exploiting firmware vulnerabilities in shared cloud environments, while CloudJacking refers to malicious control or misuse of cloud instances. Both represent significant risks for supply chains reliant on cloud-based ML models.

#### Scenario #8: LeftOvers (CVE-2023-4969)

LeftOvers exploitation of leaked GPU local memory to recover sensitive data. An attacker can use this attack to exfiltrate sensitive data from production servers and development workstations.

#### Scenario #9: WizardLM

Following the removal of WizardLM, an attacker exploits the interest in this model and publishes a fake version of the model with the same name but containing malware and backdoors.

#### Scenario #10: Model Merge/Format Conversion Service

An attacker stages an attack through a model merge or format conversion service to compromise a publicly available model and inject malicious behavior.

#### Scenario #11: Reverse-Engineer Mobile App

An attacker reverse-engineers a mobile app to replace the model with a tampered version that leads users to scam sites. Users are encouraged to download the app directly via social engineering.

#### Scenario #12: Dataset Poisoning

An attacker poisons publicly available datasets to create a backdoor when fine-tuning models. The backdoor subtly favors certain companies in different markets.

#### Scenario #13: T&Cs and Privacy Policy

An LLM operator changes its T&Cs and privacy policy to require explicit opt-out from using application data for model training, leading to memorization or exposure of sensitive data.

### Reference Links

1. [PoisonGPT: How we hid a lobotomized LLM on Hugging Face to spread fake news](https://blog.mithrilsecurity.io/poisongpt-how-we-hid-a-lobotomized-llm-on-hugging-face-to-spread-fake-news)
2. [Large Language Models On-Device with MediaPipe and TensorFlow Lite](https://developers.googleblog.com/en/large-language-models-on-device-with-mediapipe-and-tensorflow-lite/)
3. [Hijacking Safetensors Conversion on Hugging Face](https://hiddenlayer.com/research/silent-sabotage/)
4. [ML Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010)
5. [Using LoRA Adapters with vLLM](https://docs.vllm.ai/en/latest/models/lora.html)
6. [Removing RLHF Protections in GPT-4 via Fine-Tuning](https://arxiv.org/pdf/2311.05553)
7. [Model Merging with PEFT](https://huggingface.co/blog/peft_merging)
8. [HuggingFace SF_Convertbot Scanner](https://gist.github.com/rossja/d84a93e5c6b8dd2d4a538aa010b29163)
9. [Thousands of servers hacked due to insecurely deployed Ray AI framework](https://www.csoonline.com/article/2075540/thousands-of-servers-hacked-due-to-insecurely-deployed-ray-ai-framework.html)
10. [LeftoverLocals: Listening to LLM responses through leaked GPU local memory](https://blog.trailofbits.com/2024/01/16/leftoverlocals-listening-to-llm-responses-through-leaked-gpu-local-memory/)
11.[ML Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010) - MITRE ATLAS
12.[LLM Scalability Risk for Agentic-AI and Model Supply Chain Security]https://arxiv.org/abs/2602.19021

### Related Frameworks and Taxonomies

Refer to this section for comprehensive information, scenario strategies relating to infrastructure deployment, applied environment controls, and other best practices.

- [ML Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010) - MITRE ATLAS