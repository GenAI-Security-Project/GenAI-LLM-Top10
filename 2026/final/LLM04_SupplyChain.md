## LLM04:2026 Supply Chain

### Description

LLM supply chains are susceptible to vulnerabilities that affect the integrity of training data, models, adapters, conversion pipelines, and deployment platforms, resulting in biased outputs, security breaches, or system failures. While traditional software vulnerabilities focus on code flaws and dependencies, in ML the risks extend to third-party pre-trained models, datasets, and model artifacts, which can be manipulated through tampering, poisoning, or malicious artifact replacement.

Creating LLMs is specialized work that depends on third-party models, datasets, and reusable adapters built with fine-tuning methods like LoRA (Low-Rank Adaptation) and PEFT (Parameter-Efficient Fine-Tuning) and shared on platforms like Hugging Face. The supply chain now includes model artifacts, provenance, and conversion/merge workflows as first-class attack surfaces, and on-device LLMs widen it further.

Some of the risks covered here are also discussed in LLM05:2026 Data and Model Poisoning; this entry focuses on their supply-chain aspect. Supply-chain risks specific to agentic applications, including MCP servers and tool registries, are covered by ASI04 Agentic Supply Chain Vulnerabilities in the OWASP Top 10 for Agentic Applications, and MITRE ATLAS catalogs the corresponding adversary techniques under AML.T0010 AI Supply Chain Compromise.
A [simple LLM supply-chain threat model](https://github.com/jsotiro/ThreatModels/blob/main/LLM%20Threats-LLM%20Supply%20Chain.png) illustrates these surfaces.

### Common Examples of Risk

#### 1. Vulnerable or Outdated Third-Party Components and Models

Outdated or deprecated components, including packages, serving frameworks, and models themselves, can be exploited to compromise LLM applications. This is similar to [A06:2021 – Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/) with increased risks when components are used during model development, fine-tuning, or inference. LLM coding assistants add a new variant: they hallucinate plausible but nonexistent package names at scale, which attackers register in advance ("slopsquatting") so that unverified AI-suggested dependencies resolve to malicious code.

#### 2. Licensing Risks

AI development involves diverse software and dataset licenses that impose different usage, distribution, and commercialization requirements; if not properly managed, they create legal and compliance exposure.

#### 3. Vulnerable or Tampered Pre-Trained Models

Models are binary black boxes and, unlike with open-source code, static inspection can offer little to no security assurances. A pre-trained model can contain hidden biases or backdoors introduced through poisoned datasets or direct tampering. Migrating away from unsafe serialization formats such as Python pickle, which can execute arbitrary code on load, reduces but does not eliminate this risk: a backdoor can be embedded directly in a model's computational graph and persist in formats widely considered safe, such as ONNX, and a crafted model file can exploit memory-corruption bugs in a format's native parser, as shown by heap overflows in llama.cpp's GGUF parsing (CVE-2024-23496).

#### 4. Weak Provenance and Unsigned Model Artifacts

Published models carry no strong provenance assurances: Model Cards document a model but do not prove its origin, and a compromised or lookalike supplier account can publish a malicious model under a trusted name. When models, adapters, datasets, fine-tuned checkpoints, and conversion outputs are not signed or hash-pinned, an attacker can replace or silently alter artifacts in transit, in storage, or at the promotion boundary where automated pipelines accept artifacts into trusted environments — especially when pipelines resolve artifacts by a mutable reference (for example, a `latest` tag) instead of an immutable digest.

#### 5. Vulnerable Adapters and Compromised Conversion, Merge, and Quantization Workflows

LoRA adapters make fine-tuning modular and efficient, but a malicious adapter can compromise the integrity of the pre-trained base model, whether in collaborative model merge environments or on inference platforms that download and apply adapters to a deployed model. Model conversion and merge services can introduce malicious changes during transformation between formats, bypassing review controls. Quantization is a related transformation risk: model weights can be crafted so the full-precision model evaluates benignly while the quantized artifact exhibits attacker-chosen behavior, so full-precision assurances do not transfer to the deployed quantized artifact.

#### 6. On-Device LLM Supply-Chain Vulnerabilities

LLMs shipped on devices add compromised manufacturing processes, exploitation of device OS or firmware vulnerabilities, and re-packaged applications with tampered models to the attack surface, making device integrity and firmware trust part of the LLM supply chain.

#### 7. Unclear T&Cs and Data Privacy Policies

Unclear terms and conditions (T&Cs) and data privacy policies of model operators can lead to sensitive application data being used for model training and subsequent exposure, and may create copyright risk from material provided by the model supplier.

### Prevention and Mitigation Strategies

1. Carefully vet data sources and suppliers, including T&Cs and privacy policies, and only use trusted suppliers. Regularly review and audit supplier security and access, and re-assess on changes in their security posture or T&Cs.
2. Apply the mitigations in the OWASP Top Ten's [A06:2021 – Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/): vulnerability scanning, management, and a patching policy that keeps the application on maintained versions of components, APIs, and underlying models. Apply the same controls to development environments with access to sensitive data, and verify that AI-suggested dependencies exist and are the intended package before adopting them.
3. Apply AI red teaming and evaluations when selecting third-party models, focused on the use cases you plan to support, and continue in production with anomaly detection and adversarial robustness testing in MLOps and LLM pipelines to detect tampering and poisoning.
4. Maintain an up-to-date, signed inventory of components using a Software Bill of Materials (SBOM), extended to models, adapters, and datasets with AI BOMs (AIBOMs) and ML SBOMs — evaluating options such as the OWASP CycloneDX ML-BOM and the OWASP AIBOM project. Track licenses in the same inventory and audit it regularly for compliance and transparency.
5. Only use models from verifiable sources and compensate for weak provenance with third-party integrity checks, signing, and file hashes. Cryptographic model signing backed by a transparency log (for example, the OpenSSF Model Signing project and Sigstore) binds a model artifact to a signer identity; reproducible builds are not guaranteed for model training, and the Coalition for Secure AI (CoSAI) provides a maturity model for signing ML artifacts. Signing proves integrity and origin, not safety — a validly signed model from a compromised or trusted-but-malicious supplier can still be backdoored — so combine it with immutable artifact references, provenance policy, policy-based release gates (for example, SLSA), behavioral evaluation, and continuous validation of upstream model integrity. Similarly, use code signing for externally supplied code.
6. Strictly monitor and audit collaborative model development environments, and treat model conversion and merge services as high-risk promotion points.
7. Encrypt models deployed at the edge with integrity checks, use vendor attestation APIs to prevent tampered apps and models, and reject unrecognized firmware and untrusted device states.

### Example Attack Scenarios

#### Scenario #1: Compromised Packages and Serving Frameworks

A compromised dependency reaches a model development or inference environment, as in the December 2022 PyTorch supply-chain attack, where a malicious `torchtriton` package on the PyPI registry shadowed the legitimate PyTorch-nightly dependency and exfiltrated data. The serving stack is part of the same attack surface: the ShadowRay attacks exploited the disputed CVE-2023-48022 (unauthenticated dashboards on production Ray servers) in the wild, later escalating into a self-propagating botnet across exposed clusters, and in Ollama, CVE-2024-37032 allowed remote code execution through a malicious model manifest pulled from a registry.

#### Scenario #2: Tampered Model Published to a Hub

An attacker publishes a tampered model under a trusted-looking name, as demonstrated by the PoisonGPT proof-of-concept, in which a model with surgically modified parameters spread misinformation while evading detection by standard benchmark evaluation. The same trust gap covers attacker fine-tunes that strip a popular model's safety features while performing well in a narrow domain, any pre-trained model deployed without verification, and shared AI-as-a-service platforms, where researchers escaped an inference container via a malicious model to reach other customers' models and data.

#### Scenario #3: Compromised Supplier LoRA Adapter

An attacker infiltrates a third-party supplier and subtly alters a LoRA adapter that is later merged into a deployed LLM through a model-merge workflow. Once merged, the adapter provides a covert entry point into the system.

#### Scenario #4: Hijacked Model Conversion or Merge Service

An attacker stages an attack through a model merge or format conversion service to compromise a publicly available model and inject malicious behavior, as shown by HiddenLayer's research on hijacking the Safetensors conversion bot on Hugging Face.

#### Scenario #5: Model Namespace Reuse

An organization deploys a model from a public hub by referencing it solely by its `Author/ModelName` identifier. The original author deletes or transfers the account, freeing the namespace, and an attacker re-registers the same name and publishes a malicious model under the original path. Pipelines and managed model catalogs that resolve the model by name alone then pull the attacker's model, leading to remote code execution.

#### Scenario #6: Scanner, Safe-Loader, and Safe-Format Bypass

An organization gates third-party models behind a malware scanner and a loader option documented as safe against code execution. An attacker defeats both: corrupted or compression-wrapped pickle streams execute their payload before the scanner reaches the broken byte, as in the nullifAI models found on Hugging Face; both model scanners and safe-loader flags have had bypasses assigned CVEs, such as the PickleScan zero-days and `torch.load` with `weights_only` (CVE-2025-32434); and a ShadowLogic-style backdoor in the computational graph of a "safe" format like ONNX attaches no executable code for a serialization scanner to flag. Treat scanners and safe-loader flags as defense-in-depth layers rather than guarantees, alongside provenance verification and patched loaders and parsers.

#### Scenario #7: Compromised Build Pipeline for Model Artifacts

An attacker compromises the CI/CD pipeline an organization uses to fine-tune and publish models — through a malicious build-workflow dependency, a stolen artifact-registry credential, or cache poisoning, as in the Ultralytics attack, where GitHub Actions cache injection published trojanized PyPI releases of a flagship AI library, including a compromised "fix" release — the same build-time substitution seen in classical incidents such as the xz-utils backdoor and the Codecov breach. Because the backdoored artifact is built and signed by the organization's own release infrastructure, it passes downstream provenance checks, internal attestation, and supply-chain scanners that only flag externally sourced components.

#### Scenario #8: Reverse-Engineered Mobile App

An attacker reverse-engineers a mobile app to replace the on-device model with a tampered version that leads users to scam sites, distributing the re-packaged app through social engineering.

### Reference Links

1. [PoisonGPT: How we hid a lobotomized LLM on Hugging Face to spread fake news](https://blog.mithrilsecurity.io/poisongpt-how-we-hid-a-lobotomized-llm-on-hugging-face-to-spread-fake-news): **Mithril Security**
2. [Hijacking Safetensors Conversion on Hugging Face](https://hiddenlayer.com/research/silent-sabotage/): **HiddenLayer**
3. [AI Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010): **MITRE ATLAS**
4. [Removing RLHF Protections in GPT-4 via Fine-Tuning](https://arxiv.org/abs/2311.05553): **Qiusi Zhan et al., arXiv**
5. [We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs](https://arxiv.org/abs/2406.10279): **Joseph Spracklen et al., arXiv**
6. [ShadowRay 2.0: Attackers Turn AI Against Itself in Global Campaign that Hijacks AI Into Self-Propagating Botnet](https://www.oligo.security/blog/shadowray-2-0-attackers-turn-ai-against-itself-in-global-campaign-that-hijacks-ai-into-self-propagating-botnet): **Oligo Security**
7. [Model Namespace Reuse: An AI Supply-Chain Attack Exploiting Model Name Trust](https://unit42.paloaltonetworks.com/model-namespace-reuse/): **Unit 42, Palo Alto Networks**
8. [Malicious ML models discovered on Hugging Face platform (nullifAI)](https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face): **ReversingLabs**
9. [PyTorch Users at Risk: Unveiling 3 Zero-Day PickleScan Vulnerabilities](https://jfrog.com/blog/unveiling-3-zero-day-vulnerabilities-in-picklescan/): **JFrog**
10. [PyTorch torch.load weights_only bypass (CVE-2025-32434)](https://github.com/pytorch/pytorch/security/advisories/GHSA-53q9-r3pm-6pq6): **GitHub Security Advisories**
11. [ShadowLogic: Persistent No-Code Backdoors in AI Computational Graphs](https://hiddenlayer.com/innovation-hub/shadowlogic/): **HiddenLayer**
12. [Launch of Model Signing v1.0: OpenSSF AI/ML Working Group Secures the Machine Learning Supply Chain](https://openssf.org/blog/2025/04/04/launch-of-model-signing-v1-0-openssf-ai-ml-working-group-secures-the-machine-learning-supply-chain/): **OpenSSF**
13. [Coalition for Secure AI Releases Two Actionable Frameworks for AI Model Signing and Incident Response](https://www.oasis-open.org/2025/11/18/coalition-for-secure-ai-releases-two-actionable-frameworks-for-ai-model-signing-and-incident-response/): **OASIS / CoSAI**
14. [Evolving AI Transparency: The Journey of the AIBOM Generator and Its New Home at OWASP](https://genai.owasp.org/2025/12/18/evolving-ai-transparency-the-journey-of-the-aibom-generator-and-its-new-home-at-owasp/): **OWASP GenAI Security Project**
15. [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/): **OWASP GenAI Security Project**
16. [Mind the Gap: A Practical Attack on GGUF Quantization](https://arxiv.org/abs/2505.23786): **Kazuki Egashira et al., arXiv**
17. [Compromised PyTorch-nightly dependency chain between December 25th and December 30th, 2022](https://pytorch.org/blog/compromised-nightly-dependency/): **PyTorch**
18. [llama.cpp GGUF library gguf_fread_str heap-based buffer overflow vulnerability (TALOS-2024-1913)](https://talosintelligence.com/vulnerability_reports/TALOS-2024-1913): **Cisco Talos**
19. [Probllama: Ollama Remote Code Execution Vulnerability (CVE-2024-37032)](https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032): **Wiz**
20. [Wiz Research finds architecture risks that may compromise AI-as-a-Service providers](https://www.wiz.io/blog/wiz-and-hugging-face-address-risks-to-ai-infrastructure): **Wiz**
21. [Supply-chain attack analysis: Ultralytics](https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/): **PyPI Blog**
22. [Machine Learning Bill of Materials (ML-BOM)](https://cyclonedx.org/capabilities/mlbom/): **OWASP CycloneDX**
23. [Supply-chain Levels for Software Artifacts (SLSA)](https://slsa.dev): **OpenSSF**

### Related Frameworks and Taxonomies

| Framework | Reference | Relevance |
|---|---|---|
| **OWASP Top 10 for Agentic Applications (ASI)** | ASI04 — Agentic Supply Chain Vulnerabilities | This entry's own scope note defers agentic-specific supply-chain risk to ASI04, leaving this entry to cover the non-agentic model, dataset, and artifact supply chain |
| **MITRE ATLAS** | [AML.T0010 — AI Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010) | Sub-techniques for Hardware (.000), AI Software (.001), Data (.002), Model (.003), Container Registry (.004), and AI Agent Tool (.005) |
| **MITRE ATT&CK** | T1195 — Supply Chain Compromise | Classical software supply-chain compromise underlying this entry's package and pipeline risks (risk #1; Scenario #1, torchtriton/PyPI; Scenario #18, xz-utils and Codecov) |
| **CycloneDX (ECMA-424)** | [ML-BOM](https://cyclonedx.org/capabilities/mlbom/) | Bill-of-materials standard for model/dataset inventory, named in this entry's AIBOM/ML-SBOM mitigation (#4) and license-audit mitigation (#5) |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI04 — Data, Model & Artifact Poisoning | States it "extends LLM03:2025 (LLM Supply Chain) and ASI04 with a data-integrity lens, focusing on the training corpus and artifact pipeline attack surface"; its DBOM and full-chain artifact-signing controls mirror this entry's AIBOM/ML-SBOM (mitigation #4) and cryptographic model-signing (mitigation #6) |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI05 — Data Integrity & Validation Failures | Covers snapshot-import path traversal against "vector databases, model registries, and feature stores" and requires signed, checksum-verified artifacts "on every import and promotion event" — the same promotion-boundary trust failure as this entry's unsigned/replaceable-artifact risk (#10) and root-of-trust mitigation (#11) |
| **OWASP GenAI Data Security 2026 (v1.0)** | DSGAI03 — Shadow AI & Unsanctioned Data Flows | Its adversary model, naming "SaaS providers that retain prompts for training" and "vendors that change data handling practices post-adoption", is related to this entry's risk #9 (unclear model-operator T&Cs), Scenario #13, and the supplier-vetting mitigation #1, which its approved-vendor contract controls mirror |
