"""Behavioral checks for the offline, hand-set teaching model."""

import importlib.util
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("teaching_inference.py")


def load_module():
    assert SCRIPT.is_file(), "teaching_inference.py must exist"
    spec = importlib.util.spec_from_file_location("teaching_inference", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample(**changes):
    record = {
        "source": "synthetic",
        "run_id": "ai-demo-001",
        "sample_id": "s1",
        "feature_schema": "vision-features-v1",
        "timestamp_ms": 100,
        "observed_at_ms": 120,
        "features": {"color_fraction": 0.8, "shape_score": 0.8},
    }
    record.update(changes)
    return record


class TeachingInferenceTests(unittest.TestCase):
    def test_clear_candidate_reports_only_a_raw_margin_not_a_probability(self):
        result = load_module().evaluate(sample())
        self.assertEqual(result["decision"], "REPORT_ONLY")
        self.assertEqual(result["label"], "candidate_like")
        self.assertAlmostEqual(result["margin"], 0.9)
        self.assertTrue(result["evaluated"])
        self.assertEqual(result["model_id"], "hand-set-linear-v1")
        self.assertEqual(result.get("source"), "synthetic")
        self.assertEqual(result.get("run_id"), "ai-demo-001")
        self.assertEqual(result.get("sample_id"), "s1")
        self.assertEqual(result.get("feature_schema"), "vision-features-v1")
        self.assertEqual(result.get("timestamp_ms"), 100)
        self.assertEqual(result.get("observed_at_ms"), 120)
        self.assertEqual(result["reason"], "teaching_weights_unvalidated")
        self.assertNotIn("probability", result)
        self.assertNotIn("action", result)

    def test_negative_margin_reports_other_label_without_actuation(self):
        result = load_module().evaluate(sample(features={"color_fraction": 0.1, "shape_score": 0.1}))
        self.assertEqual(result["decision"], "REPORT_ONLY")
        self.assertEqual(result["label"], "other")
        self.assertAlmostEqual(result["margin"], -1.2)
        self.assertTrue(result["evaluated"])

    def test_small_absolute_margin_abstains_without_a_label(self):
        result = load_module().evaluate(sample(features={"color_fraction": 0.5, "shape_score": 0.5}))
        self.assertEqual(result["decision"], "ABSTAIN")
        self.assertIsNone(result["label"])
        self.assertEqual(result["reason"], "insufficient_margin")
        self.assertEqual(result["margin"], 0.0)
        self.assertTrue(result["evaluated"])

    def test_other_source_or_run_is_rejected_before_scoring(self):
        for changes in ({"source": "camera-0"}, {"run_id": "old-run"}):
            with self.subTest(changes=changes):
                result = load_module().evaluate(sample(**changes))
                self.assertEqual(result["decision"], "REJECTED")
                self.assertEqual(result["reason"], "source_or_session_mismatch")
                self.assertFalse(result["evaluated"])
                self.assertIsNone(result["label"])
                self.assertIsNone(result["margin"])

    def test_feature_schema_mismatch_rejects_before_scoring(self):
        result = load_module().evaluate(sample(feature_schema="vision-features-v2"))
        self.assertEqual(result["decision"], "REJECTED")
        self.assertEqual(result["reason"], "feature_schema_mismatch")
        self.assertFalse(result["evaluated"])
        self.assertIsNone(result["margin"])

    def test_stale_or_future_sample_is_rejected_before_scoring(self):
        for now_ms in (201, 99):
            with self.subTest(now_ms=now_ms):
                result = load_module().evaluate(sample(observed_at_ms=now_ms))
                self.assertEqual(result["decision"], "REJECTED")
                self.assertEqual(result["reason"], "stale_or_future_sample")
                self.assertFalse(result["evaluated"])
                self.assertIsNone(result["margin"])

    def test_out_of_contract_features_are_rejected_before_scoring(self):
        invalid = (
            {"color_fraction": 1.2, "shape_score": 0.8},
            {"color_fraction": True, "shape_score": 0.8},
            {"color_fraction": math.nan, "shape_score": 0.8},
            {"color_fraction": 0.8, "shape_score": 0.8, "extra": 1},
            {"color_fraction": 10 ** 400, "shape_score": 0.8},
        )
        for index, features in enumerate(invalid):
            with self.subTest(index=index):
                try:
                    result = load_module().evaluate(sample(features=features))
                except OverflowError as exc:
                    self.fail(f"numeric overflow raised instead of rejecting: {exc}")
                self.assertEqual(result["decision"], "REJECTED")
                self.assertEqual(result["reason"], "invalid_features")
                self.assertFalse(result["evaluated"])
                self.assertIsNone(result["margin"])

    def test_malformed_metadata_rejects_without_throwing_or_scoring(self):
        invalid = (
            None,
            {},
            sample(timestamp_ms=True),
            sample(observed_at_ms="120"),
            sample(sample_id=""),
            sample(source=7),
        )
        for record in invalid:
            with self.subTest(record=record):
                try:
                    result = load_module().evaluate(record)
                except (TypeError, KeyError, ValueError) as exc:
                    self.fail(f"malformed input raised instead of rejecting: {exc}")
                self.assertEqual(result["decision"], "REJECTED")
                self.assertEqual(result["reason"], "malformed_sample")
                self.assertFalse(result["evaluated"])
                self.assertIsNone(result["margin"])

    def test_cli_emits_six_deterministic_strict_json_records(self):
        first = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False)
        second = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        rows = [json.loads(line) for line in first.stdout.splitlines()]
        self.assertEqual([row["case"] for row in rows], [
            "clear_candidate", "clear_other", "borderline", "stale", "wrong_run", "invalid_feature"
        ])
        self.assertEqual([row["decision"] for row in rows], [
            "REPORT_ONLY", "REPORT_ONLY", "ABSTAIN", "REJECTED", "REJECTED", "REJECTED"
        ])
        self.assertTrue(all(row["margin"] is None for row in rows if row["decision"] == "REJECTED"))


if __name__ == "__main__":
    unittest.main()
