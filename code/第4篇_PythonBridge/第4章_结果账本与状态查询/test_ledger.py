"""Executable public contract for the Chapter 4 result ledger."""
from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest

from ledger import Evidence, Ledger, LedgerConflict, LedgerEvent, RequestSpec, State
from reconcile_status import Observation, reconcile


def make_request(request_id: str = "req-001") -> RequestSpec:
    return RequestSpec(
        request_id=request_id,
        operation_key="output:led:1",
        operation="set_output",
        payload_digest="sha256:demo",
        generation=1,
        created_at=10.0,
        expires_at=30.0,
    )


class LedgerContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = os.path.join(self.temp_dir.name, "ledger.sqlite3")
        self.ledger = Ledger(self.database)

    def tearDown(self) -> None:
        self.ledger.close()
        self.temp_dir.cleanup()

    def test_create_record_starts_pending(self) -> None:
        record = self.ledger.create(make_request(), now=10.0)
        self.assertEqual(record.state, State.PENDING)

    def test_create_persists_identity_and_initial_event(self) -> None:
        record = self.ledger.create(make_request(), now=10.0)

        self.assertEqual(record.request, make_request())
        self.assertEqual(record.updated_at, 10.0)
        self.assertEqual(
            self.ledger.events("req-001"),
            (LedgerEvent("req-001", None, State.PENDING, None, 10.0),),
        )

    def test_unknown_request_has_no_projection_or_events(self) -> None:
        self.assertIsNone(self.ledger.get("missing"))
        self.assertEqual(self.ledger.events("missing"), ())

    def test_state_vocabulary_is_exactly_seven_members(self) -> None:
        self.assertEqual(
            {state.value for state in State},
            {
                "PENDING", "SENT", "UNKNOWN", "APPLIED",
                "REJECTED", "EXPIRED", "NOT_APPLIED_FINAL",
            },
        )

    def test_intended_pending_sent_unknown_applied_path_is_supported(self) -> None:
        request = make_request()
        self.ledger.create(request, now=10.0)
        self.ledger.transition("req-001", expected=State.PENDING, target=State.SENT,
                               evidence=Evidence("send", "router", 11.0, "accepted"), now=11.0)
        self.ledger.transition("req-001", expected=State.SENT, target=State.UNKNOWN,
                               evidence=Evidence("lost-response", "local", 12.0), now=12.0)
        record = self.ledger.transition(
            "req-001", expected=State.UNKNOWN, target=State.APPLIED,
            evidence=Evidence("authoritative-query", "router", 13.0, "confirmed"), now=13.0
        )
        self.assertEqual(record.state, State.APPLIED)

    def test_sent_rejects_missing_or_non_send_evidence(self) -> None:
        self.ledger.create(make_request(), now=10.0)
        for evidence in (None, Evidence("query", "router", 11.0)):
            with self.subTest(evidence=evidence), self.assertRaises(LedgerConflict):
                self.ledger.transition(
                    "req-001", expected=State.PENDING, target=State.SENT,
                    evidence=evidence, now=11.0,
                )

        self.assertEqual(self.ledger.get("req-001").state, State.PENDING)
        self.assertEqual(len(self.ledger.events("req-001")), 1)

    def test_event_write_failure_rolls_back_current_projection_and_history(self) -> None:
        self.ledger.create(make_request(), now=10.0)
        before_record = self.ledger.get("req-001")
        before_events = self.ledger.events("req-001")
        connection = sqlite3.connect(self.database)
        try:
            connection.execute(
                """
                CREATE TRIGGER abort_second_event
                BEFORE INSERT ON request_events
                WHEN NEW.request_id = 'req-001' AND NEW.sequence = 2
                BEGIN
                    SELECT RAISE(ABORT, 'forced event insert failure');
                END
                """
            )
            connection.commit()
        finally:
            connection.close()

        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.transition(
                "req-001",
                expected=State.PENDING,
                target=State.SENT,
                evidence=Evidence("send", "router", 11.0),
                now=11.0,
            )

        self.assertEqual(self.ledger.get("req-001"), before_record)
        self.assertEqual(self.ledger.events("req-001"), before_events)

    def test_every_allowed_transition_is_supported(self) -> None:
        allowed = (
            (State.PENDING, State.SENT),
            (State.PENDING, State.EXPIRED),
            (State.SENT, State.UNKNOWN),
            (State.SENT, State.APPLIED),
            (State.SENT, State.REJECTED),
            (State.SENT, State.EXPIRED),
            (State.UNKNOWN, State.APPLIED),
            (State.UNKNOWN, State.REJECTED),
            (State.UNKNOWN, State.EXPIRED),
            (State.UNKNOWN, State.NOT_APPLIED_FINAL),
        )
        for source, target in allowed:
            with self.subTest(source=source, target=target):
                request_id = f"{source.value}-{target.value}"
                self.ledger.create(make_request(request_id), now=10.0)
                self._advance_to(request_id, source)
                evidence = Evidence("send", "router", 20.0) if target == State.SENT else Evidence("test", "ledger", 20.0)
                record = self.ledger.transition(
                    request_id,
                    expected=source,
                    target=target,
                    evidence=evidence,
                    now=20.0,
                )
                self.assertEqual(record.state, target)

    def test_terminal_states_have_no_outgoing_transitions(self) -> None:
        terminals = (
            (State.APPLIED, State.SENT),
            (State.REJECTED, State.SENT),
            (State.EXPIRED, State.PENDING),
            (State.NOT_APPLIED_FINAL, State.UNKNOWN),
        )
        for terminal, source in terminals:
            with self.subTest(terminal=terminal):
                request_id = f"terminal-{terminal.value}"
                self.ledger.create(make_request(request_id), now=10.0)
                self._advance_to(request_id, source)
                self.ledger.transition(
                    request_id,
                    expected=source,
                    target=terminal,
                    evidence=Evidence("test", "ledger", 20.0),
                    now=20.0,
                )
                with self.assertRaises(LedgerConflict):
                    self.ledger.transition(
                        request_id,
                        expected=terminal,
                        target=State.PENDING,
                        now=21.0,
                    )

    def test_wrong_expected_state_fails_closed(self) -> None:
        self.ledger.create(make_request(), now=10.0)
        with self.assertRaises(LedgerConflict):
            self.ledger.transition("req-001", expected=State.SENT, target=State.UNKNOWN)

    def test_illegal_transition_fails_closed(self) -> None:
        self.ledger.create(make_request(), now=10.0)
        with self.assertRaises(LedgerConflict):
            self.ledger.transition("req-001", expected=State.PENDING, target=State.APPLIED)

    def test_duplicate_request_id_fails_closed(self) -> None:
        self.ledger.create(make_request(), now=10.0)
        with self.assertRaises(LedgerConflict):
            self.ledger.create(make_request(), now=11.0)

    def test_identity_mismatch_reconciles_safely(self) -> None:
        record = self.ledger.create(make_request(), now=10.0)
        observation = Observation(
            "req-001", "output:led:2", "set_output", "sha256:demo",
            "result", "router", 11.0, True, "different operation key",
        )
        self.assertEqual(reconcile(record, observation, now=11.0).action, "KEEP_UNKNOWN")

    def test_matching_unknown_observation_remains_keep_unknown(self) -> None:
        record = self.ledger.create(make_request(), now=10.0)
        observation = Observation(
            "req-001", "output:led:1", "set_output", "sha256:demo",
            "result", "router", 11.0, False, "not authoritative",
        )
        self.assertEqual(reconcile(record, observation, now=11.0).action, "KEEP_UNKNOWN")

    def test_reopening_database_retains_record_and_event_history(self) -> None:
        self.ledger.create(make_request(), now=10.0)
        self.ledger.transition("req-001", expected=State.PENDING, target=State.SENT,
                               evidence=Evidence("send", "router", 11.0), now=11.0)
        self.ledger.close()
        reopened = Ledger(self.database)
        try:
            self.assertEqual(reopened.get("req-001").state, State.SENT)
            self.assertEqual(len(reopened.events("req-001")), 2)
        finally:
            reopened.close()

    def _advance_to(self, request_id: str, target: State) -> None:
        if target == State.PENDING:
            return
        self.ledger.transition(
            request_id,
            expected=State.PENDING,
            target=State.SENT,
            evidence=Evidence("send", "router", 11.0),
            now=11.0,
        )
        if target == State.UNKNOWN:
            self.ledger.transition(
                request_id,
                expected=State.SENT,
                target=State.UNKNOWN,
                evidence=Evidence("test", "ledger", 12.0),
                now=12.0,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
