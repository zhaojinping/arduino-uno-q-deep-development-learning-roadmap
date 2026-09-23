"""Behavior tests for the offline inference-regression teaching tool."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compare_inference import compare_payload


def record(sample_id, scores, preprocess_id="prep-v1", labels=None):
    return {
        "sample_id": sample_id,
        "preprocess_id": preprocess_id,
        "labels": labels or ["normal", "fault"],
        "scores": scores,
    }


def payload(reference, candidate, atol=0.01, rtol=0.02, min_margin=0.0):
    return {
        "schema_version": 1,
        "atol": atol,
        "rtol": rtol,
        "min_margin": min_margin,
        "reference": reference,
        "candidate": candidate,
    }


class CompareInferenceTests(unittest.TestCase):
    def test_pairs_by_sample_id_when_candidate_records_are_reordered(self):
        result = compare_payload(payload(
            [record("a", [0.9, 0.1]), record("b", [0.2, 0.8])],
            [record("b", [0.2, 0.8]), record("a", [0.9, 0.1])],
        ))

        self.assertEqual(result["decision"], "MATCH_WITHIN_TOLERANCE")
        self.assertEqual(result["summary"]["sample_count"], 2)

    def test_applies_absolute_and_relative_tolerance_per_value(self):
        result = compare_payload(payload(
            [record("near-zero", [0.9, 0.1])],
            [record("near-zero", [0.9, 0.108])],
            atol=0.001,
            rtol=0.05,
        ))

        self.assertEqual(result["summary"]["values_over_tolerance"], 1)
        self.assertEqual(result["decision"], "REVIEW_REQUIRED")

    def test_keeps_small_numerical_drift_within_declared_tolerance(self):
        result = compare_payload(payload(
            [record("stable", [0.8, 0.2])],
            [record("stable", [0.805, 0.195])],
        ))

        self.assertEqual(result["summary"]["max_absolute_error"], 0.005)
        self.assertEqual(result["summary"]["values_over_tolerance"], 0)
        self.assertEqual(result["decision"], "MATCH_WITHIN_TOLERANCE")

    def test_reviews_argmax_change_even_when_values_are_within_tolerance(self):
        result = compare_payload(payload(
            [record("boundary", [0.51, 0.49])],
            [record("boundary", [0.49, 0.51])],
            atol=0.03,
            rtol=0.0,
        ))

        self.assertEqual(result["summary"]["values_over_tolerance"], 0)
        self.assertEqual(result["summary"]["argmax_changed_samples"], 1)
        self.assertEqual(result["decision"], "REVIEW_REQUIRED")

    def test_reviews_a_sample_that_crosses_the_margin_abstention_gate(self):
        result = compare_payload(payload(
            [record("gate", [0.55, 0.45])],
            [record("gate", [0.61, 0.39])],
            atol=0.1,
            rtol=0.0,
            min_margin=0.15,
        ))

        self.assertEqual(result["summary"]["argmax_changed_samples"], 0)
        self.assertEqual(result["summary"]["decision_changed_samples"], 1)
        self.assertEqual(result["summary"]["reference_abstentions"], 1)
        self.assertEqual(result["decision"], "REVIEW_REQUIRED")

    def test_abstains_on_an_exact_tie_even_when_minimum_margin_is_zero(self):
        result = compare_payload(payload(
            [record("tie", [0.5, 0.5])],
            [record("tie", [0.5, 0.5])],
            min_margin=0.0,
        ))

        self.assertIsNone(result["samples"][0]["reference_decision"])
        self.assertEqual(result["summary"]["reference_abstentions"], 1)

    def test_rejects_missing_or_extra_sample_ids(self):
        with self.assertRaisesRegex(ValueError, "sample_id sets differ"):
            compare_payload(payload(
                [record("reference-only", [0.9, 0.1])],
                [record("candidate-only", [0.9, 0.1])],
            ))

    def test_rejects_different_preprocessing_contracts_for_a_pair(self):
        with self.assertRaisesRegex(ValueError, "preprocess_id differs"):
            compare_payload(payload(
                [record("same-input", [0.9, 0.1], "rgb-0-1-v1")],
                [record("same-input", [0.9, 0.1], "bgr-0-255-v1")],
            ))

    def test_rejects_class_order_mismatch_instead_of_comparing_wrong_outputs(self):
        with self.assertRaisesRegex(ValueError, "labels differ"):
            compare_payload(payload(
                [record("same-input", [0.9, 0.1], labels=["normal", "fault"])],
                [record("same-input", [0.1, 0.9], labels=["fault", "normal"])],
            ))

    def test_rejects_non_finite_scores_and_boolean_scores(self):
        invalid_records = ([float("nan"), 0.0], [True, 0.0])
        for scores in invalid_records:
            with self.subTest(scores=scores):
                with self.assertRaisesRegex(ValueError, "invalid score"):
                    compare_payload(payload(
                        [record("bad", [0.9, 0.1])],
                        [record("bad", scores)],
                    ))

    def test_rejects_integer_scores_that_cannot_be_represented_as_floats(self):
        with self.assertRaisesRegex(ValueError, "invalid score"):
            compare_payload(payload(
                [record("huge", [0.9, 0.1])],
                [record("huge", [10 ** 1000, 0])],
            ))

    def test_rejects_tolerances_that_cannot_be_represented_as_floats(self):
        with self.assertRaisesRegex(ValueError, "invalid atol"):
            compare_payload(payload(
                [record("huge", [0.9, 0.1])],
                [record("huge", [0.9, 0.1])],
                atol=10 ** 1000,
            ))

    def test_rejects_tolerance_arithmetic_that_overflows(self):
        with self.assertRaisesRegex(ValueError, "non-finite tolerance"):
            compare_payload(payload(
                [record("overflow", [1e308, 0.0])],
                [record("overflow", [1e308, 0.0])],
                atol=0.0,
                rtol=1e308,
            ))

    def test_rejects_non_finite_derived_differences_and_margins(self):
        cases = [
            (
                [record("overflow", [1e308, 0.0])],
                [record("overflow", [-1e308, 0.0])],
                "non-finite score difference",
            ),
            (
                [record("overflow", [1e308, -1e308])],
                [record("overflow", [1e308, -1e308])],
                "non-finite score margin",
            ),
        ]
        for reference, candidate, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    compare_payload(payload(reference, candidate))

    def test_rejects_duplicate_sample_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicate sample_id"):
            compare_payload(payload(
                [record("duplicate", [0.9, 0.1]), record("duplicate", [0.8, 0.2])],
                [record("duplicate", [0.9, 0.1])],
            ))

    def test_requires_schema_version_to_be_an_integer(self):
        for version in (True, 1.0):
            with self.subTest(version=version):
                data = payload(
                    [record("version", [0.9, 0.1])],
                    [record("version", [0.9, 0.1])],
                )
                data["schema_version"] = version
                with self.assertRaisesRegex(ValueError, "unsupported schema_version"):
                    compare_payload(data)

    def test_cli_returns_report_only_review_without_treating_it_as_process_failure(self):
        script = Path(__file__).with_name("compare_inference.py")
        case_data = payload(
            [record("boundary", [0.51, 0.49])],
            [record("boundary", [0.49, 0.51])],
            atol=0.03,
            rtol=0.0,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "comparison.json"
            input_path.write_text(json.dumps(case_data), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(script), "--input", str(input_path)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["decision"], "REVIEW_REQUIRED")
        self.assertTrue(report["report_only"])


if __name__ == "__main__":
    unittest.main()
