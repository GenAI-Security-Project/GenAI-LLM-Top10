# Appendix: Mapping the Top 10 to OWASP AISVS 1.0

## Purpose

The OWASP Top 10 for LLM Applications is a *risk-awareness* document: it names the ten most critical categories of failure and explains, at the level of principles, how to prevent and mitigate each one. The [OWASP AI Security & Privacy Verification Standard (AISVS)](https://github.com/OWASP/AISVS) is a *verification* standard: it decomposes AI security into testable requirements ("**Verify that** …"), each assigned an assurance Level from L1 (baseline) to L3 (advanced).

The two are complementary. This appendix connects them, so a team that has read a Top 10 entry can move directly to the concrete, auditable controls that defend against it. For each risk it answers a single question:

> *"Given this risk, which AISVS requirements should I verify to know I am defended?"*

**Versions mapped:** OWASP Top 10 for LLM Applications **2026** to OWASP AISVS **1.0**.

## How to read this appendix

The **[coverage matrix](#coverage-matrix)** is an at-a-glance grid of all ten risks against the twelve AISVS control chapters. Use it to see where a risk concentrates and which chapters carry the most defensive weight, then read the full text of those chapters in [AISVS 1.0](https://github.com/OWASP/AISVS/tree/main/1.0/en) for the specific `Verify that…` requirements that apply to your system.

Mappings are directional guidance, not a compliance crosswalk: a marked chapter contributes to defending a risk but rarely "closes" it on its own, and a chapter may be relevant to a risk beyond the ones marked here.

Legend: **●** primary defense (the chapter is a main line of defense for this risk) · **○** supporting defense (contributes but is not the center of gravity).

## AISVS 1.0 control chapters

| ID | Chapter |
|---|---|
| **C1** | Training Data Integrity & Traceability |
| **C2** | Input Validation |
| **C3** | Model Lifecycle Management & Change Control |
| **C4** | Infrastructure, Configuration & Deployment Security |
| **C5** | Access Control & Identity for AI Components & Users |
| **C6** | Supply Chain Security for Models |
| **C7** | Model Behavior, Output Control & Safety Assurance |
| **C8** | Memory, Embeddings & Vector Database Security |
| **C9** | Orchestration & Agentic Security |
| **C10** | Model Context Protocol (MCP) Security |
| **C11** | Adversarial Robustness |
| **C12** | Monitoring, Logging & Anomaly Detection |

## Coverage matrix

| Risk | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **LLM01** Prompt Injection | | ● | | | | | ○ | | ● | ● | ● | ● |
| **LLM02** Sensitive Information Disclosure | ○ | | | | ● | | ● | ● | | | ● | ○ |
| **LLM03** Excessive Agency | | | | | ● | | | | ● | ● | | ○ |
| **LLM04** Supply Chain | ○ | | ● | ● | | ● | | | | ○ | | |
| **LLM05** Data & Model Poisoning | ● | | ● | | | ○ | | ● | | | ● | ○ |
| **LLM06** Unbounded Consumption | | | | | ○ | | ○ | | ● | | ● | ● |
| **LLM07** Misinformation | ○ | | | | | | ● | ○ | | | ○ | ● |
| **LLM08** Hidden Context Exposure | | ○ | | | ○ | | ● | | ● | | ● | ○ |
| **LLM09** Vector & Embedding Weaknesses | ○ | | | | ● | | ○ | ● | | | | ○ |
| **LLM10** Improper Output Handling | | | | | | | ● | | ● | ○ | | |

## Notes and caveats

- **Directional, not certifying.** A chapter is marked for a risk because verifying its controls *contributes to* defending that risk. Full coverage of a risk generally requires controls from several chapters plus system-specific design decisions AISVS cannot encode.
- **Chapters, not individual requirements.** The matrix maps at chapter granularity (C1 through C12). Within each marked chapter, the applicable `Verify that…` requirements and their assurance Levels (from L1 baseline to L3 advanced) depend on your system; consult the chapter text in AISVS 1.0.
- **Agentic amplification.** Several 2026 entries note that their risks amplify in agentic and multi-agent systems. Where that is the case, AISVS **C9** (Orchestration & Agentic Security) and **C10** (MCP Security) carry defenses that this appendix maps, but the [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/) remains the primary reference for agent-specific threats.
- **Living mapping.** Both documents evolve. This appendix maps Top 10 **2026** to AISVS **1.0**; revisit it when either advances a version.
