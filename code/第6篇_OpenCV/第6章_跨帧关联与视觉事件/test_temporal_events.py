import importlib.util
import math
import re
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("temporal_events.py")


def frame(frame_id, timestamp_ms, xy=None, source="synthetic"):
    candidate = None if xy is None else {"centroid": xy, "area": 100.0}
    return {
        "source": source,
        "frame_id": frame_id,
        "timestamp_ms": timestamp_ms,
        "candidate": candidate,
    }


class TemporalEventsTests(unittest.TestCase):
    def load_module(self):
        self.assertTrue(SCRIPT.is_file(), "temporal_events.py must exist")
        spec = importlib.util.spec_from_file_location("temporal_events", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def tracker(self):
        module = self.load_module()
        return module.TemporalGate(
            expected_source="synthetic", min_hits=3,
            max_step_px=10.0, max_gap_ms=100,
        )

    def test_nearby_consecutive_hits_become_stable_only_on_third_frame(self):
        gate = self.tracker()
        results = [
            gate.process(frame(1, 0, (10.0, 10.0))),
            gate.process(frame(2, 40, (13.0, 14.0))),
            gate.process(frame(3, 80, (16.0, 18.0))),
            gate.process(frame(4, 120, (17.0, 18.0))),
        ]
        self.assertEqual(
            [result["status"] for result in results],
            ["TENTATIVE", "TENTATIVE", "STABLE", "CONTINUING"],
        )
        self.assertEqual([result["hits"] for result in results], [1, 2, 3, 4])
        self.assertEqual(results[-1]["centroid"], (17.0, 18.0))

    def test_loss_removes_location_and_next_hit_starts_new_hypothesis(self):
        gate = self.tracker()
        for frame_id, timestamp_ms, xy in (
            (1, 0, (10.0, 10.0)),
            (2, 40, (13.0, 14.0)),
            (3, 80, (16.0, 18.0)),
        ):
            gate.process(frame(frame_id, timestamp_ms, xy))
        lost = gate.process(frame(4, 120))
        self.assertEqual(lost["status"], "LOST")
        self.assertIsNone(lost["centroid"])
        self.assertEqual(lost["hits"], 0)
        restarted = gate.process(frame(5, 160, (20.0, 20.0)))
        self.assertEqual(restarted["status"], "TENTATIVE")
        self.assertEqual(restarted["hits"], 1)

    def test_far_jump_is_rejected_without_reusing_confirmed_location(self):
        gate = self.tracker()
        gate.process(frame(1, 0, (10.0, 10.0)))
        gate.process(frame(2, 40, (13.0, 14.0)))
        gate.process(frame(3, 80, (16.0, 18.0)))
        jump = gate.process(frame(4, 120, (100.0, 100.0)))
        self.assertEqual(jump["status"], "REJECTED_JUMP")
        self.assertIsNone(jump["centroid"])
        self.assertEqual(jump["hits"], 0)
        new = gate.process(frame(5, 160, (100.0, 100.0)))
        self.assertEqual(new["status"], "TENTATIVE")

    def test_missing_duplicate_and_stale_frames_reset_hypothesis(self):
        gate = self.tracker()
        gate.process(frame(1, 0, (10.0, 10.0)))
        gate.process(frame(2, 40, (13.0, 14.0)))
        gate.process(frame(3, 80, (16.0, 18.0)))
        skipped = gate.process(frame(5, 160, (18.0, 19.0)))
        self.assertEqual(skipped["status"], "REJECTED_GAP")
        self.assertIsNone(skipped["centroid"])
        self.assertEqual(gate.process(frame(6, 200, (18.0, 19.0)))["status"], "TENTATIVE")
        duplicate = gate.process(frame(6, 240, (19.0, 19.0)))
        self.assertEqual(duplicate["status"], "REJECTED_ORDER")
        self.assertEqual(gate.process(frame(7, 280, (19.0, 19.0)))["status"], "TENTATIVE")
        stale = gate.process(frame(8, 500, (20.0, 19.0)))
        self.assertEqual(stale["status"], "REJECTED_GAP")
        self.assertIsNone(stale["centroid"])

    def test_bad_input_is_rejected_and_clears_prior_track(self):
        gate = self.tracker()
        gate.process(frame(1, 0, (10.0, 10.0)))
        gate.process(frame(2, 40, (13.0, 14.0)))
        gate.process(frame(3, 80, (16.0, 18.0)))
        with self.assertRaises(ValueError):
            gate.process(frame(4, 120, (math.nan, 20.0)))
        after = gate.process(frame(5, 160, (20.0, 20.0)))
        self.assertEqual(after["status"], "REJECTED_GAP")
        self.assertIsNone(after["centroid"])
        with self.assertRaises(ValueError):
            gate.process(frame(6, 200, (20.0, 20.0), source="other"))

    def test_invalid_gate_configuration_is_rejected(self):
        module = self.load_module()
        for kwargs in (
            {"expected_source": "", "min_hits": 3, "max_step_px": 10, "max_gap_ms": 100},
            {"expected_source": "synthetic", "min_hits": 1, "max_step_px": 10, "max_gap_ms": 100},
            {"expected_source": "synthetic", "min_hits": 3, "max_step_px": 0, "max_gap_ms": 100},
            {"expected_source": "synthetic", "min_hits": 3, "max_step_px": 10, "max_gap_ms": 0},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    module.TemporalGate(**kwargs)

    def test_cli_is_deterministic_and_shows_loss_and_jump(self):
        first = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        second = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(
            re.findall(r"status=([A-Z_]+)", first.stdout),
            ["TENTATIVE", "TENTATIVE", "STABLE", "LOST",
             "TENTATIVE", "TENTATIVE", "STABLE", "REJECTED_JUMP"],
        )
        self.assertIn("frame=4 timestamp_ms=120 status=LOST hits=0 centroid=None", first.stdout)


if __name__ == "__main__":
    unittest.main()
