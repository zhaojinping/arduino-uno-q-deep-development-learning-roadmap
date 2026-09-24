"""Behavior tests for the offline IoT remote-command teaching model."""

from __future__ import annotations

import unittest
import json
import subprocess
import sys
from pathlib import Path

import remote_command_gate

try:
    CommandGate = remote_command_gate.CommandGate
except ModuleNotFoundError:
    CommandGate = None  # type: ignore[assignment,misc]


EXPECTED_DEVICE = "uno-q-demo-01"
POLICY = {
    "maintenance-demo": {"read_status", "set_sampling_period"},
    "observer-demo": {"read_status"},
}


def make_command(**overrides: object) -> dict[str, object]:
    command: dict[str, object] = {
        "schema_version": 1,
        "command_id": "cmd-demo-001",
        "correlation_id": "corr-demo-001",
        "device_id": EXPECTED_DEVICE,
        "operation": "set_sampling_period",
        "parameters": {"seconds": 20},
        "issued_at_unix": 1_000,
        "expires_at_unix": 1_300,
    }
    command.update(overrides)
    return command


class CommandGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertIsNotNone(
            CommandGate,
            "missing feature: the offline remote-command gate has not been implemented",
        )
        assert CommandGate is not None
        self.gate = CommandGate(
            expected_device_id=EXPECTED_DEVICE,
            principal_operations=POLICY,
        )

    def test_valid_command_is_accepted_without_applying_configuration(self) -> None:
        result = self.gate.submit(
            make_command(), principal="maintenance-demo", now=1_100
        )

        self.assertEqual(result["status"], "ACCEPTED")
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 10)

    def test_accepted_command_changes_configuration_only_in_apply_phase(self) -> None:
        self.gate.submit(make_command(), principal="maintenance-demo", now=1_100)
        execute = getattr(self.gate, "execute", None)
        self.assertTrue(
            callable(execute), "missing feature: accepted command has no apply phase"
        )

        result = execute("cmd-demo-001", now=1_101)

        self.assertEqual(result["status"], "APPLIED")
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 20)

    def test_command_for_another_device_is_rejected(self) -> None:
        result = self.gate.submit(
            make_command(device_id="uno-q-other-99"),
            principal="maintenance-demo",
            now=1_100,
        )

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "TARGET_MISMATCH")

    def test_read_only_principal_cannot_change_device_configuration(self) -> None:
        result = self.gate.submit(
            make_command(), principal="observer-demo", now=1_100
        )

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "OPERATION_NOT_AUTHORIZED")
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 10)

    def test_principal_context_must_be_a_string(self) -> None:
        try:
            result = self.gate.submit(
                make_command(),
                principal=["maintenance-demo"],  # type: ignore[arg-type]
                now=1_100,
            )
        except TypeError as error:
            self.fail(f"invalid principal context escaped validation: {error}")

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "INVALID_PRINCIPAL_CONTEXT")

    def test_expired_command_is_not_accepted(self) -> None:
        result = self.gate.submit(
            make_command(), principal="maintenance-demo", now=1_300
        )

        self.assertEqual(result["status"], "EXPIRED")
        self.assertEqual(result["reason"], "COMMAND_EXPIRED")

    def test_future_issued_command_is_rejected(self) -> None:
        result = self.gate.submit(
            make_command(issued_at_unix=1_101),
            principal="maintenance-demo",
            now=1_100,
        )

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "COMMAND_NOT_YET_VALID")

    def test_command_validity_window_cannot_exceed_policy_limit(self) -> None:
        result = self.gate.submit(
            make_command(expires_at_unix=1_301),
            principal="maintenance-demo",
            now=1_100,
        )

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "COMMAND_LIFETIME_TOO_LONG")

    def test_negative_unix_times_are_rejected(self) -> None:
        cases = (
            (make_command(issued_at_unix=-1, expires_at_unix=100), 0),
            (make_command(issued_at_unix=0, expires_at_unix=100), -1),
        )
        for command, now in cases:
            with self.subTest(command=command, now=now):
                result = self.gate.submit(
                    command, principal="maintenance-demo", now=now
                )

                self.assertEqual(result["status"], "REJECTED")
                self.assertEqual(result["reason"], "INVALID_TIME")

    def test_command_expiring_while_queued_is_not_applied(self) -> None:
        self.gate.submit(make_command(), principal="maintenance-demo", now=1_100)

        result = self.gate.execute("cmd-demo-001", now=1_300)

        self.assertEqual(result["status"], "EXPIRED")
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 10)

    def test_expired_replay_converges_ledger_and_keeps_command_id_reserved(self) -> None:
        command = make_command()
        self.gate.submit(command, principal="maintenance-demo", now=1_100)

        replay = self.gate.submit(
            command, principal="maintenance-demo", now=1_300
        )

        self.assertEqual(replay["status"], "DUPLICATE_RETURNED")
        self.assertEqual(replay["stored_status"], "EXPIRED")
        self.assertEqual(self.gate.query("cmd-demo-001")["status"], "EXPIRED")

        altered = make_command(parameters={"seconds": 30})
        conflict = self.gate.submit(
            altered, principal="maintenance-demo", now=1_300
        )
        self.assertEqual(conflict["status"], "ID_CONFLICT")
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 10)

    def test_invalid_execution_time_cannot_apply_accepted_command(self) -> None:
        self.gate.submit(make_command(), principal="maintenance-demo", now=1_100)

        result = self.gate.execute("cmd-demo-001", now=-1)

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "INVALID_TIME")
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 10)

    def test_clock_before_command_issue_time_cannot_apply_command(self) -> None:
        self.gate.submit(make_command(), principal="maintenance-demo", now=1_100)

        result = self.gate.execute("cmd-demo-001", now=999)

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "COMMAND_NOT_YET_VALID")
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 10)

    def test_replaying_applied_command_returns_ledger_result(self) -> None:
        command = make_command()
        self.gate.submit(command, principal="maintenance-demo", now=1_100)
        self.gate.execute("cmd-demo-001", now=1_101)

        replay = self.gate.submit(
            command, principal="maintenance-demo", now=1_102
        )

        self.assertEqual(replay["status"], "DUPLICATE_RETURNED")
        self.assertEqual(replay["stored_status"], "APPLIED")
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 20)

    def test_same_command_id_with_changed_payload_is_a_conflict(self) -> None:
        command = make_command()
        self.gate.submit(command, principal="maintenance-demo", now=1_100)
        self.gate.execute("cmd-demo-001", now=1_101)
        altered = make_command(parameters={"seconds": 30})

        result = self.gate.submit(
            altered, principal="maintenance-demo", now=1_102
        )

        self.assertEqual(result["status"], "ID_CONFLICT")
        self.assertEqual(result["reason"], "COMMAND_ID_REUSED_WITH_DIFFERENT_CONTENT")
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 20)

    def test_missing_result_is_unknown_and_does_not_authorize_a_retry(self) -> None:
        query = getattr(self.gate, "query", None)
        self.assertTrue(
            callable(query), "missing feature: command result cannot be reconciled"
        )

        result = query("cmd-not-observed-009")

        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["reason"], "RESULT_NOT_IN_LOCAL_LEDGER")
        self.assertEqual(result["next_step"], "RECONCILE_BEFORE_ANY_RETRY")

    def test_execute_unknown_command_returns_unknown_instead_of_raising(self) -> None:
        try:
            result = self.gate.execute("cmd-not-observed-009", now=1_100)
        except KeyError as error:
            self.fail(f"missing unknown-command result behavior: {error}")

        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["reason"], "RESULT_NOT_IN_LOCAL_LEDGER")

    def test_command_with_unrecognized_field_is_rejected(self) -> None:
        command = make_command(shell="restart-all")

        result = self.gate.submit(
            command, principal="maintenance-demo", now=1_100
        )

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "INVALID_COMMAND_SCHEMA")

    def test_schema_version_and_identifiers_are_strictly_bounded(self) -> None:
        cases = (
            ({"schema_version": True}, "cmd-schema-1"),
            ({"command_id": ""}, "cmd-schema-2"),
            ({"correlation_id": "c" * 65}, "cmd-schema-3"),
        )
        for overrides, unique_id in cases:
            with self.subTest(overrides=overrides):
                command = make_command(command_id=unique_id)
                command.update(overrides)
                result = self.gate.submit(
                    command,
                    principal="maintenance-demo",
                    now=1_100,
                )

                self.assertEqual(result["status"], "REJECTED")
                self.assertEqual(result["reason"], "INVALID_COMMAND_SCHEMA")

    def test_operation_outside_fixed_allowlist_is_rejected(self) -> None:
        command = make_command(
            operation="execute_shell", parameters={"command": "restart-all"}
        )

        result = self.gate.submit(
            command, principal="maintenance-demo", now=1_100
        )

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "UNSUPPORTED_OPERATION")

    def test_sampling_period_rejects_out_of_range_and_boolean_values(self) -> None:
        for invalid_seconds in (0, 61, True, "20"):
            with self.subTest(seconds=invalid_seconds):
                result = self.gate.submit(
                    make_command(parameters={"seconds": invalid_seconds}),
                    principal="maintenance-demo",
                    now=1_100,
                )

                self.assertEqual(result["status"], "REJECTED")
                self.assertEqual(result["reason"], "INVALID_PARAMETERS")

    def test_read_only_principal_can_observe_status_without_mutation(self) -> None:
        command = make_command(
            command_id="cmd-read-001",
            correlation_id="corr-read-001",
            operation="read_status",
            parameters={},
        )
        self.gate.submit(command, principal="observer-demo", now=1_100)

        try:
            result = self.gate.execute("cmd-read-001", now=1_101)
        except (KeyError, TypeError) as error:
            self.fail(f"missing read-only operation behavior: {error}")

        self.assertEqual(result["status"], "OBSERVED")
        self.assertEqual(result["result"]["sampling_period_seconds"], 10)
        self.assertEqual(self.gate.snapshot()["sampling_period_seconds"], 10)

    def test_completed_command_cannot_be_applied_again(self) -> None:
        self.gate.submit(make_command(), principal="maintenance-demo", now=1_100)
        self.gate.execute("cmd-demo-001", now=1_101)

        repeated = self.gate.execute("cmd-demo-001", now=1_102)

        self.assertEqual(repeated["status"], "DUPLICATE_RETURNED")
        self.assertEqual(repeated["stored_status"], "APPLIED")

    def test_mutating_caller_payload_after_submit_cannot_change_accepted_command(self) -> None:
        command = make_command()
        self.gate.submit(command, principal="maintenance-demo", now=1_100)
        command["parameters"]["seconds"] = 59  # type: ignore[index]

        result = self.gate.execute("cmd-demo-001", now=1_101)

        self.assertEqual(result["status"], "APPLIED")
        self.assertEqual(result["result"]["sampling_period_seconds"], 20)

    def test_mutating_returned_result_cannot_change_internal_ledger(self) -> None:
        command = make_command(
            command_id="cmd-read-002",
            correlation_id="corr-read-002",
            operation="read_status",
            parameters={},
        )
        self.gate.submit(command, principal="observer-demo", now=1_100)
        result = self.gate.execute("cmd-read-002", now=1_101)
        result["result"]["sampling_period_seconds"] = 99

        stored = self.gate.query("cmd-read-002")

        self.assertEqual(stored["status"], "OBSERVED")
        self.assertEqual(stored["result"]["sampling_period_seconds"], 10)

    def test_json_parser_rejects_duplicate_members(self) -> None:
        parse_command = getattr(remote_command_gate, "parse_command", None)
        self.assertTrue(
            callable(parse_command), "missing feature: bounded command JSON parser"
        )
        raw = b'{"schema_version":1,"schema_version":1}'

        with self.assertRaises(ValueError):
            parse_command(raw)

    def test_json_parser_rejects_payload_over_byte_limit(self) -> None:
        parse_command = getattr(remote_command_gate, "parse_command", None)
        self.assertTrue(callable(parse_command))
        raw = b" " * (remote_command_gate.MAX_COMMAND_BYTES + 1) + b"{}"

        with self.assertRaises(ValueError):
            parse_command(raw)

    def test_json_parser_rejects_non_finite_numbers(self) -> None:
        parse_command = getattr(remote_command_gate, "parse_command", None)
        self.assertTrue(callable(parse_command))

        with self.assertRaises(ValueError):
            parse_command(b'{"value":NaN}')

    def test_command_ledger_stops_accepting_before_memory_grows_without_bound(self) -> None:
        for index in range(64):
            result = self.gate.submit(
                make_command(command_id=f"cmd-cap-{index:02d}"),
                principal="maintenance-demo",
                now=1_100,
            )
            self.assertEqual(result["status"], "ACCEPTED")

        overflow = self.gate.submit(
            make_command(command_id="cmd-cap-overflow"),
            principal="maintenance-demo",
            now=1_100,
        )

        self.assertEqual(overflow["status"], "LEDGER_FULL")
        self.assertEqual(overflow["reason"], "COMMAND_LEDGER_CAPACITY_REACHED")

    def test_cli_demo_shows_acceptance_application_replay_and_unknown_states(self) -> None:
        script = Path(remote_command_gate.__file__).resolve()
        completed = subprocess.run(
            [sys.executable, "-B", str(script)],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        events = [json.loads(line) for line in completed.stdout.splitlines()]

        self.assertEqual(
            [event["status"] for event in events],
            [
                "ACCEPTED",
                "APPLIED",
                "DUPLICATE_RETURNED",
                "ID_CONFLICT",
                "ACCEPTED",
                "OBSERVED",
                "ACCEPTED",
                "EXPIRED",
                "EXPIRED",
                "UNKNOWN",
            ],
        )
        self.assertTrue(
            all(event["scope"] == "OFFLINE_IOT_REMOTE_COMMAND_SIMULATION" for event in events)
        )


if __name__ == "__main__":
    unittest.main()
