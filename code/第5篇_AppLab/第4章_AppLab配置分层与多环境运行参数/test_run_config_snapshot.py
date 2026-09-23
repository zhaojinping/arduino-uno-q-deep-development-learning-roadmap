"""TDD contract for redacted, deterministic run configuration snapshots."""
from __future__ import annotations

import unittest

from run_config_snapshot import SnapshotError, build_snapshot


class RunConfigSnapshotTests(unittest.TestCase):
    def test_snapshot_is_order_independent_and_redacts_secrets(self) -> None:
        first = build_snapshot(
            "run-042",
            "staging",
            {"LOG_LEVEL": "debug", "DB_PASSWORD": "do-not-print", "APP_MODE": "staging"},
            secret_keys=("DB_PASSWORD",),
        )
        second = build_snapshot(
            "run-042",
            "staging",
            {"APP_MODE": "staging", "DB_PASSWORD": "do-not-print", "LOG_LEVEL": "debug"},
            secret_keys=("DB_PASSWORD",),
        )

        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertEqual(first.to_json(), second.to_json())
        self.assertEqual(first.redacted_keys, ("DB_PASSWORD",))
        self.assertNotIn("do-not-print", first.to_json())
        self.assertEqual(first.redacted_values["DB_PASSWORD"], "<redacted>")

    def test_non_secret_change_changes_fingerprint(self) -> None:
        first = build_snapshot("run-042", "staging", {"LOG_LEVEL": "debug"})
        second = build_snapshot("run-042", "staging", {"LOG_LEVEL": "info"})

        self.assertNotEqual(first.fingerprint, second.fingerprint)

    def test_empty_identity_is_rejected(self) -> None:
        with self.assertRaisesRegex(SnapshotError, "run_id must not be empty"):
            build_snapshot(" ", "staging", {})
        with self.assertRaisesRegex(SnapshotError, "environment must not be empty"):
            build_snapshot("run-042", " ", {})

    def test_non_json_scalar_is_rejected(self) -> None:
        with self.assertRaisesRegex(SnapshotError, "must be a JSON scalar"):
            build_snapshot("run-042", "staging", {"NESTED": {"bad": True}})

    def test_secret_key_must_be_present_before_redaction(self) -> None:
        with self.assertRaisesRegex(SnapshotError, "secret key is missing"):
            build_snapshot("run-042", "staging", {"LOG_LEVEL": "debug"}, secret_keys=("TOKEN",))


if __name__ == "__main__":
    unittest.main()
