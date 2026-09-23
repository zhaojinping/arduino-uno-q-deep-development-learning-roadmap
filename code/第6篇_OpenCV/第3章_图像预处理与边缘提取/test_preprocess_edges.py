import re
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("preprocess_edges.py")


def run_cli(*arguments):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=SCRIPT.parent,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


class PreprocessEdgesCliTests(unittest.TestCase):
    def test_demo_reduces_noise_and_returns_valid_edge_maps(self):
        result = run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("input_shape=(128, 160) dtype=uint8", result.stdout)

        for noise_model in ("gaussian", "salt_pepper"):
            match = re.search(
                noise_model
                + r"_rmse_before=([0-9.]+) "
                + noise_model
                + r"_rmse_after=([0-9.]+)",
                result.stdout,
            )
            self.assertIsNotNone(match, result.stdout)
            self.assertLess(float(match.group(2)), float(match.group(1)))

        for edge_map in ("gaussian", "median"):
            match = re.search(
                edge_map + r"_edge_pixels=([0-9]+)", result.stdout
            )
            self.assertIsNotNone(match, result.stdout)
            self.assertGreater(int(match.group(1)), 0)

        self.assertIn(
            "edge_map_shape=(128, 160) dtype=uint8 values=[0, 255]",
            result.stdout,
        )

    def test_demo_is_deterministic_for_a_fixed_seed(self):
        first = run_cli("--seed", "2026")
        second = run_cli("--seed", "2026")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)

    def test_cli_rejects_non_increasing_canny_thresholds(self):
        result = run_cli("--low-threshold", "150", "--high-threshold", "50")
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "high threshold must be greater than low threshold",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
