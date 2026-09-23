"""TDD contract for run-scoped App Lab evidence classification."""
from __future__ import annotations

import unittest

from session_evidence import EvidenceLine, assess_session


class SessionEvidenceTests(unittest.TestCase):
    def test_current_run_ignores_stale_error(self) -> None:
        lines = (
            EvidenceLine("run-old", "python", "ERROR", "dependency failed"),
            EvidenceLine("run-new", "startup", "READY", "startup ready"),
            EvidenceLine("run-new", "python", "STARTED", "main started"),
        )

        decision = assess_session("run-new", lines)

        self.assertEqual(decision.action, "RUNNING")
        self.assertEqual(decision.channels, ("python", "startup"))

    def test_missing_current_lines_is_unknown(self) -> None:
        decision = assess_session(
            "run-new",
            (EvidenceLine("run-old", "startup", "READY", "old run"),),
        )

        self.assertEqual(decision.action, "UNKNOWN_NO_CURRENT_LINES")

    def test_current_error_is_failed(self) -> None:
        decision = assess_session(
            "run-new",
            (
                EvidenceLine("run-new", "startup", "READY", "startup ready"),
                EvidenceLine("run-new", "python", "ERROR", "traceback"),
            ),
        )

        self.assertEqual(decision.action, "FAILED")
        self.assertEqual(decision.reason, "python emitted ERROR")

    def test_stop_marker_wins_after_running_evidence(self) -> None:
        decision = assess_session(
            "run-new",
            (
                EvidenceLine("run-new", "startup", "READY", "startup ready"),
                EvidenceLine("run-new", "python", "STARTED", "main started"),
                EvidenceLine("run-new", "lifecycle", "STOPPED", "user requested stop"),
            ),
        )

        self.assertEqual(decision.action, "STOPPED")

    def test_required_sketch_channel_can_be_added(self) -> None:
        decision = assess_session(
            "run-new",
            (
                EvidenceLine("run-new", "startup", "READY", "startup ready"),
                EvidenceLine("run-new", "python", "STARTED", "main started"),
            ),
            required_channels=("startup", "python", "sketch"),
        )

        self.assertEqual(decision.action, "UNKNOWN_INCOMPLETE")
        self.assertEqual(decision.missing, ("sketch",))


if __name__ == "__main__":
    unittest.main()
