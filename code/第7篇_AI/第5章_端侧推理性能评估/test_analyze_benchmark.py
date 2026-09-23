import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from analyze_benchmark import BenchmarkInputError, analyze_run, percentile_nearest_rank


ANALYZER = Path(__file__).with_name("analyze_benchmark.py")


def make_run(warmups, measured):
    samples = []
    for phase, values in (("warmup", warmups), ("measured", measured)):
        for value in values:
            index = len(samples) + 1
            samples.append(
                {
                    "index": index,
                    "phase": phase,
                    "latency_ms": value,
                    "rss_mib": 400.0 + index,
                }
            )
    return {
        "schema_version": 1,
        "run_id": "synthetic-run-001",
        "environment": {
            "platform_id": "synthetic-host",
            "os_image_id": "teaching-image-v1",
            "runtime_id": "synthetic-runtime-v1",
            "execution_provider_id": "CPU",
            "artifact_id": "synthetic-model-v1",
            "input_shape": [1, 3, 224, 224],
            "batch_size": 1,
            "thread_count": 2,
        },
        "warmup_count": len(warmups),
        "measured_count": len(measured),
        "samples": samples,
    }


class PercentileTests(unittest.TestCase):
    def test_nearest_rank_uses_ceiling_of_percentile_times_sample_count(self):
        values = list(range(1, 21))
        self.assertEqual(percentile_nearest_rank(values, 0.50), 10)
        self.assertEqual(percentile_nearest_rank(values, 0.95), 19)

    def test_nearest_rank_rejects_empty_values(self):
        with self.assertRaises(BenchmarkInputError):
            percentile_nearest_rank([], 0.5)

    def test_nearest_rank_rejects_out_of_range_or_boolean_percentile(self):
        for percentile in (0, -0.1, 1.01, float("nan"), True):
            with self.subTest(percentile=percentile):
                with self.assertRaises(BenchmarkInputError):
                    percentile_nearest_rank([1.0, 2.0], percentile)


class AnalyzeRunTests(unittest.TestCase):
    def test_warmups_do_not_affect_latency_or_observed_rss_summary(self):
        run = make_run([999.0, 888.0], [10.0, 20.0, 30.0, 40.0])
        run["samples"][0]["rss_mib"] = 1000.0
        run["samples"][1]["rss_mib"] = 2000.0
        report = analyze_run(run)

        self.assertEqual(report["latency_ms"]["p50_nearest_rank"], 20.0)
        self.assertEqual(report["latency_ms"]["p95_nearest_rank"], 40.0)
        self.assertEqual(report["latency_ms"]["max"], 40.0)
        self.assertEqual(report["memory_mib"]["observed_max_rss"], 406.0)

    def test_valid_run_is_report_only_and_applies_no_threshold(self):
        report = analyze_run(make_run([5.0], [10000.0, 20000.0]))

        self.assertEqual(report["status"], "REPORT_ONLY")
        self.assertIs(report["report_only"], True)
        self.assertIs(report["thresholds_applied"], False)

    def test_report_preserves_run_identity_and_counts(self):
        report = analyze_run(make_run([5.0, 6.0], [10.0, 11.0, 12.0]))

        self.assertEqual(report["run_id"], "synthetic-run-001")
        self.assertEqual(report["warmup_count"], 2)
        self.assertEqual(report["measured_count"], 3)

    def test_nearest_rank_summary_matches_hand_computed_values(self):
        report = analyze_run(make_run([], list(range(1, 21))))

        self.assertEqual(report["latency_ms"]["p50_nearest_rank"], 10)
        self.assertEqual(report["latency_ms"]["p95_nearest_rank"], 19)
        self.assertEqual(report["latency_ms"]["max"], 20)

    def test_mean_does_not_overflow_for_finite_large_latencies(self):
        report = analyze_run(make_run([], [1e308, 1e308]))

        self.assertEqual(report["latency_ms"]["mean"], 1e308)

    def test_wrong_schema_version_is_rejected(self):
        run = make_run([], [1.0])
        run["schema_version"] = 2

        with self.assertRaises(BenchmarkInputError):
            analyze_run(run)

    def test_unknown_top_level_field_is_rejected(self):
        run = make_run([], [1.0])
        run["unexpected"] = "not part of schema v1"

        with self.assertRaises(BenchmarkInputError):
            analyze_run(run)

    def test_missing_environment_identity_is_rejected(self):
        run = make_run([], [1.0])
        del run["environment"]["runtime_id"]

        with self.assertRaises(BenchmarkInputError):
            analyze_run(run)

    def test_boolean_batch_size_is_not_accepted_as_an_integer(self):
        run = make_run([], [1.0])
        run["environment"]["batch_size"] = True

        with self.assertRaises(BenchmarkInputError):
            analyze_run(run)

    def test_non_positive_or_boolean_input_dimension_is_rejected(self):
        for dimension in (0, -1, True, 2.5):
            with self.subTest(dimension=dimension):
                run = make_run([], [1.0])
                run["environment"]["input_shape"] = [1, dimension]
                with self.assertRaises(BenchmarkInputError):
                    analyze_run(run)

    def test_declared_counts_must_match_sample_rows(self):
        run = make_run([1.0], [2.0, 3.0])
        run["measured_count"] = 1

        with self.assertRaises(BenchmarkInputError):
            analyze_run(run)

    def test_sample_phase_must_follow_declared_warmup_boundary(self):
        run = make_run([1.0], [2.0, 3.0])
        run["samples"][1]["phase"] = "warmup"

        with self.assertRaises(BenchmarkInputError):
            analyze_run(run)

    def test_sample_indices_must_be_contiguous_and_one_based(self):
        run = make_run([], [1.0, 2.0])
        run["samples"][1]["index"] = 3

        with self.assertRaises(BenchmarkInputError):
            analyze_run(run)

    def test_empty_measured_set_is_rejected(self):
        with self.assertRaises(BenchmarkInputError):
            analyze_run(make_run([1.0], []))

    def test_boolean_zero_negative_nonfinite_and_non_numeric_latency_are_rejected(self):
        invalid_values = (True, 0, -0.1, float("nan"), float("inf"), float("-inf"), "1.0", None)
        for value in invalid_values:
            with self.subTest(value=value):
                run = make_run([], [1.0])
                run["samples"][0]["latency_ms"] = value
                with self.assertRaises(BenchmarkInputError):
                    analyze_run(run)

    def test_boolean_zero_negative_nonfinite_and_non_numeric_rss_are_rejected(self):
        invalid_values = (True, 0, -0.1, float("nan"), float("inf"), float("-inf"), "1.0", None)
        for value in invalid_values:
            with self.subTest(value=value):
                run = make_run([], [1.0])
                run["samples"][0]["rss_mib"] = value
                with self.assertRaises(BenchmarkInputError):
                    analyze_run(run)


class CommandLineTests(unittest.TestCase):
    def test_valid_cli_report_is_json_and_does_not_modify_input(self):
        run = make_run([100.0], [10.0, 20.0])
        original = json.dumps(run)
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "run.json"
            input_path.write_text(original, encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-B", str(ANALYZER), "--input", str(input_path)],
                cwd=ANALYZER.parent,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["status"], "REPORT_ONLY")
            self.assertEqual(input_path.read_text(encoding="utf-8"), original)

    def test_invalid_cli_input_is_blocked_with_nonzero_exit_code(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "invalid.json"
            input_path.write_text("{broken", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-B", str(ANALYZER), "--input", str(input_path)],
                cwd=ANALYZER.parent,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(json.loads(completed.stderr)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
