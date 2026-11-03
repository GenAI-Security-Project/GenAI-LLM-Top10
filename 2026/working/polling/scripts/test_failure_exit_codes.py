#!/usr/bin/env python3
"""Tests for the exit codes of create_issues.py and sync_sprint2.py.

GitHub is replaced with stubbed HTTP responses, so no token or network access
is needed.

    python 2026/working/polling/scripts/test_failure_exit_codes.py
"""

from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import create_issues as ci  # noqa: E402
import sync_sprint2 as ss  # noqa: E402

ENTRY_B = {"id": "LLM01", "title": "Prompt Injection", "file": "LLM01_PromptInjection.md"}
ENTRY_A = {"id": "TA-CFAS", "title": "Alignment Subversion", "file": "TA_CFAS.md"}
FORM_URL = "https://example.test/form"


def run_quietly(func, *args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = func(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()


class CreateIssuesExitCodes(unittest.TestCase):
    def run_main(self, responses, extra_args=()):
        calls = []

        def fake_request(method, path, token, body=None):
            calls.append((method, path))
            return responses[min(len(calls), len(responses)) - 1]

        argv = ["create_issues.py", "--form-url", FORM_URL, "--skip-labels",
                "--only-ids", "LLM01,TA-CFAS", *extra_args]
        with mock.patch.object(ci, "_request", fake_request), \
                mock.patch.object(ci.time, "sleep", lambda s: None), \
                mock.patch.dict(ci.os.environ, {"GH_TOKEN": "x"}), \
                mock.patch.object(sys, "argv", argv):
            rc, out, err = run_quietly(ci.main)
        return rc, out, err, calls

    def test_all_requests_failing_with_401_exit_2(self):
        rc, out, err, calls = self.run_main([(401, {"message": "Bad credentials"})])
        self.assertEqual(len(calls), 2)
        self.assertEqual(rc, 2)
        self.assertNotIn("done.", out)
        self.assertIn("LLM01", err)

    def test_server_error_exits_2_and_reports_partial_success(self):
        rc, out, err, calls = self.run_main([
            (201, {"number": 7, "html_url": "https://example.test/7"}),
            (500, {"message": "Server Error"}),
        ])
        self.assertEqual(rc, 2)
        self.assertIn("#7", out)
        self.assertIn("TA-CFAS", err)
        self.assertIn("LLM01", err)

    def test_success_exits_0(self):
        rc, out, err, _ = self.run_main([(201, {"number": 1, "html_url": "u"})])
        self.assertEqual(rc, 0)
        self.assertIn("done.", out)

    def test_dry_run_exits_0_without_requests(self):
        rc, _, _, calls = self.run_main([(500, {})], extra_args=("--dry-run",))
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [])

    def test_post_issue_raises_instead_of_returning_none_on_failure(self):
        with mock.patch.object(ci, "_request", lambda *a, **k: (401, {"message": "no"})):
            with self.assertRaises(ci.IssueCreateError):
                run_quietly(ci.post_issue, "t", "b", [], "x", False)
        self.assertIsNone(run_quietly(ci.post_issue, "t", "b", [], "x", True)[0])


class SyncSprint2Summary(unittest.TestCase):
    CONFIG = {"labels": [], "track_a": [], "track_b": [ENTRY_B]}

    def sync(self, status, **kwargs):
        existing = kwargs.pop("existing", [])
        diff = kwargs.pop("diff", {})
        body = {"number": 9, "html_url": "u"} if status in (200, 201) else {"message": "err"}
        with mock.patch.object(ci, "_request", lambda *a, **k: (status, body)), \
                mock.patch.object(ss, "_request", lambda *a, **k: (status, body, {})), \
                mock.patch.object(ss.time, "sleep", lambda s: None), \
                mock.patch.object(ci.time, "sleep", lambda s: None):
            summary, _, _ = run_quietly(
                ss.sync_github_issues, self.CONFIG, diff, FORM_URL, "x", False, existing, **kwargs)
        return summary

    def test_failed_create_is_not_recorded_as_created(self):
        for status in (401, 500):
            with self.subTest(status=status):
                summary = self.sync(status)
                self.assertEqual(summary["created"], [])
                self.assertEqual(summary["failed"], ["LLM01"])

    def test_successful_create_is_recorded(self):
        summary = self.sync(201)
        self.assertEqual(summary["created"], ["LLM01"])
        self.assertEqual(summary["failed"], [])

    def test_failed_force_rebuild_patch_is_not_recorded_as_updated(self):
        existing = [{"number": 36, "title": "t", "labels": [{"name": "LLM01"}]}]
        for status in (401, 500):
            with self.subTest(status=status):
                summary = self.sync(status, existing=existing, force_rebuild=True)
                self.assertEqual(summary["updated"], [])
                self.assertEqual(summary["failed"], ["LLM01"])

    def test_failed_changed_entry_patch_is_not_updated_or_retried(self):
        existing = [{"number": 36, "title": "t", "labels": [{"name": "LLM01"}]}]
        diff = {"changed_b": [(ENTRY_B, dict(ENTRY_B, title="Renamed"))]}
        summary = self.sync(500, existing=existing, diff=diff, force_rebuild=True)
        self.assertEqual(summary["updated"], [])
        self.assertEqual(summary["failed"], ["LLM01"])
        self.assertEqual(summary["skipped_unchanged"], [])

    def test_successful_patch_is_recorded(self):
        existing = [{"number": 36, "title": "t", "labels": [{"name": "LLM01"}]}]
        summary = self.sync(200, existing=existing, force_rebuild=True)
        self.assertEqual(summary["updated"], ["LLM01"])
        self.assertEqual(summary["failed"], [])


class SyncSprint2MainExitCode(unittest.TestCase):
    def run_main(self, status):
        config = {
            "_meta": {"form": {"published_url": FORM_URL}},
            "labels": [], "track_a": [], "track_b": [],
        }
        body = {"number": 9, "html_url": "u"} if status == 201 else {"message": "err"}
        argv = ["sync_sprint2.py"]
        with mock.patch.object(ss, "fetch_remote_registry", lambda *a: config), \
                mock.patch.object(ss, "load_existing_from_remote", lambda *a: [ENTRY_B]), \
                mock.patch.object(ss, "load_candidates_from_remote", lambda *a: ([], [])), \
                mock.patch.object(ss, "fetch_issues_with_label", lambda *a: []), \
                mock.patch.object(ss, "write_config", lambda c: None), \
                mock.patch.object(ci, "_request", lambda *a, **k: (status, body)), \
                mock.patch.object(ss.time, "sleep", lambda s: None), \
                mock.patch.object(ci.time, "sleep", lambda s: None), \
                mock.patch.dict(ss.os.environ, {"GH_TOKEN": "x"}), \
                mock.patch.object(sys, "argv", argv):
            return run_quietly(ss.main)

    def test_failed_create_exits_2_and_hides_next_steps(self):
        for status in (401, 500):
            with self.subTest(status=status):
                rc, out, err = self.run_main(status)
                self.assertEqual(rc, 2)
                self.assertNotIn("NEXT STEPS", out)
                self.assertIn("LLM01", err)

    def test_successful_create_exits_0_with_next_steps(self):
        rc, out, _ = self.run_main(201)
        self.assertEqual(rc, 0)
        self.assertIn("NEXT STEPS", out)


if __name__ == "__main__":
    unittest.main()
