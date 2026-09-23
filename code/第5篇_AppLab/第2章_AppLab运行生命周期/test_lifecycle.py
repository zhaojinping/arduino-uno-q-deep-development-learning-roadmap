"""TDD contract for the local App Lab run lifecycle model."""
from __future__ import annotations

import unittest

from lifecycle import LifecycleError, advance, new_session


class LifecycleTests(unittest.TestCase):
    def test_new_session_starts_at_imported(self) -> None:
        session = new_session("run-001")

        self.assertEqual(session.run_id, "run-001")
        self.assertEqual(session.phase, "IMPORTED")
        self.assertEqual(session.history, ("IMPORTED",))

    def test_valid_sequence_reaches_running_with_history(self) -> None:
        session = new_session("run-001")
        for phase in ("PREPARING", "STARTING", "RUNNING"):
            session = advance(session, phase)

        self.assertEqual(session.phase, "RUNNING")
        self.assertEqual(
            session.history,
            ("IMPORTED", "PREPARING", "STARTING", "RUNNING"),
        )

    def test_invalid_transition_preserves_previous_session(self) -> None:
        session = new_session("run-001")

        with self.assertRaisesRegex(LifecycleError, "IMPORTED cannot advance to STOPPED"):
            advance(session, "STOPPED")

        self.assertEqual(session.phase, "IMPORTED")
        self.assertEqual(session.history, ("IMPORTED",))

    def test_empty_run_id_is_rejected(self) -> None:
        with self.assertRaisesRegex(LifecycleError, "run_id must not be empty"):
            new_session("  ")

    def test_terminal_session_cannot_restart_in_place(self) -> None:
        session = new_session("run-001")
        for phase in ("PREPARING", "STARTING", "RUNNING", "STOPPING", "STOPPED"):
            session = advance(session, phase)

        with self.assertRaisesRegex(LifecycleError, "STOPPED cannot advance to PREPARING"):
            advance(session, "PREPARING")


if __name__ == "__main__":
    unittest.main()
