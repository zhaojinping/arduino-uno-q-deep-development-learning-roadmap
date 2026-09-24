import json
import subprocess
import sys
import unittest
from pathlib import Path

from readiness_gate import ManifestParseError, evaluate_manifest, parse_manifest_json


SCRIPT = Path(__file__).with_name("readiness_gate.py")


def complete_claim_manifest():
    return {
        "schema_version": 1,
        "report_id": "demo-ai-integration-001",
        "gates": {
            "task_definition": {"status": "CLAIMED_PASS", "reference": "EV-TASK-001"},
            "dataset_evaluation": {"status": "CLAIMED_PASS", "reference": "EV-DATA-001"},
            "model_artifact": {"status": "CLAIMED_PASS", "reference": "EV-MODEL-001"},
            "inference_regression": {"status": "CLAIMED_PASS", "reference": "EV-REGRESSION-001"},
            "performance_budget": {"status": "CLAIMED_PASS", "reference": "EV-PERFORMANCE-001"},
            "quantization_evaluation": {"status": "CLAIMED_PASS", "reference": "EV-QUANTIZATION-001"},
            "tool_call_safety": {"status": "CLAIMED_PASS", "reference": "EV-TOOLS-001"},
            "target_acceptance": {"status": "CLAIMED_PASS", "reference": "EV-TARGET-001"},
        },
    }


class ReadinessGateTests(unittest.TestCase):
    def setUp(self):
        self.manifest = complete_claim_manifest()

    def test_complete_claims_only_request_human_review(self):
        report = evaluate_manifest(self.manifest)

        self.assertEqual(report["decision"], "READY_FOR_HUMAN_REVIEW")
        self.assertEqual(report["scope"], "REPORT_ONLY")
        self.assertIs(report["deployment_authorized"], False)
        self.assertEqual(report["counts"]["claimed_pass"], 8)
        self.assertEqual(len(report["gates"]), 8)

    def test_unverified_target_keeps_report_incomplete(self):
        self.manifest["gates"]["target_acceptance"] = {
            "status": "NOT_RUN",
            "reference": None,
        }

        report = evaluate_manifest(self.manifest)

        self.assertEqual(report["decision"], "INCOMPLETE")
        self.assertEqual(report["counts"]["not_run"], 1)
        self.assertIs(report["deployment_authorized"], False)

    def test_any_blocked_gate_blocks_the_integrated_report(self):
        self.manifest["gates"]["tool_call_safety"] = {
            "status": "BLOCKED",
            "reference": "EV-TOOLS-FAIL-001",
        }

        report = evaluate_manifest(self.manifest)

        self.assertEqual(report["decision"], "BLOCKED")
        self.assertEqual(report["counts"]["blocked"], 1)
        self.assertIs(report["deployment_authorized"], False)

    def test_review_required_gate_is_not_counted_as_a_pass(self):
        self.manifest["gates"]["quantization_evaluation"] = {
            "status": "REVIEW_REQUIRED",
            "reference": "EV-QUANTIZATION-REVIEW-001",
        }

        report = evaluate_manifest(self.manifest)

        self.assertEqual(report["decision"], "INCOMPLETE")
        self.assertEqual(report["counts"]["review_required"], 1)
        self.assertEqual(report["counts"]["claimed_pass"], 7)

    def test_missing_required_gate_rejects_manifest(self):
        del self.manifest["gates"]["model_artifact"]

        report = evaluate_manifest(self.manifest)

        self.assertEqual(report["decision"], "INVALID_MANIFEST")
        self.assertEqual(report["reason"], "GATE_SET_MISMATCH")

    def test_unknown_gate_rejects_manifest(self):
        self.manifest["gates"]["deployment_override"] = {
            "status": "CLAIMED_PASS",
            "reference": "EV-OVERRIDE-001",
        }

        report = evaluate_manifest(self.manifest)

        self.assertEqual(report["decision"], "INVALID_MANIFEST")
        self.assertEqual(report["reason"], "GATE_SET_MISMATCH")

    def test_unknown_gate_status_rejects_manifest(self):
        self.manifest["gates"]["tool_call_safety"]["status"] = "APPROVED"

        report = evaluate_manifest(self.manifest)

        self.assertEqual(report["decision"], "INVALID_MANIFEST")
        self.assertEqual(report["reason"], "INVALID_GATE_STATUS")

    def test_claimed_pass_requires_a_bounded_evidence_reference(self):
        self.manifest["gates"]["task_definition"]["reference"] = ""

        report = evaluate_manifest(self.manifest)

        self.assertEqual(report["decision"], "INVALID_MANIFEST")
        self.assertEqual(report["reason"], "INVALID_EVIDENCE_REFERENCE")

    def test_not_run_gate_cannot_claim_an_evidence_reference(self):
        self.manifest["gates"]["target_acceptance"] = {
            "status": "NOT_RUN",
            "reference": "EV-TARGET-001",
        }

        report = evaluate_manifest(self.manifest)

        self.assertEqual(report["decision"], "INVALID_MANIFEST")
        self.assertEqual(report["reason"], "INVALID_EVIDENCE_REFERENCE")

    def test_non_object_manifest_is_rejected(self):
        report = evaluate_manifest(["not", "a", "manifest"])

        self.assertEqual(report["decision"], "INVALID_MANIFEST")
        self.assertEqual(report["reason"], "ROOT_NOT_OBJECT")

    def test_json_parser_rejects_duplicate_keys(self):
        with self.assertRaises(ManifestParseError) as raised:
            parse_manifest_json(b'{"schema_version":1,"schema_version":1}')

        self.assertEqual(raised.exception.code, "DUPLICATE_JSON_KEY")

    def test_json_parser_rejects_payload_over_16_kib(self):
        with self.assertRaises(ManifestParseError) as raised:
            parse_manifest_json(b" " * 16385)

        self.assertEqual(raised.exception.code, "MANIFEST_TOO_LARGE")

    def test_json_parser_rejects_malformed_json_and_invalid_utf8(self):
        cases = (
            (b'{"schema_version":', "INVALID_JSON"),
            (b"\xff", "INVALID_UTF8"),
        )
        for payload, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaises(ManifestParseError) as raised:
                    parse_manifest_json(payload)
                self.assertEqual(raised.exception.code, reason)


class CommandLineTests(unittest.TestCase):
    def test_cli_emits_fixed_sample_report_without_authorizing_deployment(self):
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            cwd=SCRIPT.parent,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["report_id"], "demo-ai-integration-001")
        self.assertEqual(report["decision"], "INCOMPLETE")
        self.assertEqual(report["scope"], "REPORT_ONLY")
        self.assertIs(report["deployment_authorized"], False)
        self.assertEqual(report["counts"]["claimed_pass"], 7)
        self.assertEqual(report["counts"]["not_run"], 1)


if __name__ == "__main__":
    unittest.main()
