"""Behavior tests for the synthetic, offline dataset evaluation chapter."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from dataset_evaluation import (
    audit_samples, fit_centroids, score, classify, evaluate_rows, select_threshold,
    load_csv, run_experiment,
)


def sample_rows():
    rows = []
    cases = (
        ("train-A", "train", "candidate_like", 0.9, 0.9),
        ("train-A", "train", "other", 0.1, 0.2),
        ("val-C", "validation", "candidate_like", 0.8, 0.7),
        ("val-C", "validation", "other", 0.3, 0.2),
        ("test-D", "test", "candidate_like", 0.8, 0.8),
        ("test-D", "test", "other", 0.2, 0.1),
    )
    for index, (group_id, split, label, color, shape) in enumerate(cases):
        rows.append({
            "sample_id": f"sample-{index}",
            "group_id": group_id,
            "split": split,
            "label": label,
            "color_fraction": str(color),
            "shape_score": str(shape),
        })
    return rows


def scored_row(sample_id, label, color, shape):
    return {
        "sample_id": sample_id, "group_id": "teaching-group", "label": label,
        "color_fraction": color, "shape_score": shape,
    }


class DatasetAuditTests(unittest.TestCase):
    def test_same_group_in_two_splits_is_rejected(self):
        rows = sample_rows()
        rows[2]["group_id"] = "train-A"
        with self.assertRaisesRegex(ValueError, "group"):
            audit_samples(rows)

    def test_duplicate_sample_id_is_rejected(self):
        rows = sample_rows()
        rows[3]["sample_id"] = rows[0]["sample_id"]
        with self.assertRaisesRegex(ValueError, "sample_id"):
            audit_samples(rows)

    def test_invalid_feature_is_rejected_before_fit(self):
        for invalid in ("nan", "inf", "1.2", "-0.1", ""):
            with self.subTest(invalid=invalid):
                rows = sample_rows()
                rows[0]["color_fraction"] = invalid
                with self.assertRaisesRegex(ValueError, "color_fraction"):
                    audit_samples(rows)

    def test_unknown_label_or_split_is_rejected(self):
        for field, value in (("label", "unknown"), ("split", "holdout")):
            with self.subTest(field=field):
                rows = sample_rows()
                rows[0][field] = value
                with self.assertRaisesRegex(ValueError, field):
                    audit_samples(rows)

    def test_each_split_requires_both_labels(self):
        rows = sample_rows()
        rows[3]["label"] = "candidate_like"
        with self.assertRaisesRegex(ValueError, "both labels"):
            audit_samples(rows)

    def test_valid_csv_numbers_are_normalized(self):
        rows = audit_samples(sample_rows())
        self.assertEqual(rows[0]["color_fraction"], 0.9)
        self.assertEqual(rows[0]["shape_score"], 0.9)

    def test_extra_column_and_empty_group_are_rejected(self):
        rows = sample_rows()
        rows[0]["unexpected"] = "1"
        with self.assertRaisesRegex(ValueError, "schema"):
            audit_samples(rows)
        rows = sample_rows()
        rows[0]["group_id"] = "  "
        with self.assertRaisesRegex(ValueError, "group_id"):
            audit_samples(rows)


class ModelTests(unittest.TestCase):
    def test_centroids_use_training_rows_only(self):
        rows = sample_rows()
        rows.insert(2, {
            "sample_id": "train-candidate-2", "group_id": "train-B",
            "split": "train", "label": "candidate_like",
            "color_fraction": "0.7", "shape_score": "0.7",
        })
        rows.insert(3, {
            "sample_id": "train-other-2", "group_id": "train-B",
            "split": "train", "label": "other",
            "color_fraction": "0.3", "shape_score": "0.2",
        })
        rows[6]["color_fraction"] = "0.0"  # test value must not alter fit
        centroids = fit_centroids(audit_samples(rows))
        self.assertAlmostEqual(centroids["candidate_like"][0], 0.8)
        self.assertAlmostEqual(centroids["candidate_like"][1], 0.8)
        self.assertAlmostEqual(centroids["other"][0], 0.2)
        self.assertAlmostEqual(centroids["other"][1], 0.2)

    def test_raw_score_is_not_probability_and_gate_abstains(self):
        centroids = {"candidate_like": (0.8, 0.8), "other": (0.2, 0.2)}
        self.assertAlmostEqual(score((0.8, 0.7), centroids), 0.6)
        self.assertAlmostEqual(score((0.3, 0.2), centroids), -0.6)
        self.assertAlmostEqual(score((0.65, 0.6), centroids), 0.3)
        self.assertEqual(classify(0.6, 0.36), "candidate_like")
        self.assertEqual(classify(-0.6, 0.36), "other")
        self.assertIsNone(classify(0.3, 0.36))


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.centroids = {"candidate_like": (0.8, 0.8), "other": (0.2, 0.2)}

    def test_validation_selects_lowest_zero_false_positive_gate_with_max_coverage(self):
        rows = [
            scored_row("v1", "candidate_like", 0.8, 0.7),
            scored_row("v2", "other", 0.3, 0.2),
            scored_row("v3", "candidate_like", 0.55, 0.5),
            scored_row("v4", "other", 0.65, 0.6),
        ]
        chosen, trials = select_threshold(rows, self.centroids)
        self.assertEqual(chosen, 0.36)
        self.assertEqual([trial["counts"]["fp"] for trial in trials], [1, 1, 0])
        self.assertEqual(trials[2]["counts"]["decided"], 2)

    def test_no_eligible_validation_gate_fails_closed(self):
        rows = [scored_row("v1", "other", 0.8, 0.8)]
        with self.assertRaisesRegex(ValueError, "zero false positives"):
            select_threshold(rows, self.centroids)

    def test_empty_validation_set_cannot_choose_a_gate(self):
        with self.assertRaisesRegex(ValueError, "validation"):
            select_threshold([], self.centroids)

    def test_test_matrix_keeps_abstentions_out_of_four_cells(self):
        rows = [
            scored_row("d1", "candidate_like", 0.85, 0.75),
            scored_row("d2", "other", 0.2, 0.25),
            scored_row("d3", "candidate_like", 0.55, 0.55),
            scored_row("d4", "other", 0.65, 0.55),
            scored_row("e1", "candidate_like", 0.3, 0.2),
            scored_row("e2", "other", 0.8, 0.7),
            scored_row("e3", "candidate_like", 0.8, 0.8),
            scored_row("e4", "other", 0.2, 0.1),
        ]
        result = evaluate_rows(rows, self.centroids, 0.36)
        self.assertEqual(result["counts"], {
            "tp": 2, "fp": 1, "tn": 2, "fn": 1,
            "abstain_positive": 1, "abstain_negative": 1,
            "decided": 6, "total": 8,
        })
        self.assertEqual(result["metrics"]["coverage"], 0.75)
        self.assertAlmostEqual(result["metrics"]["precision_decided"], 2 / 3)
        self.assertAlmostEqual(result["metrics"]["recall_decided"], 2 / 3)
        self.assertAlmostEqual(result["metrics"]["accuracy_decided"], 4 / 6)
        self.assertIsNone(result["samples"][2]["prediction"])

    def test_metrics_with_zero_denominators_are_undefined(self):
        result = evaluate_rows(
            [scored_row("x", "candidate_like", 0.5, 0.5)],
            self.centroids, 0.36,
        )
        self.assertEqual(result["metrics"]["coverage"], 0.0)
        self.assertIsNone(result["metrics"]["precision_decided"])
        self.assertIsNone(result["metrics"]["recall_decided"])
        self.assertIsNone(result["metrics"]["accuracy_decided"])

    def test_displayed_six_decimal_score_is_the_decision_boundary(self):
        rows = [
            scored_row("positive-edge", "candidate_like", 0.6, 0.7),
            scored_row("negative-edge", "other", 0.3, 0.4),
            scored_row("positive-inside", "candidate_like", 0.6, 0.699999),
            scored_row("negative-inside", "other", 0.3, 0.400001),
        ]
        samples = evaluate_rows(rows, self.centroids, 0.36)["samples"]
        self.assertEqual([item["raw_score"] for item in samples],
                         [0.36, -0.36, 0.359999, -0.359999])
        self.assertEqual([item["prediction"] for item in samples],
                         ["candidate_like", "other", None, None])


class IntegrationTests(unittest.TestCase):
    def test_duplicate_csv_header_cannot_hide_a_column(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "duplicate-header.csv"
            path.write_text(
                "sample_id,group_id,split,label,color_fraction,shape_score,sample_id\n"
                "first,group-A,train,candidate_like,0.8,0.8,second\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "CSV header"):
                load_csv(path)

    def test_checked_in_csv_produces_hand_counted_test_results(self):
        path = Path(__file__).with_name("synthetic_samples.csv")
        report = run_experiment(load_csv(path))
        self.assertEqual(report["dataset"]["total"], 20)
        self.assertEqual(report["dataset"]["splits"], {
            "train": 8, "validation": 4, "test": 8,
        })
        self.assertEqual(report["centroids"], {
            "candidate_like": (0.8, 0.8), "other": (0.2, 0.2),
        })
        self.assertEqual(report["chosen_threshold"], 0.36)
        self.assertEqual(report["test"]["counts"]["fp"], 1)
        self.assertEqual(report["test"]["counts"]["fn"], 1)
        self.assertEqual(report["test"]["counts"]["decided"], 6)
        self.assertEqual(report["test"]["samples"][0]["group_id"], "test-D")

    def test_changing_test_labels_does_not_change_fit_or_selected_gate(self):
        path = Path(__file__).with_name("synthetic_samples.csv")
        rows = load_csv(path)
        original = run_experiment(rows)
        altered = [dict(row) for row in rows]
        for row in altered:
            if row["split"] == "test":
                row["label"] = "other" if row["label"] == "candidate_like" else "candidate_like"
        changed = run_experiment(altered)
        self.assertEqual(changed["centroids"], original["centroids"])
        self.assertEqual(changed["chosen_threshold"], original["chosen_threshold"])
        self.assertNotEqual(changed["test"]["counts"], original["test"]["counts"])

    def test_cli_emits_deterministic_json(self):
        script = Path(__file__).with_name("dataset_evaluation.py")
        first = subprocess.run(
            [sys.executable, str(script)], check=True, capture_output=True, text=True,
        ).stdout
        second = subprocess.run(
            [sys.executable, str(script)], check=True, capture_output=True, text=True,
        ).stdout
        self.assertEqual(first, second)
        report = json.loads(first)
        self.assertEqual(report["chosen_threshold"], 0.36)
        self.assertEqual(report["test"]["counts"]["total"], 8)


if __name__ == "__main__":
    unittest.main()
