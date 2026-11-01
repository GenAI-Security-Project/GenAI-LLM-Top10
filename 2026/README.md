# OWASP Top 10 for LLM Applications 2026

* **Status:** Published
* **Release date:** August 4, 2026
* **Official publication:** [Get the OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)

The files in [`final/`](./final/) are the canonical Markdown source for the published 2026 release. Files under [`working/`](./working/) record the completed community process and retain the pre-renumbering drafts, candidate entries, polling tools, and contribution instructions used during the release cycle.

## Final List

| Entry | Source |
|---|---|
| LLM01:2026 Prompt Injection | [`LLM01_PromptInjection.md`](./final/LLM01_PromptInjection.md) |
| LLM02:2026 Sensitive Information Disclosure | [`LLM02_SensitiveInformationDisclosure.md`](./final/LLM02_SensitiveInformationDisclosure.md) |
| LLM03:2026 Excessive Agency | [`LLM03_ExcessiveAgency.md`](./final/LLM03_ExcessiveAgency.md) |
| LLM04:2026 Supply Chain | [`LLM04_SupplyChain.md`](./final/LLM04_SupplyChain.md) |
| LLM05:2026 Data and Model Poisoning | [`LLM05_DataModelPoisoning.md`](./final/LLM05_DataModelPoisoning.md) |
| LLM06:2026 Unbounded Consumption | [`LLM06_UnboundedConsumption.md`](./final/LLM06_UnboundedConsumption.md) |
| LLM07:2026 Misinformation | [`LLM07_Misinformation.md`](./final/LLM07_Misinformation.md) |
| LLM08:2026 Hidden Context Exposure | [`LLM08_HiddenContextExposure.md`](./final/LLM08_HiddenContextExposure.md) |
| LLM09:2026 Vector and Embedding Weaknesses | [`LLM09_VectorAndEmbeddingWeaknesses.md`](./final/LLM09_VectorAndEmbeddingWeaknesses.md) |
| LLM10:2026 Improper Output Handling | [`LLM10_ImproperOutputHandling.md`](./final/LLM10_ImproperOutputHandling.md) |

The release also includes [related framework mappings](./final/Appendix_A_Related_Framework_Mappings.md) (with machine-readable versions under [`final/mappings/`](./final/mappings/)), an [application architecture and threat modeling appendix](./final/Appendix_B_LLM_Application_Architecture_and_Threat_Modeling.md), a [consolidated references file](./final/references.md), and publication figures under [`final/report/images/`](./final/report/images/).

## Canonical per-entry URLs

Stable `/llmrisk/` permalinks for the ten 2026 entries. The 2025 LLM01 page is [`/llmrisk/llm01-prompt-injection/`](https://genai.owasp.org/llmrisk/llm01-prompt-injection/), with no year infix. The 2026 set does not carry that exception forward: every entry, including LLM01, uses `/llmrisk/llmXX2026-<slug>/`. These are the 2026 numbers. Do not reuse a 2025 slug for a renumbered entry.

| Entry | Canonical URL |
|---|---|
| LLM01:2026 Prompt Injection | https://genai.owasp.org/llmrisk/llm012026-prompt-injection/ |
| LLM02:2026 Sensitive Information Disclosure | https://genai.owasp.org/llmrisk/llm022026-sensitive-information-disclosure/ |
| LLM03:2026 Excessive Agency | https://genai.owasp.org/llmrisk/llm032026-excessive-agency/ |
| LLM04:2026 Supply Chain | https://genai.owasp.org/llmrisk/llm042026-supply-chain/ |
| LLM05:2026 Data and Model Poisoning | https://genai.owasp.org/llmrisk/llm052026-data-and-model-poisoning/ |
| LLM06:2026 Unbounded Consumption | https://genai.owasp.org/llmrisk/llm062026-unbounded-consumption/ |
| LLM07:2026 Misinformation | https://genai.owasp.org/llmrisk/llm072026-misinformation/ |
| LLM08:2026 Hidden Context Exposure | https://genai.owasp.org/llmrisk/llm082026-hidden-context-exposure/ |
| LLM09:2026 Vector and Embedding Weaknesses | https://genai.owasp.org/llmrisk/llm092026-vector-and-embedding-weaknesses/ |
| LLM10:2026 Improper Output Handling | https://genai.owasp.org/llmrisk/llm102026-improper-output-handling/ |

The same table is in [`final/permalinks.md`](./final/permalinks.md), and the machine-readable list is [`final/permalinks.json`](./final/permalinks.json). Until the site publishes these ten posts, this registry is the slug contract for that publication. Integrators should use these URLs rather than the 2025 pages or only the aggregate resource URL.

## Corrections and Feedback

* [Report a specific error or publication mismatch](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/issues/new?template=release-errata.yml)
* [Submit broader release feedback](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/issues/new?template=release-feedback.yml)

Changes to the canonical source must be submitted through a pull request and follow the repository's review and branch-protection requirements.
