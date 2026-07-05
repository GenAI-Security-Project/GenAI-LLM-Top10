## LLM04:2026 Supply Chain

### Description

LLM supply chains are susceptible to vulnerabilities that can affect the integrity of training data, models, adapters, conversion pipelines, and deployment platforms. These risks can result in biased outputs, security breaches, or system failures. While traditional software vulnerabilities focus on issues like code flaws and dependencies, in ML the risks also extend to third-party pre-trained models, datasets, and model artifacts.

These external elements can be manipulated through tampering, poisoning, or malicious artifact replacement.

Creating LLMs is a specialized task that often depends on third-party models and reusable adapters. The rise of open-access LLMs and new fine-tuning methods like LoRA (Low-Rank Adaptation) and PEFT (Parameter-Efficient Fine-Tuning), especially on platforms like Hugging Face, introduces new supply-chain risks. The biggest recent shift is that the supply chain now includes model artifacts, provenance, and conversion/merge workflows as first-class attack surfaces. Finally, the emergence of on-device LLMs increases the attack surface and supply-chain risks for LLM applications.

Some of the risks discussed here are also discussed in "LLM05 Data and Model Poisoning." This entry focuses on the supply-chain aspect of the risks. Supply-chain risks specific to agentic applications are covered by ASI04 Agentic Supply Chain Vulnerabilities in the OWASP Top 10 for Agentic Applications.
A simple threat model can be found [here](https://github.com/jsotiro/ThreatModels/blob/main/LLM%20Threats-LLM%20Supply%20Chain.png).

### Common Examples of Risk

#### 1. Traditional Third-party Package Vulnerabilities

These include outdated or deprecated components, which attackers can exploit to compromise LLM applications. This is similar to "A06:2021 – Vulnerable and Outdated Components" with increased risks when components are used during model development, fine-tuning, or inference.
(Ref. link: [A06:2021 – Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/))

#### 2. Licensing Risks

AI development often involves diverse software and dataset licenses, creating risks if not properly managed. Different open-source and proprietary licenses impose different legal requirements. Dataset licenses may restrict usage, distribution, or commercialization.

#### 3. Outdated or Deprecated Models

Using outdated or deprecated models that are no longer maintained leads to security issues and unpatched behavior drift.

#### 4. Vulnerable Pre-Trained Model

Models are binary black boxes and, unlike with open-source code, static inspection can offer little to no security assurances. Vulnerable pre-trained models can contain hidden biases, backdoors, or other malicious features that have not been identified through the safety evaluations of model repositories. Vulnerable models can be created by poisoned datasets, direct model tampering, or malicious re-publication of a trusted model. Migrating away from unsafe serialization formats such as Python pickle, which can execute arbitrary code on load, reduces but does not eliminate this risk: a backdoor can be embedded directly in a model's computational graph and persist in formats widely considered safe, such as ONNX. Likewise, a crafted model file can exploit memory-corruption bugs in a format's native parser, as shown by heap overflows in llama.cpp's GGUF parsing (CVE-2024-23496), executing code even though the format itself carries none.

#### 5. Weak Model Provenance

Currently there are no strong provenance assurances in published models. Model Cards and associated documentation provide model information to users, but they offer no guarantees on the origin of the model. An attacker can compromise a supplier account on a model repo or create a similar one and combine it with social engineering techniques to compromise the supply chain of an LLM application.

#### 6. Vulnerable LoRA Adapters

LoRA is a popular fine-tuning technique that enhances modularity by allowing pre-trained layers to be bolted onto an existing LLM. The method increases efficiency but creates new risks, where a malicious LoRA adapter compromises the integrity and security of the pre-trained base model. This can happen in collaborative model merge environments and in inference deployment platforms that allow adapters to be downloaded and applied to a deployed model.

#### 7. Compromised Model Conversion and Merge Workflows

Collaborative model merge and model handling services, including format conversion pipelines, can be exploited to introduce vulnerabilities into shared models. Model merging is popular on model hubs and can be abused to bypass review controls. Conversion services are especially risky because a malicious change can be introduced during transformation between model formats. Quantization is a related transformation risk: model weights can be crafted so that the full-precision model behaves benignly under evaluation while the standard quantized version exhibits attacker-chosen behavior, so assurances obtained on the full-precision artifact do not transfer to the deployed quantized artifact.

#### 8. LLM Model On-Device Supply-Chain Vulnerabilities

LLM models on device increase the supply-chain attack surface with compromised manufacturing processes and exploitation of device OS or firmware vulnerabilities. Attackers can reverse engineer and re-package applications with tampered models. This makes device integrity and firmware trust part of the LLM supply chain.

#### 9. Unclear T&Cs and Data Privacy Policies

Unclear terms and conditions (T&Cs) and data privacy policies of model operators can lead to sensitive application data being used for model training and subsequent exposure. This may also apply to risks from using copyrighted material provided by the model supplier.

#### 10. Unsigned or Replaceable Model Artifacts

When models, adapters, datasets, fine-tuned checkpoints, and conversion outputs are not signed or hash-pinned, an attacker can replace, repackage, or silently alter artifacts in transit, in storage, or at the promotion boundary where automated pipelines accept artifacts into trusted environments. Pipelines that resolve artifacts by a mutable reference (for example, a `latest` tag) instead of an immutable digest, or that trust namespace and repository metadata alone, can be made to load a malicious version under a trusted name.

### Prevention and Mitigation Strategies

1. Carefully vet data sources and suppliers, including T&Cs and privacy policies, and only use trusted suppliers. Regularly review and audit supplier security and access, ensuring no changes in their security posture or T&Cs.
2. Understand and apply the mitigations found in the OWASP Top Ten's "A06:2021 – Vulnerable and Outdated Components." This includes vulnerability scanning, management, and patching components. For development environments with access to sensitive data, apply these controls there too.
   (Ref. link: [A06:2021 – Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/))
3. Apply comprehensive AI red teaming and evaluations when selecting third-party models. Use extensive AI red teaming to evaluate the model, especially for the use cases you are planning to support.
4. Maintain an up-to-date inventory of components using a Software Bill of Materials (SBOM) to ensure you have an accurate and signed inventory, preventing tampering with deployed packages. Extend this to AI BOMs (AIBOMs) and ML SBOMs for models, adapters, and datasets, evaluating options such as the OWASP CycloneDX ML-BOM and the OWASP AIBOM project.
5. To mitigate AI licensing risks, create an inventory of all licenses involved using BOMs and conduct regular audits of all software, tools, models, and datasets, ensuring compliance and transparency.
6. Only use models from verifiable sources and use third-party model integrity checks with signing and file hashes to compensate for the lack of strong model provenance. Cryptographic model signing backed by a transparency log (for example, the OpenSSF Model Signing project and Sigstore) binds a model artifact to a signer identity and is preferable to relying on reproducible builds, which are not guaranteed for model training. Note that signing proves integrity and origin, not safety: a validly signed model from a compromised or trusted-but-malicious supplier can still be backdoored, so combine signing with provenance policy and behavioral evaluation. For a maturity model of artifact-signing practices, see the Coalition for Secure AI (CoSAI) work on signing ML artifacts. Similarly, use code signing for externally supplied code.
7. Implement strict monitoring and auditing practices for collaborative model development environments to prevent and quickly detect abuse. Treat model conversion and merge services as high-risk promotion points.
8. Use anomaly detection and adversarial robustness tests on supplied models and data to help detect tampering and poisoning. This should be part of MLOps and LLM pipelines.
9. Implement a patching policy to mitigate vulnerable or outdated components. Ensure the application relies on maintained versions of APIs and underlying models.
10. Encrypt models deployed at the edge with integrity checks and use vendor attestation APIs to prevent tampered apps and models. Reject unrecognized firmware and untrusted device states.
11. Implement verifiable root-of-trust controls across the full lifecycle, including signed artifacts, immutable artifact references, provenance tracking, policy-based release gates, and continuous validation of upstream model integrity.

### Example Attack Scenarios

#### Scenario #1: Vulnerable Python Library

An attacker exploits a vulnerable Python library to compromise an LLM app. This can happen when a compromised dependency is introduced into a model development or inference environment, as in the December 2022 PyTorch supply-chain attack where a malicious `torchtriton` package on the PyPI registry shadowed the legitimate PyTorch-nightly dependency and exfiltrated data, and in the ShadowRay attacks against the Ray AI framework where the disputed CVE-2023-48022 (unauthenticated dashboards on production servers) was exploited in the wild. Model-serving frameworks are part of the same attack surface: in Ollama, CVE-2024-37032 allowed remote code execution through a malicious model manifest pulled from a registry.

#### Scenario #2: Direct Tampering

An attacker directly tampers with a model and publishes it to spread misinformation, as demonstrated by the PoisonGPT proof-of-concept in which a model with surgically modified parameters was uploaded to Hugging Face under a trusted-looking name and evaded detection by standard benchmark evaluation.

#### Scenario #3: Fine-tuning a Popular Model

An attacker fine-tunes a popular open access model to remove key safety features and perform well in a narrow domain. The model is then published to exploit trust in benchmark assurances.

#### Scenario #4: Pre-Trained Models

An LLM system deploys pre-trained models from a widely used repository without thorough verification. A compromised model introduces malicious behavior, causing biased outputs or harmful outcomes.

#### Scenario #5: Compromised Third-Party Supplier

A compromised third-party supplier provides a vulnerable LoRA adapter that is merged into an LLM using a model-merge workflow.

#### Scenario #6: Supplier Infiltration

An attacker infiltrates a third-party supplier and compromises the production of a LoRA adapter intended for integration with an on-device LLM. The compromised adapter is subtly altered to include hidden vulnerabilities and malicious code. Once merged, it provides a covert entry point into the system.

#### Scenario #7: CloudBorne and CloudJacking Attacks

These attacks target cloud infrastructures, leveraging shared resources and vulnerabilities in virtualization layers. CloudBorne involves exploiting firmware vulnerabilities in shared cloud environments, while CloudJacking refers to malicious control or misuse of cloud instances. Both represent significant risks for supply chains reliant on cloud-based ML models. Researchers have since demonstrated the AI-specific variant: uploading a malicious model to a shared AI-as-a-service platform and escaping the inference container to reach other customers' models and datasets.

#### Scenario #8: LeftoverLocals (CVE-2023-4969)

An attacker exploits LeftoverLocals to recover data leaked in GPU local memory, exfiltrating sensitive information from production servers and development workstations.

#### Scenario #9: WizardLM

Following the removal of WizardLM, an attacker exploits the interest in this model and publishes a fake version of the model with the same name but containing malware and backdoors.

#### Scenario #10: Model Merge/Format Conversion Service

An attacker stages an attack through a model merge or format conversion service to compromise a publicly available model and inject malicious behavior, as shown by HiddenLayer's research on hijacking the Safetensors conversion bot on Hugging Face to introduce malicious code into converted models.

#### Scenario #11: Reverse-Engineer Mobile App

An attacker reverse-engineers a mobile app to replace the model with a tampered version that leads users to scam sites. Users are encouraged to download the app directly via social engineering.

#### Scenario #12: Dataset Poisoning

An attacker poisons publicly available datasets to create a backdoor when fine-tuning models. The backdoor subtly favors certain companies in different markets.

#### Scenario #13: T&Cs and Privacy Policy

An LLM operator changes its T&Cs and privacy policy to require explicit opt-out from using application data for model training, leading to memorization or exposure of sensitive data.

#### Scenario #14: Model Namespace Reuse

An organization deploys a model from a public hub by referencing it solely by its `Author/ModelName` identifier. The original author deletes or transfers the account, freeing the namespace, and an attacker re-registers the same name and publishes a malicious model under the original path. Pipelines and managed model catalogs that resolve the model by name alone then pull the attacker's model, leading to remote code execution. This technique reinforces that trusting a model by name is not a substitute for provenance verification.

#### Scenario #15: Malicious Serialized Model Evading Hub Scanners

An attacker uploads a model whose serialized weights file is crafted to evade the hub's automated malware scanner, for example a corrupted or compression-wrapped pickle stream that executes its payload before the scanner reaches the broken byte and errors out. A victim who loads the model with the default loader triggers arbitrary code execution. This shows that hub-side scanning of serialized models is necessary but not sufficient.

#### Scenario #16: Codeless Backdoor in a "Safe" Model Format

An attacker modifies a model's computational graph to insert logic that activates only on a specific trigger input, then distributes the model in a format widely considered safe from code execution, such as ONNX. Because no executable code is attached and the backdoor lives in the graph itself, format-based "safe loading" controls and serialization scanners do not detect it, and the tampered model passes superficial review before being integrated downstream.

#### Scenario #17: "Safe" Loader and Scanner Bypass

An organization relies on a loader option documented as safe against code execution (for example, loading weights only) or on a scanner-gated ingestion step to accept third-party models. An attacker crafts a model file that defeats the control, bypassing the safe-loader option or evading the scanner through tricks such as file-extension mismatch or archive corruption, and still achieves arbitrary code execution when the model is loaded. Both safe-loader flags and model scanners have had such bypasses assigned CVEs, so treat them as defense-in-depth layers rather than guarantees, alongside provenance verification and keeping loaders and parsers patched.

#### Scenario #18: Compromised Build Pipeline for Model Artifacts

An attacker compromises the CI/CD pipeline an organization uses to fine-tune and publish an LLM, for example through a malicious GitHub Actions dependency, a stolen artifact-registry credential, or a tampered build secret. The next training or packaging run produces a backdoored model artifact. Because the artifact is built and signed by the organization's own release infrastructure, it passes downstream provenance checks, internal attestation, and supply-chain scanners that only flag externally sourced components. The same build-time substitution that affected traditional software supply chains, as in the xz-utils backdoor and the Codecov breach, applies wherever model artifacts are produced by automated pipelines without model-specific integrity controls such as reproducible builds, transparency logs, or post-build behavioral evaluation.

### Reference Links

1. [PoisonGPT: How we hid a lobotomized LLM on Hugging Face to spread fake news](https://blog.mithrilsecurity.io/poisongpt-how-we-hid-a-lobotomized-llm-on-hugging-face-to-spread-fake-news): **Mithril Security**
2. [Large Language Models On-Device with MediaPipe and TensorFlow Lite](https://developers.googleblog.com/en/large-language-models-on-device-with-mediapipe-and-tensorflow-lite/): **Google Developers Blog**
3. [Hijacking Safetensors Conversion on Hugging Face](https://hiddenlayer.com/research/silent-sabotage/): **HiddenLayer**
4. [AI Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010): **MITRE ATLAS**
5. [Using LoRA Adapters with vLLM](https://docs.vllm.ai/en/latest/features/lora/): **vLLM**
6. [Removing RLHF Protections in GPT-4 via Fine-Tuning](https://arxiv.org/abs/2311.05553): **Qiusi Zhan et al., arXiv**
7. [PEFT welcomes new merging methods](https://huggingface.co/blog/peft_merging): **Hugging Face**
8. [Thousands of servers hacked due to insecurely deployed Ray AI framework](https://www.csoonline.com/article/2075540/thousands-of-servers-hacked-due-to-insecurely-deployed-ray-ai-framework.html): **CSO Online**
9. [LeftoverLocals: Listening to LLM responses through leaked GPU local memory](https://blog.trailofbits.com/2024/01/16/leftoverlocals-listening-to-llm-responses-through-leaked-gpu-local-memory/): **Trail of Bits**
10. [LLM Scalability Risk for Agentic-AI and Model Supply Chain Security](https://arxiv.org/abs/2602.19021): **Kiarash Ahi et al., arXiv**
11. [Model Namespace Reuse: An AI Supply-Chain Attack Exploiting Model Name Trust](https://unit42.paloaltonetworks.com/model-namespace-reuse/): **Unit 42, Palo Alto Networks**
12. [Malicious ML models discovered on Hugging Face platform (nullifAI)](https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face): **ReversingLabs**
13. [PyTorch Users at Risk: Unveiling 3 Zero-Day PickleScan Vulnerabilities](https://jfrog.com/blog/unveiling-3-zero-day-vulnerabilities-in-picklescan/): **JFrog**
14. [PyTorch torch.load weights_only bypass (CVE-2025-32434)](https://github.com/pytorch/pytorch/security/advisories/GHSA-53q9-r3pm-6pq6): **GitHub Security Advisories**
15. [Inside CVE-2025-1550: Remote Code Execution via Keras Models](https://blog.huntr.com/inside-cve-2025-1550-remote-code-execution-via-keras-models): **huntr**
16. [ShadowLogic: Persistent No-Code Backdoors in AI Computational Graphs](https://hiddenlayer.com/innovation-hub/shadowlogic/): **HiddenLayer**
17. [Launch of Model Signing v1.0: OpenSSF AI/ML Working Group Secures the Machine Learning Supply Chain](https://openssf.org/blog/2025/04/04/launch-of-model-signing-v1-0-openssf-ai-ml-working-group-secures-the-machine-learning-supply-chain/): **OpenSSF**
18. [Coalition for Secure AI Releases Two Actionable Frameworks for AI Model Signing and Incident Response](https://www.oasis-open.org/2025/11/18/coalition-for-secure-ai-releases-two-actionable-frameworks-for-ai-model-signing-and-incident-response/): **OASIS / CoSAI**
19. [Evolving AI Transparency: The Journey of the AIBOM Generator and Its New Home at OWASP](https://genai.owasp.org/2025/12/18/evolving-ai-transparency-the-journey-of-the-aibom-generator-and-its-new-home-at-owasp/): **OWASP GenAI Security Project**
20. [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/): **OWASP GenAI Security Project**
21. [Exploiting LLM Quantization](https://arxiv.org/abs/2405.18137): **Kazuki Egashira et al., arXiv**
22. [Compromised PyTorch-nightly dependency chain between December 25th and December 30th, 2022](https://pytorch.org/blog/compromised-nightly-dependency/): **PyTorch**
23. [llama.cpp GGUF library gguf_fread_str heap-based buffer overflow vulnerability (TALOS-2024-1913)](https://talosintelligence.com/vulnerability_reports/TALOS-2024-1913): **Cisco Talos**
24. [Probllama: Ollama Remote Code Execution Vulnerability (CVE-2024-37032)](https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032): **Wiz**
25. [Wiz Research finds architecture risks that may compromise AI-as-a-Service providers](https://www.wiz.io/blog/wiz-and-hugging-face-address-risks-to-ai-infrastructure): **Wiz**
26. [Machine Learning Bill of Materials (ML-BOM)](https://cyclonedx.org/capabilities/mlbom/): **OWASP CycloneDX**
27. [Supply-chain Levels for Software Artifacts (SLSA)](https://slsa.dev): **OpenSSF**

### Related Frameworks and Taxonomies

| Framework | Reference | Relevance |
|---|---|---|
| **OWASP Top 10 for Agentic Applications (ASI)** | ASI04 — Agentic Supply Chain Vulnerabilities | This entry's own scope note defers agentic-specific supply-chain risk to ASI04, leaving this entry to cover the non-agentic model, dataset, and artifact supply chain |
| **MITRE ATLAS** | [AML.T0010 — AI Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010) | Sub-techniques for Hardware (.000), AI Software (.001), Data (.002), Model (.003), Container Registry (.004), and AI Agent Tool (.005) |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI04 — Data, Model & Artifact Poisoning | States it "extends LLM03:2025 (LLM Supply Chain) and ASI04 with a data-integrity lens, focusing on the training corpus and artifact pipeline attack surface"; its DBOM and full-chain artifact-signing controls mirror this entry's AIBOM/ML-SBOM (mitigation #4) and cryptographic model-signing (mitigation #6) |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI05 — Data Integrity & Validation Failures | Covers snapshot-import path traversal against "vector databases, model registries, and feature stores" and requires signed, checksum-verified artifacts "on every import and promotion event" — the same promotion-boundary trust failure as this entry's unsigned/replaceable-artifact risk (#10) and root-of-trust mitigation (#11) |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI03 — Shadow AI & Unsanctioned Data Flows | Its adversary model, naming "SaaS providers that retain prompts for training" and "vendors that change data handling practices post-adoption", is related to this entry's risk #9 (unclear model-operator T&Cs), Scenario #13, and the supplier-vetting mitigation #1, which its approved-vendor contract controls mirror |
