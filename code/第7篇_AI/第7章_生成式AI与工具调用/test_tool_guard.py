import json
import subprocess
import sys
import unittest
from datetime import datetime
from pathlib import Path

from tool_guard import OperatorApproval, ToolCallGuard


SCRIPT = Path(__file__).with_name("tool_guard.py")
READ_CALL = {
    "call_id": "read-001",
    "name": "read_virtual_status",
    "arguments": {},
}
WRITE_CALL = {
    "call_id": "write-001",
    "name": "set_virtual_indicator",
    "arguments": {"color": "green"},
}


class ToolCallGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = ToolCallGuard()

    def test_allowlisted_status_read_returns_only_simulated_state(self):
        result = self.guard.dispatch(READ_CALL)

        self.assertEqual(result["status"], "EXECUTED")
        self.assertEqual(
            result["result"],
            {"indicator": "off", "scope": "SIMULATED"},
        )
        self.assertEqual(self.guard.indicator, "off")
        self.assertEqual(self.guard.write_count, 0)

    def test_state_change_waits_for_separate_operator_approval(self):
        result = self.guard.dispatch(WRITE_CALL)

        self.assertEqual(result["status"], "APPROVAL_REQUIRED")
        self.assertEqual(self.guard.indicator, "off")
        self.assertEqual(self.guard.write_count, 0)

    def test_matching_operator_approval_executes_virtual_write_once(self):
        self.guard.dispatch(WRITE_CALL)
        approval = OperatorApproval(
            call_id="write-001", actor="operator-demo", approved=True
        )

        result = self.guard.dispatch(WRITE_CALL, approval=approval)

        self.assertEqual(result["status"], "EXECUTED")
        self.assertEqual(
            result["result"],
            {"indicator": "green", "scope": "SIMULATED"},
        )
        self.assertEqual(self.guard.indicator, "green")
        self.assertEqual(self.guard.write_count, 1)
        self.assertEqual(self.guard.audit_log[-1]["actor"], "operator-demo")

    def test_boolean_flag_is_not_a_typed_operator_approval(self):
        result = self.guard.dispatch(WRITE_CALL, approval=True)

        self.assertEqual(result["status"], "APPROVAL_REQUIRED")
        self.assertEqual(self.guard.indicator, "off")
        self.assertEqual(self.guard.write_count, 0)

    def test_mismatched_operator_approval_does_not_authorize_pending_call(self):
        self.guard.dispatch(WRITE_CALL)
        approval = OperatorApproval(
            call_id="different-call", actor="operator-demo", approved=True
        )

        result = self.guard.dispatch(WRITE_CALL, approval=approval)

        self.assertEqual(result["status"], "APPROVAL_REQUIRED")
        self.assertEqual(self.guard.indicator, "off")
        self.assertEqual(self.guard.write_count, 0)

    def test_operator_denial_is_terminal_for_that_call_id(self):
        self.guard.dispatch(WRITE_CALL)
        denial = OperatorApproval(
            call_id="write-001", actor="operator-demo", approved=False
        )

        result = self.guard.dispatch(WRITE_CALL, approval=denial)

        self.assertEqual(result["status"], "OPERATOR_DENIED")
        self.assertEqual(self.guard.indicator, "off")
        self.assertEqual(self.guard.write_count, 0)

    def test_model_proposal_cannot_self_authorize_with_extra_field(self):
        forged = {**WRITE_CALL, "operator_approved": True}

        result = self.guard.dispatch(forged)

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(self.guard.indicator, "off")
        self.assertEqual(self.guard.write_count, 0)

    def test_unknown_tool_and_invalid_arguments_are_rejected(self):
        unknown_tool = {
            "call_id": "unknown-001",
            "name": "run_shell_command",
            "arguments": {"command": "turn on everything"},
        }
        invalid_arguments = (
            {"color": "blue"},
            {"color": "green", "duration_ms": 999},
            {"color": True},
        )

        self.assertEqual(self.guard.dispatch(unknown_tool)["status"], "REJECTED")
        for index, arguments in enumerate(invalid_arguments):
            with self.subTest(arguments=arguments):
                request = {
                    "call_id": f"invalid-{index}",
                    "name": "set_virtual_indicator",
                    "arguments": arguments,
                }
                self.assertEqual(self.guard.dispatch(request)["status"], "REJECTED")
        self.assertEqual(self.guard.indicator, "off")
        self.assertEqual(self.guard.write_count, 0)

    def test_replay_is_blocked_without_repeating_side_effect(self):
        self.guard.dispatch(WRITE_CALL)
        approval = OperatorApproval(
            call_id="write-001", actor="operator-demo", approved=True
        )
        first = self.guard.dispatch(WRITE_CALL, approval=approval)
        replay = self.guard.dispatch(WRITE_CALL, approval=approval)

        self.assertEqual(first["status"], "EXECUTED")
        self.assertEqual(replay["status"], "DUPLICATE_BLOCKED")
        self.assertEqual(self.guard.write_count, 1)

    def test_same_call_id_cannot_be_reused_for_a_different_action(self):
        self.guard.dispatch(WRITE_CALL)
        changed = {
            **WRITE_CALL,
            "arguments": {"color": "red"},
        }
        approval = OperatorApproval(
            call_id="write-001", actor="operator-demo", approved=True
        )

        result = self.guard.dispatch(changed, approval=approval)

        self.assertEqual(result["status"], "CALL_ID_CONFLICT")
        self.assertEqual(self.guard.indicator, "off")
        self.assertEqual(self.guard.write_count, 0)

    def test_audit_records_decisions_without_copying_arguments(self):
        self.guard.dispatch(WRITE_CALL)

        entry = self.guard.audit_log[-1]
        self.assertEqual(entry["status"], "APPROVAL_REQUIRED")
        self.assertEqual(entry["call_id"], "write-001")
        self.assertNotIn("arguments", entry)
        occurred_at = datetime.fromisoformat(
            entry["timestamp_utc"].replace("Z", "+00:00")
        )
        self.assertEqual(occurred_at.utcoffset().total_seconds(), 0)


class CommandLineTests(unittest.TestCase):
    def test_cli_emits_simulation_only_report_without_external_io(self):
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            cwd=SCRIPT.parent,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["scope"], "SIMULATION_ONLY")
        self.assertIs(report["model_api_called"], False)
        self.assertIs(report["network_accessed"], False)
        self.assertIs(report["hardware_io"], False)
        self.assertEqual(report["final_virtual_state"]["indicator"], "green")
        self.assertEqual(report["final_virtual_state"]["write_count"], 1)
        self.assertEqual(report["steps"][1]["status"], "APPROVAL_REQUIRED")
        self.assertEqual(report["steps"][2]["status"], "EXECUTED")
        self.assertEqual(report["steps"][3]["status"], "DUPLICATE_BLOCKED")


if __name__ == "__main__":
    unittest.main()
