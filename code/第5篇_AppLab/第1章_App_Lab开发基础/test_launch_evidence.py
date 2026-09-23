"""Executable contract for App Lab launch-log evidence gates."""
from __future__ import annotations

import unittest

from launch_evidence import LaunchEvidence, assess_launch


class LaunchEvidenceTests(unittest.TestCase):
    def test_startup_compile_failure_blocks_all_conclusions(self) -> None:
        decision = assess_launch(
            LaunchEvidence("COMPILE_FAILED", ("not started",), True, ())
        )

        self.assertEqual(decision.action, "BLOCKED_STARTUP")

    def test_python_only_app_needs_python_log(self) -> None:
        decision = assess_launch(LaunchEvidence("READY", ("INFO app started",), False, ()))

        self.assertEqual(decision.action, "PYTHON_LOG_READY")
        self.assertIn("Python", decision.reason)

    def test_sketch_app_requires_sketch_log_and_device_assertion(self) -> None:
        decision = assess_launch(
            LaunchEvidence("READY", ("INFO app started",), True, ("INFO sketch started",))
        )

        self.assertEqual(decision.action, "SKETCH_LOG_READY_NEEDS_DEVICE_ASSERTION")

    def test_missing_sketch_log_is_not_success(self) -> None:
        decision = assess_launch(LaunchEvidence("READY", ("INFO app started",), True, ()))

        self.assertEqual(decision.action, "MISSING_SKETCH_LOG")

    def test_runtime_error_is_reported_by_its_side(self) -> None:
        python_error = assess_launch(
            LaunchEvidence("READY", ("ERROR import failed",), False, ())
        )
        sketch_error = assess_launch(
            LaunchEvidence("READY", ("INFO app started",), True, ("ERROR setup failed",))
        )

        self.assertEqual(python_error.action, "PYTHON_RUNTIME_ERROR")
        self.assertEqual(sketch_error.action, "SKETCH_RUNTIME_ERROR")


if __name__ == "__main__":
    unittest.main()
