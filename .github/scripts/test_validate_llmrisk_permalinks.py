#!/usr/bin/env python3
"""Offline tests for the 2026 /llmrisk/ permalink contract.

    python .github/scripts/test_validate_llmrisk_permalinks.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_llmrisk_permalinks as v  # noqa: E402


class PermalinkContractTest(unittest.TestCase):
    def test_repository_contract_holds(self) -> None:
        self.assertEqual(v.validate(), [])

    def test_derived_slug_includes_year_for_llm01(self) -> None:
        slug = v.canonical_slug("LLM01", "2026", "Prompt Injection")
        self.assertEqual(slug, "llm012026-prompt-injection")
        self.assertNotEqual(slug, "llm01-prompt-injection")

    def test_title_slug_keeps_and(self) -> None:
        self.assertEqual(
            v.canonical_slug("LLM05", "2026", "Data and Model Poisoning"),
            "llm052026-data-and-model-poisoning",
        )

    def test_rejects_yearless_llm01_and_unknown_link(self) -> None:
        registry = v.load_registry()
        headings = v.entry_headings()
        text = (
            "See https://genai.owasp.org/llmrisk/llm01-prompt-injection/ "
            "and https://genai.owasp.org/llmrisk/llm012026-not-a-real-entry/"
        )
        problems = v.problems_for(registry, headings, [("2026/final/fixture.md", text)])
        self.assertTrue(any("llm012026-not-a-real-entry" in item for item in problems), problems)
        self.assertFalse(any("llm01-prompt-injection/" in item and "not canonical" in item for item in problems), problems)

    def test_historical_2025_link_in_references_is_allowed(self) -> None:
        registry = v.load_registry()
        headings = v.entry_headings()
        text = "https://genai.owasp.org/llmrisk/llm092025-misinformation/"
        problems = v.problems_for(registry, headings, [("2026/final/references.md", text)])
        self.assertEqual(problems, [])

    def test_registry_slug_drift_fails(self) -> None:
        registry = json.loads(json.dumps(v.load_registry()))
        registry["entries"][0]["slug"] = "llm01-prompt-injection"
        registry["entries"][0]["url"] = v.canonical_url("llm01-prompt-injection")
        problems = v.problems_for(registry, v.entry_headings(), [])
        self.assertTrue(any("LLM01" in item for item in problems), problems)

    def test_copied_tree_without_readme_url_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "2026" / "final"
            final.mkdir(parents=True)
            # Minimal tree: registry, one heading file, table missing the URL, readme missing it.
            registry = {
                "llm01_decision": "normalize-year-infix",
                "entries": [
                    {
                        "id": "LLM01",
                        "year": "2026",
                        "title": "Prompt Injection",
                        "source": "2026/final/LLM01_PromptInjection.md",
                        "slug": "llm012026-prompt-injection",
                        "url": "https://genai.owasp.org/llmrisk/llm012026-prompt-injection/",
                    }
                ],
                "historical_2025": [
                    {"url": "https://genai.owasp.org/llmrisk/llm01-prompt-injection/"}
                ],
            }
            (final / "permalinks.json").write_text(json.dumps(registry), encoding="utf-8")
            (final / "LLM01_PromptInjection.md").write_text(
                "## LLM01:2026 Prompt Injection\n", encoding="utf-8"
            )
            (final / "permalinks.md").write_text("no url here\n", encoding="utf-8")
            (root / "2026" / "README.md").write_text("no url here\n", encoding="utf-8")
            problems = v.validate(root)
            self.assertTrue(any("permalinks.md missing" in item for item in problems), problems)
            self.assertTrue(any("README.md missing" in item for item in problems), problems)


if __name__ == "__main__":
    unittest.main()
