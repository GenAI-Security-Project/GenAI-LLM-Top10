#!/usr/bin/env python3
"""Regression tests for the 2026 entry contract validator."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_entry_contract as contract  # noqa: E402


GOOD = """## LLM01:2026 Prompt Injection

### Description

Injected instructions override the intended task.

### Common Examples of Risk

1. Direct injection in the user prompt.

### Prevention and Mitigation Strategies

1. Constrain tool execution outside the model.

### Example Attack Scenarios

1. A retrieved page tells the agent to exfiltrate mail.
"""


class EntryContractTest(unittest.TestCase):
    def test_published_entries_match_the_contract(self) -> None:
        errors = contract.validate_directory(contract.FINAL_DIR)
        self.assertEqual(errors, [])

    def test_missing_section_is_rejected(self) -> None:
        text = GOOD.replace("### Example Attack Scenarios\n\n1. A retrieved page tells the agent to exfiltrate mail.\n", "")
        errors = contract.validate_text("LLM01_PromptInjection.md", text)
        self.assertTrue(any("Example Attack Scenarios" in error for error in errors), errors)

    def test_renamed_title_is_rejected(self) -> None:
        errors = contract.validate_text(
            "LLM01_PromptInjection.md",
            GOOD.replace("Prompt Injection", "Prompt Smuggling"),
        )
        self.assertTrue(errors)

    def test_script_markup_is_rejected(self) -> None:
        errors = contract.validate_text(
            "LLM01_PromptInjection.md",
            GOOD + "\n<script>alert(1)</script>\n",
        )
        self.assertTrue(any("script" in error for error in errors), errors)

    def test_empty_prevention_section_is_rejected(self) -> None:
        text = GOOD.replace(
            "### Prevention and Mitigation Strategies\n\n1. Constrain tool execution outside the model.\n",
            "### Prevention and Mitigation Strategies\n\n",
        )
        errors = contract.validate_text("LLM01_PromptInjection.md", text)
        self.assertTrue(any("empty" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
