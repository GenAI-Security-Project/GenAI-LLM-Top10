# Canonical 2026 /llmrisk/ permalinks

Stable per-entry URLs for the OWASP Top 10 for LLM Applications (2026). The machine-readable copy is [`permalinks.json`](./permalinks.json).

The 2025 site published ten `llmrisk` pages. Nine use `/llmrisk/llmXX2025-<slug>/`. LLM01 does not: the live 2025 page is [`/llmrisk/llm01-prompt-injection/`](https://genai.owasp.org/llmrisk/llm01-prompt-injection/), with no year infix. A generator that copies "the existing pattern" therefore already 404s on `llm012025-prompt-injection`.

The 2026 set does not carry that exception forward. Every 2026 entry, including LLM01, uses `/llmrisk/llmXX2026-<slug>/`. The slug is the H1 title, lowercased, with punctuation turned into hyphens. These are the 2026 numbers, not the 2025 numbers. Excessive Agency is LLM03 in 2026 (it was LLM06 in 2025). Unbounded Consumption is LLM06 in 2026 (it was LLM10 in 2025). Improper Output Handling is LLM10 in 2026 (it was LLM05 in 2025).

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

Integrators should use these URLs. Do not point a 2026 entry at its 2025 page, and do not point every entry only at the aggregate publication [https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/).

The `llmrisk` post type on genai.owasp.org is what publishes these paths. Until those ten 2026 posts exist, the URLs above are the contract for that publication, not a claim that the posts are already live. `.github/scripts/validate_llmrisk_permalinks.py` rejects any `/llmrisk/` link under `2026/final/` that is not in this list or in the recorded 2025 historical set.
