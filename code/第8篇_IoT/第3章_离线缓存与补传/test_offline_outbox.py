"""Behavioral contract for the offline telemetry outbox."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "outbox.py"
EVENT = {
    "schema_version": 1,
    "device_id": "sensor-01",
    "boot_id": "boot-a7",
    "sequence": 42,
    "event_time": "2026-09-24T08:30:00+08:00",
    "metric": "temperature",
    "value": 23.75,
    "unit": "degC",
    "quality": "GOOD",
}


class OfflineOutboxTests(unittest.TestCase):
    def setUp(self) -> None:
        if not SCRIPT.is_file():
            self.fail("outbox.py must implement the durable queue contract")
        sys.path.insert(0, str(HERE))
        import outbox

        self.outbox_module = outbox
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary_directory.name) / "outbox.sqlite3"
        self.queue = outbox.Outbox(self.database, max_items=3, max_payload_bytes=2048)

    def tearDown(self) -> None:
        if hasattr(self, "queue"):
            self.queue.close()
        if hasattr(self, "temporary_directory"):
            self.temporary_directory.cleanup()
        if str(HERE) in sys.path:
            sys.path.remove(str(HERE))

    @staticmethod
    def encode(event: dict[str, object] = EVENT, *, pretty: bool = False) -> bytes:
        return json.dumps(
            event,
            indent=2 if pretty else None,
            separators=None if pretty else (",", ":"),
        ).encode("utf-8")

    def enqueue(self, event: dict[str, object] = EVENT, *, now: int = 1000) -> dict[str, object]:
        return self.queue.enqueue(self.encode(event), now=now, ttl_seconds=60)

    def test_valid_event_is_stored_and_survives_reopening_the_database(self) -> None:
        accepted = self.enqueue()
        self.queue.close()

        reopened = self.outbox_module.Outbox(
            self.database, max_items=3, max_payload_bytes=2048
        )
        try:
            ready = reopened.next_ready(now=1000)
        finally:
            reopened.close()

        self.assertEqual(accepted["outcome"], "ENQUEUED")
        self.assertEqual(ready["event_key"], "sensor-01/boot-a7/42")
        self.assertEqual(json.loads(ready["payload"])["value"], 23.75)

    def test_same_key_and_canonical_payload_is_idempotent_but_changed_payload_conflicts(self) -> None:
        first = self.enqueue()
        reordered = self.queue.enqueue(self.encode(EVENT, pretty=True), now=1001, ttl_seconds=60)
        changed = self.enqueue({**EVENT, "value": 25.0}, now=1002)

        self.assertEqual(first["outcome"], "ENQUEUED")
        self.assertEqual(reordered["outcome"], "DUPLICATE_IGNORED")
        self.assertEqual(changed["outcome"], "CONFLICT_REVIEW")
        self.assertEqual(self.queue.size(), 1)

    def test_full_queue_rejects_newest_without_evicting_existing_events(self) -> None:
        first = self.enqueue()
        second = self.enqueue({**EVENT, "sequence": 43}, now=1001)
        third = self.enqueue({**EVENT, "sequence": 44}, now=1002)
        overflow = self.enqueue({**EVENT, "sequence": 45}, now=1003)

        self.assertEqual([first["outcome"], second["outcome"], third["outcome"]],
                         ["ENQUEUED"] * 3)
        self.assertEqual(overflow["outcome"], "QUEUE_FULL")
        self.assertEqual(self.queue.pending_keys(), [
            "sensor-01/boot-a7/42", "sensor-01/boot-a7/43", "sensor-01/boot-a7/44"
        ])

    def test_payload_larger_than_configured_limit_is_rejected(self) -> None:
        tiny = self.outbox_module.Outbox(
            self.database.parent / "tiny.sqlite3", max_items=2, max_payload_bytes=8
        )
        try:
            result = tiny.enqueue(self.encode(), now=1000, ttl_seconds=60)
        finally:
            tiny.close()

        self.assertEqual(result["outcome"], "PAYLOAD_TOO_LARGE")
        self.assertEqual(self.queue.size(), 0)

    def test_expiry_boundary_is_inclusive_and_expired_keys_are_reported(self) -> None:
        self.enqueue(now=1000)

        self.assertIsNotNone(self.queue.next_ready(now=1059))
        expired = self.queue.expire_due(now=1060)

        self.assertEqual(expired, ["sensor-01/boot-a7/42"])
        self.assertIsNone(self.queue.next_ready(now=1060))
        self.assertEqual(self.queue.size(), 0)

    def test_replay_is_fifo_and_does_not_skip_a_backing_off_head_event(self) -> None:
        self.enqueue(now=1000)
        self.enqueue({**EVENT, "sequence": 43}, now=1001)
        head = self.queue.next_ready(now=1001)
        self.queue.record_outcome(head["event_key"], "RETRYABLE", now=1001)

        blocked = self.queue.next_ready(now=1002)
        first_due = self.queue.next_ready(now=1003)

        self.assertIsNone(blocked)
        self.assertEqual(first_due["event_key"], "sensor-01/boot-a7/42")

    def test_retryable_and_uncertain_outcomes_preserve_key_and_use_capped_backoff(self) -> None:
        self.enqueue()
        original = self.queue.next_ready(now=1000)

        retry = self.queue.record_outcome(
            original["event_key"], "RETRYABLE", now=1000,
            base_backoff_seconds=2, max_backoff_seconds=5,
        )
        self.assertEqual(retry["next_attempt_at"], 1002)
        self.assertIsNone(self.queue.next_ready(now=1001))

        again = self.queue.next_ready(now=1002)
        uncertain = self.queue.record_outcome(
            again["event_key"], "UNCERTAIN", now=1002,
            base_backoff_seconds=2, max_backoff_seconds=5,
        )
        self.assertEqual(uncertain["next_attempt_at"], 1006)
        due = self.queue.next_ready(now=1006)
        self.assertEqual(due["event_key"], original["event_key"])
        self.assertEqual(due["attempts"], 2)

        capped = self.queue.record_outcome(
            due["event_key"], "RETRYABLE", now=1006,
            base_backoff_seconds=2, max_backoff_seconds=5,
        )
        self.assertEqual(capped["retry_delay_seconds"], 5)
        self.assertEqual(capped["next_attempt_at"], 1011)

    def test_acknowledged_hop_removes_only_that_event(self) -> None:
        self.enqueue()
        self.enqueue({**EVENT, "sequence": 43}, now=1001)
        first = self.queue.next_ready(now=1001)

        result = self.queue.record_outcome(first["event_key"], "ACKED", now=1001)

        self.assertEqual(result["outcome"], "ACKED_REMOVED")
        self.assertEqual(self.queue.pending_keys(), ["sensor-01/boot-a7/43"])

    def test_invalid_telemetry_and_invalid_ttl_are_rejected_without_storage(self) -> None:
        invalid = self.queue.enqueue(b"{}", now=1000, ttl_seconds=60)
        bad_ttl = self.queue.enqueue(self.encode(), now=1000, ttl_seconds=0)

        self.assertEqual(invalid["outcome"], "INVALID_REJECTED")
        self.assertEqual(bad_ttl["outcome"], "INVALID_TTL")
        self.assertEqual(self.queue.size(), 0)

    def test_unknown_or_missing_outcome_cannot_delete_the_event(self) -> None:
        self.enqueue()
        with self.assertRaises(ValueError):
            self.queue.record_outcome("sensor-01/boot-a7/42", "SUCCESS", now=1001)

        self.assertEqual(self.queue.size(), 1)

    def test_database_failure_does_not_partially_enqueue(self) -> None:
        with closing(sqlite3.connect(self.database)) as connection:
            with connection:
                connection.execute(
                    """CREATE TRIGGER reject_event BEFORE INSERT ON outbox
                       BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END"""
                )

        with self.assertRaises(sqlite3.IntegrityError):
            self.enqueue()
        self.assertEqual(self.queue.size(), 0)


if __name__ == "__main__":
    unittest.main()
