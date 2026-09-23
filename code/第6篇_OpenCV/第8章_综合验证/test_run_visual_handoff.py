import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("run_visual_handoff.py")


class IntegratedVisualHandoffTests(unittest.TestCase):
    def module(self):
        self.assertTrue(SCRIPT.is_file(), "run_visual_handoff.py must exist")
        spec = importlib.util.spec_from_file_location("run_visual_handoff", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def records(self):
        return self.module().run_demo()

    def by_case(self):
        return {item["case"]: item for item in self.records()}

    def test_real_three_stage_pipeline_reaches_preview_only_on_third_hit(self):
        records = self.records()
        self.assertEqual(
            [item["temporal_status"] for item in records if item["stage"] == "pipeline"][:3],
            ["TENTATIVE", "TENTATIVE", "STABLE"],
        )
        self.assertEqual(
            [item["decision"] for item in records if item["stage"] == "pipeline"][:3],
            ["BLOCKED", "BLOCKED", "PREVIEW_ONLY"],
        )
        stable = self.by_case()["fresh_stable"]
        self.assertEqual(stable["candidate"], "PIXEL_CANDIDATE")
        self.assertEqual(stable["centroid"], (30.5, 29.5))
        self.assertEqual(stable["area_px2"], 361.0)
        self.assertEqual(stable["preview"]["frame_id"], 3)
        self.assertEqual(
            [item["case"] for item in records if item["decision"] == "PREVIEW_ONLY"],
            ["fresh_stable"],
        )
        self.assertTrue(all(
            item["preview"] is None for item in records if item["decision"] == "BLOCKED"
        ))

    def test_blank_frame_loses_target_and_next_frame_starts_new_hypothesis(self):
        records = self.by_case()
        lost = records["target_lost"]
        self.assertEqual(lost["candidate"], "NO_CANDIDATE")
        self.assertEqual(lost["temporal_status"], "LOST")
        self.assertEqual(lost["decision"], "BLOCKED")
        self.assertIsNone(lost["preview"])
        self.assertEqual(records["reacquire_1"]["temporal_status"], "TENTATIVE")
        self.assertIsNone(records["reacquire_1"]["preview"])

    def test_stale_stable_event_does_not_pass_feedback_review(self):
        stale = self.by_case()["stale_stable"]
        self.assertEqual(stale["temporal_status"], "STABLE")
        self.assertEqual(stale["timestamp_ms"], 240)
        self.assertEqual(stale["observed_at_ms"], 400)
        self.assertEqual(stale["decision"], "BLOCKED")
        self.assertEqual(stale["reason"], "stale_or_future_frame")
        self.assertIsNone(stale["preview"])

    def test_large_pixel_jump_discards_position_and_preview(self):
        jump = self.by_case()["jump"]
        self.assertEqual(jump["candidate"], "PIXEL_CANDIDATE")
        self.assertEqual(jump["temporal_status"], "REJECTED_JUMP")
        self.assertEqual(jump["decision"], "BLOCKED")
        self.assertIsNotNone(jump["candidate_centroid"])
        self.assertIsNone(jump["centroid"])
        self.assertIsNone(jump["preview"])

    def test_wrong_run_is_review_probe_not_extra_capture_frame(self):
        records = self.records()
        probe = next(item for item in records if item["case"] == "wrong_run_probe")
        self.assertEqual(probe["stage"], "review_probe")
        self.assertEqual(probe["frame_id"], 3)
        self.assertEqual(probe["temporal_status"], "STABLE")
        self.assertEqual(probe["decision"], "BLOCKED")
        self.assertEqual(probe["reason"], "source_or_session_mismatch")
        self.assertIsNone(probe["preview"])
        self.assertEqual(
            [item["frame_id"] for item in records if item["stage"] == "pipeline"],
            [1, 2, 3, 4, 5, 6, 7, 8],
        )

    def test_cli_outputs_deterministic_parseable_json_lines(self):
        first = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        second = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        lines = [json.loads(line) for line in first.stdout.splitlines()]
        self.assertEqual(len(lines), 9)
        self.assertEqual(lines[2]["case"], "fresh_stable")
        self.assertEqual(lines[2]["decision"], "PREVIEW_ONLY")
        self.assertEqual(lines[-1]["case"], "jump")
        self.assertEqual(lines[-1]["decision"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
