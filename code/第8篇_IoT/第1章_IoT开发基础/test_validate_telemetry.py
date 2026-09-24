"""Behavior tests for the offline telemetry payload contract."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from validate_telemetry import MAX_PAYLOAD_BYTES, validate_payload


VALID_PAYLOAD = (
    b'{"schema_version":1,"device_id":"sensor-01",'
    b'"boot_id":"boot-a7","sequence":42,'
    b'"event_time":"2026-09-24T10:30:00+08:00",'
    b'"metric":"temperature","value":23.75,'
    b'"unit":"degC","quality":"GOOD"}'
)


class ValidateTelemetryTests(unittest.TestCase):
    def test_accepts_a_well_formed_synthetic_reading(self) -> None:
        self.assertEqual(
            validate_payload(VALID_PAYLOAD),
            {
                "schema_version": 1,
                "scope": "OFFLINE_SCHEMA_ONLY",
                "result": "VALID",
                "reason": None,
                "event_key": "sensor-01/boot-a7/42",
            },
        )

    def test_rejects_text_instead_of_raw_bytes(self) -> None:
        self.assertEqual(validate_payload("{}")["reason"], "INPUT_NOT_BYTES")

    def test_rejects_a_payload_over_the_size_limit(self) -> None:
        self.assertEqual(
            validate_payload(b" " * (MAX_PAYLOAD_BYTES + 1))["reason"],
            "PAYLOAD_TOO_LARGE",
        )

    def test_rejects_invalid_utf8(self) -> None:
        self.assertEqual(validate_payload(b"\xff")["reason"], "INVALID_UTF8")

    def test_rejects_malformed_json_and_nonstandard_constants(self) -> None:
        for raw in (
            b"{",
            b"{\"value\":NaN}",
            b"{\"value\":Infinity}",
            b"{\"value\":-Infinity}",
        ):
            with self.subTest(raw=raw):
                self.assertEqual(validate_payload(raw)["reason"], "INVALID_JSON")

    def test_rejects_duplicate_json_member_names(self) -> None:
        raw = VALID_PAYLOAD.replace(b'"sequence":42', b'"sequence":1,"sequence":42')
        self.assertEqual(validate_payload(raw)["reason"], "DUPLICATE_JSON_KEY")

    def test_requires_a_json_object(self) -> None:
        self.assertEqual(validate_payload(b"[]")["reason"], "INVALID_ROOT")

    def test_rejects_missing_or_unknown_top_level_fields(self) -> None:
        value = json.loads(VALID_PAYLOAD)
        missing = dict(value)
        del missing["quality"]
        unknown = {**value, "extra": "not in schema v1"}
        for candidate in (missing, unknown):
            with self.subTest(candidate=candidate):
                raw = json.dumps(candidate, separators=(",", ":")).encode("utf-8")
                self.assertEqual(validate_payload(raw)["reason"], "FIELDS_MISMATCH")

    def test_rejects_boolean_schema_version(self) -> None:
        value = json.loads(VALID_PAYLOAD)
        value["schema_version"] = True
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        self.assertEqual(
            validate_payload(raw)["reason"], "UNSUPPORTED_SCHEMA_VERSION"
        )

    def test_rejects_invalid_device_and_boot_identifiers(self) -> None:
        for field, bad_value in (("device_id", ""), ("boot_id", "boot/id")):
            value = json.loads(VALID_PAYLOAD)
            value[field] = bad_value
            raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
            with self.subTest(field=field):
                self.assertEqual(validate_payload(raw)["reason"], "INVALID_IDENTITY")

    def test_requires_a_nonnegative_integer_sequence_not_a_boolean(self) -> None:
        for bad_sequence in (-1, True, 2.5):
            value = json.loads(VALID_PAYLOAD)
            value["sequence"] = bad_sequence
            raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
            with self.subTest(sequence=bad_sequence):
                self.assertEqual(validate_payload(raw)["reason"], "INVALID_SEQUENCE")

    def test_requires_an_rfc3339_timestamp_with_a_known_offset(self) -> None:
        for event_time in (
            "2026-09-24T10:30:00",
            "2026-02-30T10:30:00Z",
            "2026-09-24T10:30:00-00:00",
            "2026-09-24T10:30:60Z",
        ):
            value = json.loads(VALID_PAYLOAD)
            value["event_time"] = event_time
            raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
            with self.subTest(event_time=event_time):
                self.assertEqual(validate_payload(raw)["reason"], "INVALID_EVENT_TIME")

    def test_accepts_utc_z_timestamp(self) -> None:
        value = json.loads(VALID_PAYLOAD)
        value["event_time"] = "2026-09-24T02:30:00Z"
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        self.assertEqual(validate_payload(raw)["result"], "VALID")

    def test_rejects_boolean_and_non_finite_reading_values(self) -> None:
        for raw in (
            VALID_PAYLOAD.replace(b'"value":23.75', b'"value":true'),
            VALID_PAYLOAD.replace(b'"value":23.75', b'"value":1e9999'),
        ):
            with self.subTest(raw=raw):
                self.assertEqual(validate_payload(raw)["reason"], "INVALID_VALUE")

    def test_rejects_invalid_metric_name_unit_or_quality(self) -> None:
        for field, bad_value in (
            ("metric", "Temperature C"),
            ("unit", ""),
            ("quality", "EXCELLENT"),
        ):
            value = json.loads(VALID_PAYLOAD)
            value[field] = bad_value
            raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
            with self.subTest(field=field):
                self.assertEqual(validate_payload(raw)["reason"], "INVALID_READING")

    def test_sample_command_emits_a_schema_only_report(self) -> None:
        script = Path(__file__).with_name("validate_telemetry.py")
        completed = subprocess.run(
            [sys.executable, "-B", str(script)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["result"], "VALID")
        self.assertEqual(report["scope"], "OFFLINE_SCHEMA_ONLY")
        self.assertIsNone(report["reason"])


if __name__ == "__main__":
    unittest.main()
