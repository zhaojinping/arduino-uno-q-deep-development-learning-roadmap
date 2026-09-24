"""Behavior tests for the offline MQTT redelivery/idempotency lesson."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "idempotent_consumer.py"
EVENT = {
    "schema_version": 1,
    "device_id": "sensor-01",
    "boot_id": "boot-a7",
    "sequence": 42,
    "event_time": "2026-09-24T10:30:00+08:00",
    "metric": "temperature",
    "value": 23.75,
    "unit": "degC",
    "quality": "GOOD",
}


class IdempotentConsumerTests(unittest.TestCase):
    def setUp(self) -> None:
        if not SCRIPT.is_file():
            self.fail("idempotent_consumer.py must implement this contract")
        sys.path.insert(0, str(HERE))
        import idempotent_consumer

        self.consumer = idempotent_consumer
        self.connection = sqlite3.connect(":memory:")
        self.consumer.initialize_database(self.connection)

    def tearDown(self) -> None:
        if hasattr(self, "connection"):
            self.connection.close()
        if str(HERE) in sys.path:
            sys.path.remove(str(HERE))

    @staticmethod
    def encode(event: dict[str, object]) -> bytes:
        return json.dumps(event, separators=(",", ":")).encode("utf-8")

    def table_count(self, table: str) -> int:
        return self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_first_delivery_applies_and_same_redelivery_is_ignored(self) -> None:
        first = self.consumer.consume_delivery(self.connection, self.encode(EVENT))
        second = self.consumer.consume_delivery(self.connection, self.encode(EVENT))

        self.assertEqual(first["outcome"], "APPLIED")
        self.assertEqual(second["outcome"], "DUPLICATE_IGNORED")
        self.assertEqual(self.table_count("processed_events"), 1)
        self.assertEqual(self.table_count("simulated_effects"), 1)

    def test_same_sequence_in_a_new_boot_is_a_distinct_event(self) -> None:
        next_boot = {**EVENT, "boot_id": "boot-b8"}

        first = self.consumer.consume_delivery(self.connection, self.encode(EVENT))
        second = self.consumer.consume_delivery(self.connection, self.encode(next_boot))

        self.assertEqual(first["event_key"], "sensor-01/boot-a7/42")
        self.assertEqual(second["event_key"], "sensor-01/boot-b8/42")
        self.assertEqual(second["outcome"], "APPLIED")
        self.assertEqual(self.table_count("processed_events"), 2)
        self.assertEqual(self.table_count("simulated_effects"), 2)

    def test_same_event_key_with_different_payload_requires_review(self) -> None:
        changed_payload = {**EVENT, "value": 99.0}
        self.consumer.consume_delivery(self.connection, self.encode(EVENT))

        conflict = self.consumer.consume_delivery(
            self.connection, self.encode(changed_payload)
        )

        self.assertEqual(conflict["outcome"], "CONFLICT_REVIEW")
        self.assertEqual(self.table_count("processed_events"), 1)
        self.assertEqual(self.table_count("simulated_effects"), 1)

    def test_database_failure_rolls_back_ledger_and_effect_together(self) -> None:
        self.connection.execute(
            """CREATE TRIGGER reject_effect BEFORE INSERT ON simulated_effects
               BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END"""
        )

        with self.assertRaises(sqlite3.IntegrityError):
            self.consumer.consume_delivery(self.connection, self.encode(EVENT))

        self.assertEqual(self.table_count("processed_events"), 0)
        self.assertEqual(self.table_count("simulated_effects"), 0)
        self.connection.execute("DROP TRIGGER reject_effect")
        retry = self.consumer.consume_delivery(self.connection, self.encode(EVENT))
        self.assertEqual(retry["outcome"], "APPLIED")

    def test_duplicate_after_a_new_process_is_not_applied_again(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            database = temp / "consumer.sqlite3"
            delivery = temp / "delivery.jsonl"
            delivery.write_text(
                json.dumps(EVENT, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            command = [
                sys.executable,
                "-B",
                str(SCRIPT),
                "--database",
                str(database),
                "--deliveries",
                str(delivery),
            ]

            first_process = subprocess.run(
                command, capture_output=True, check=False, text=True
            )
            second_process = subprocess.run(
                command, capture_output=True, check=False, text=True
            )

            self.assertEqual(first_process.returncode, 0, first_process.stderr)
            self.assertEqual(second_process.returncode, 0, second_process.stderr)
            self.assertEqual(json.loads(first_process.stdout)["outcome"], "APPLIED")
            self.assertEqual(
                json.loads(second_process.stdout)["outcome"], "DUPLICATE_IGNORED"
            )
            with closing(sqlite3.connect(database)) as connection:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM simulated_effects").fetchone()[0],
                    1,
                )


if __name__ == "__main__":
    unittest.main()
