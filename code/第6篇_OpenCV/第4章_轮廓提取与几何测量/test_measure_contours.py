import importlib.util
import math
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).with_name("measure_contours.py")


def load_module():
    spec = importlib.util.spec_from_file_location("measure_contours", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContourGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert SCRIPT.is_file(), "measure_contours.py must exist"
        cls.module = load_module()

    def test_filters_speck_and_reports_pixel_geometry(self):
        mask = np.zeros((80, 100), dtype=np.uint8)
        mask[10:30, 20:50] = 255
        mask[2:4, 2:4] = 255
        snapshot = mask.copy()

        result = self.module.measure_contours(mask, min_area=100)

        self.assertEqual(result["raw_count"], 2)
        self.assertEqual(result["rejected_count"], 1)
        self.assertEqual(len(result["accepted"]), 1)
        shape = result["accepted"][0]
        self.assertEqual(shape["bbox"], (20, 10, 30, 20))
        self.assertEqual(shape["area"], 551.0)
        self.assertEqual(shape["perimeter"], 96.0)
        self.assertEqual(shape["centroid"], (34.5, 19.5))
        self.assertEqual(np.count_nonzero(mask), 604)
        np.testing.assert_array_equal(mask, snapshot)

    def test_rejects_invalid_mask_and_area_threshold(self):
        measure = self.module.measure_contours
        for mask in (
            np.zeros((0, 4), dtype=np.uint8),
            np.zeros((4, 4, 3), dtype=np.uint8),
            np.zeros((4, 4), dtype=np.float32),
            np.full((4, 4), 127, dtype=np.uint8),
        ):
            with self.subTest(shape=mask.shape, dtype=str(mask.dtype)):
                with self.assertRaises(ValueError):
                    measure(mask, min_area=1)
        for threshold in (0, -1, math.nan, math.inf):
            with self.subTest(threshold=threshold):
                with self.assertRaises(ValueError):
                    measure(np.zeros((4, 4), dtype=np.uint8), min_area=threshold)

    def test_empty_foreground_is_valid_no_detection(self):
        result = self.module.measure_contours(
            np.zeros((12, 12), dtype=np.uint8), min_area=1
        )
        self.assertEqual(result, {
            "raw_count": 0,
            "rejected_count": 0,
            "accepted": [],
        })

    def test_cli_demo_is_deterministic_and_rejects_bad_threshold(self):
        first = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        second = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.stdout, first.stdout)
        self.assertIn("raw_contours=3 accepted=2 rejected=1", first.stdout)
        self.assertIn("bbox=(15, 20, 40, 30)", first.stdout)
        self.assertIn("bbox=(90, 60, 50, 45)", first.stdout)

        bad = subprocess.run(
            [sys.executable, str(SCRIPT), "--min-area", "0"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(bad.returncode, 2)
        self.assertIn("positive finite", bad.stderr)


if __name__ == "__main__":
    unittest.main()
