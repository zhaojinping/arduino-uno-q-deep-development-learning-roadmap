import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).with_name("locate_color.py")
GREEN_LOW = (35, 80, 80)
GREEN_HIGH = (85, 255, 255)


class LocateColorTests(unittest.TestCase):
    def load_module(self):
        self.assertTrue(SCRIPT.is_file(), "locate_color.py must exist")
        spec = importlib.util.spec_from_file_location("locate_color", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_green_target_excludes_red_and_single_pixel_noise(self):
        module = self.load_module()
        frame = np.full((64, 96, 3), 30, dtype=np.uint8)
        frame[10:30, 20:50] = (0, 180, 0)
        frame[35:55, 60:85] = (0, 0, 180)
        frame[3, 3] = (0, 180, 0)
        original = frame.copy()

        result = module.locate_hsv_region(
            frame, GREEN_LOW, GREEN_HIGH, min_area=100, kernel_size=3
        )

        self.assertEqual(result["raw_pixels"], 601)
        self.assertEqual(result["clean_pixels"], 600)
        self.assertEqual(result["contour_count"], 1)
        self.assertEqual(result["eligible_count"], 1)
        self.assertEqual(result["target"]["bbox"], (20, 10, 30, 20))
        self.assertEqual(result["target"]["area"], 551.0)
        self.assertEqual(result["target"]["centroid"], (34.5, 19.5))
        np.testing.assert_array_equal(frame, original)

    def test_no_candidate_does_not_reuse_previous_location(self):
        module = self.load_module()
        frame = np.zeros((64, 96, 3), dtype=np.uint8)
        frame[10:30, 20:50] = (0, 180, 0)
        found = module.locate_hsv_region(
            frame, GREEN_LOW, GREEN_HIGH, min_area=100, kernel_size=3
        )
        self.assertIsNotNone(found["target"])

        frame[:] = 0
        first = module.locate_hsv_region(
            frame, GREEN_LOW, GREEN_HIGH, min_area=100, kernel_size=3
        )
        self.assertIsNone(first["target"])
        self.assertEqual(first["eligible_count"], 0)

        frame[10:30, 20:50] = (0, 180, 0)
        second = module.locate_hsv_region(
            frame, GREEN_LOW, GREEN_HIGH, min_area=600, kernel_size=3
        )
        self.assertIsNone(second["target"])
        self.assertEqual(second["contour_count"], 1)
        self.assertEqual(second["eligible_count"], 0)

    def test_invalid_frame_bounds_and_kernel_are_rejected(self):
        module = self.load_module()
        valid = np.zeros((8, 8, 3), dtype=np.uint8)
        for bad_frame in (
            np.zeros((0, 8, 3), dtype=np.uint8),
            np.zeros((8, 8), dtype=np.uint8),
            np.zeros((8, 8, 3), dtype=np.float32),
            np.zeros((8, 8, 4), dtype=np.uint8),
        ):
            with self.subTest(shape=bad_frame.shape, dtype=str(bad_frame.dtype)):
                with self.assertRaises(ValueError):
                    module.locate_hsv_region(
                        bad_frame, GREEN_LOW, GREEN_HIGH, 1, 3
                    )
        for lower, upper in (
            ((170, 80, 80), (10, 255, 255)),
            ((35, 80, 80), (180, 255, 255)),
            ((35, 80), (85, 255, 255)),
        ):
            with self.subTest(lower=lower, upper=upper):
                with self.assertRaises(ValueError):
                    module.locate_hsv_region(valid, lower, upper, 1, 3)
        for area, kernel in ((0, 3), (True, 3), (1, 2), (1, 0)):
            with self.subTest(area=area, kernel=kernel):
                with self.assertRaises(ValueError):
                    module.locate_hsv_region(
                        valid, GREEN_LOW, GREEN_HIGH, area, kernel
                    )

    def test_cli_reports_synthetic_candidate_and_rejects_bad_area(self):
        first = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        second = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertIn("raw_pixels=2101 clean_pixels=2100", first.stdout)
        self.assertIn("contours=2 eligible=2", first.stdout)
        self.assertIn("bbox=(15, 20, 40, 40)", first.stdout)

        none = subprocess.run(
            [sys.executable, str(SCRIPT), "--min-area", "100000"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(none.returncode, 0, none.stderr)
        self.assertIn("target=NO_CANDIDATE", none.stdout)
        self.assertNotIn("bbox=", none.stdout)

        bad = subprocess.run(
            [sys.executable, str(SCRIPT), "--min-area", "0"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(bad.returncode, 2)
        self.assertIn("positive finite", bad.stderr)


if __name__ == "__main__":
    unittest.main()
