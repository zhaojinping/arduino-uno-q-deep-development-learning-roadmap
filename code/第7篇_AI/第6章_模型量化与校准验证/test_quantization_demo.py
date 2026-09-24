import json
import subprocess
import sys
import unittest
from pathlib import Path

from quantization_demo import QuantizationInputError, build_report, simulate_quantization


SCRIPT = Path(__file__).with_name("quantization_demo.py")
NARROW_CALIBRATION = [-1.0, -0.5, 0.0, 0.5, 1.0]
OUTLIER_INCLUSIVE_CALIBRATION = [-8.0, -1.0, -0.5, 0.0, 0.5, 1.0, 8.0]
EVALUATION = [-1.5, -0.1, 0.0, 0.1, 1.5]


class QuantizationSimulationTests(unittest.TestCase):
    def test_narrow_calibration_uses_symmetric_int8_scale_and_rounding(self):
        result = simulate_quantization(NARROW_CALIBRATION, EVALUATION)

        self.assertEqual(result["scale"], 1.0 / 127.0)
        self.assertEqual(result["zero_point"], 0)
        self.assertEqual(result["quantized_values"], [-127, -13, 0, 13, 127])

    def test_values_outside_calibrated_integer_range_are_counted_as_clipped(self):
        result = simulate_quantization(NARROW_CALIBRATION, EVALUATION)

        self.assertEqual(result["clipped_count"], 2)
        self.assertEqual(result["reconstructed_values"][0], -1.0)
        self.assertEqual(result["reconstructed_values"][-1], 1.0)
        self.assertEqual(result["max_absolute_error"], 0.5)

    def test_outlier_calibration_reduces_clipping_but_coarsens_small_values(self):
        narrow = simulate_quantization(NARROW_CALIBRATION, EVALUATION)
        wide = simulate_quantization(OUTLIER_INCLUSIVE_CALIBRATION, EVALUATION)

        self.assertEqual(wide["scale"], 8.0 / 127.0)
        self.assertEqual(wide["clipped_count"], 0)
        self.assertEqual(wide["quantized_values"], [-24, -2, 0, 2, 24])
        self.assertAlmostEqual(narrow["reconstructed_values"][1], -13.0 / 127.0)
        self.assertAlmostEqual(wide["reconstructed_values"][1], -16.0 / 127.0)
        self.assertGreater(wide["absolute_errors"][1], narrow["absolute_errors"][1])

    def test_all_zero_calibration_is_rejected_instead_of_emitting_zero_scale(self):
        with self.assertRaises(QuantizationInputError):
            simulate_quantization([0.0, 0.0], [0.0])

    def test_empty_calibration_or_evaluation_is_rejected(self):
        with self.assertRaises(QuantizationInputError):
            simulate_quantization([], [0.1])
        with self.assertRaises(QuantizationInputError):
            simulate_quantization([1.0], [])

    def test_boolean_and_nonfinite_values_are_rejected(self):
        for invalid in (True, float("nan"), float("inf"), float("-inf")):
            with self.subTest(invalid=invalid):
                with self.assertRaises(QuantizationInputError):
                    simulate_quantization([1.0], [invalid])
                with self.assertRaises(QuantizationInputError):
                    simulate_quantization([invalid], [1.0])

    def test_report_estimates_only_raw_element_payload_not_model_file_size(self):
        report = build_report()

        self.assertEqual(report["payload_estimate"]["float32_bytes"], 20)
        self.assertEqual(report["payload_estimate"]["int8_bytes"], 5)
        self.assertEqual(report["payload_estimate"]["ratio"], 4.0)
        self.assertIs(report["payload_estimate"]["includes_model_overhead"], False)

    def test_report_is_always_descriptive_and_never_claims_acceptance(self):
        report = build_report()

        self.assertEqual(report["status"], "REPORT_ONLY")
        self.assertIs(report["report_only"], True)
        self.assertIs(report["thresholds_applied"], False)
        self.assertNotIn("decision", report)


class CommandLineTests(unittest.TestCase):
    def test_cli_emits_machine_readable_report_only_json(self):
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            cwd=SCRIPT.parent,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "REPORT_ONLY")
        self.assertIs(report["thresholds_applied"], False)
        self.assertEqual(report["scenarios"]["narrow_calibration"]["clipped_count"], 2)
        self.assertEqual(report["scenarios"]["outlier_inclusive_calibration"]["clipped_count"], 0)


if __name__ == "__main__":
    unittest.main()
