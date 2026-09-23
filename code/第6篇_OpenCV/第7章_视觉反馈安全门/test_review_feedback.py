import copy
import importlib.util
import math
import re
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("review_feedback.py")


def fixture():
    frame = {
        "source": "synthetic",
        "run_id": "demo-001",
        "frame_id": 3,
        "timestamp_ms": 80,
        "candidate": {"centroid": (16.0, 18.0), "area": 100.0},
    }
    event = {
        "status": "STABLE",
        "frame_id": 3,
        "hits": 3,
        "centroid": (16.0, 18.0),
    }
    intent = {"kind": "indicator", "level": 12}
    context = {"now_ms": 100, "simulated_approval": True}
    policy = {
        "source": "synthetic",
        "run_id": "demo-001",
        "max_age_ms": 100,
        "roi": (0, 0, 160, 128),
        "max_level": 20,
    }
    return frame, event, intent, context, policy


class FeedbackReviewTests(unittest.TestCase):
    def module(self):
        self.assertTrue(SCRIPT.is_file(), "review_feedback.py must exist")
        spec = importlib.util.spec_from_file_location("review_feedback", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def review(self, frame=None, event=None, intent=None, context=None, policy=None):
        standard = fixture()
        provided = (frame, event, intent, context, policy)
        args = [copy.deepcopy(default if value is None else value)
                for default, value in zip(standard, provided)]
        return self.module().review_feedback(*args)

    def assert_blocked(self, decision, reason):
        self.assertEqual(decision["decision"], "BLOCKED")
        self.assertEqual(decision["reason"], reason)
        self.assertIsNone(decision["preview"])

    def test_valid_stable_event_yields_preview_only_not_a_command(self):
        decision = self.review()
        self.assertEqual(decision["decision"], "PREVIEW_ONLY")
        self.assertEqual(decision["reason"], "requires_separate_hardware_review")
        self.assertEqual(
            decision["preview"],
            {"kind": "indicator", "level": 12, "run_id": "demo-001", "frame_id": 3},
        )

    def test_nonstable_or_invalid_event_cannot_create_preview(self):
        for status in ("TENTATIVE", "LOST", "NO_CANDIDATE",
                       "REJECTED_ORDER", "REJECTED_GAP", "REJECTED_JUMP", "UNKNOWN"):
            with self.subTest(status=status):
                frame, event, *_ = fixture()
                event["status"] = status
                self.assert_blocked(self.review(frame=frame, event=event), "event_not_stable")
        _, event, *_ = fixture()
        event["hits"] = 2
        self.assert_blocked(self.review(event=event), "event_not_stable")

    def test_source_and_session_mismatch_block_preview(self):
        frame, *_ = fixture()
        frame["source"] = "other-camera"
        self.assert_blocked(self.review(frame=frame), "source_or_session_mismatch")
        frame, *_ = fixture()
        frame["run_id"] = "old-run"
        self.assert_blocked(self.review(frame=frame), "source_or_session_mismatch")

    def test_frame_id_and_centroid_must_match_event_to_frame(self):
        _, event, *_ = fixture()
        event["frame_id"] = 2
        self.assert_blocked(self.review(event=event), "event_frame_mismatch")
        _, event, *_ = fixture()
        event["centroid"] = (17.0, 18.0)
        self.assert_blocked(self.review(event=event), "event_frame_mismatch")
        frame, *_ = fixture()
        frame["candidate"] = None
        self.assert_blocked(self.review(frame=frame), "event_frame_mismatch")

    def test_age_boundary_and_future_timestamp(self):
        _, _, _, context, _ = fixture()
        context["now_ms"] = 180
        self.assertEqual(self.review(context=context)["decision"], "PREVIEW_ONLY")
        context["now_ms"] = 181
        self.assert_blocked(self.review(context=context), "stale_or_future_frame")
        context["now_ms"] = 79
        self.assert_blocked(self.review(context=context), "stale_or_future_frame")

    def test_roi_and_nonfinite_centroid_block_preview(self):
        frame, event, *_ = fixture()
        frame["candidate"]["centroid"] = (160.0, 18.0)
        event["centroid"] = (160.0, 18.0)
        self.assert_blocked(self.review(frame=frame, event=event), "outside_roi")
        frame, event, *_ = fixture()
        frame["candidate"]["centroid"] = (math.nan, 18.0)
        event["centroid"] = (math.nan, 18.0)
        self.assert_blocked(self.review(frame=frame, event=event), "malformed_record")

    def test_intent_kind_and_level_are_bounded(self):
        _, _, intent, _, _ = fixture()
        intent["level"] = 21
        self.assert_blocked(self.review(intent=intent), "intent_out_of_bounds")
        intent["level"] = -1
        self.assert_blocked(self.review(intent=intent), "intent_out_of_bounds")
        intent["level"] = 12
        intent["kind"] = "motor"
        self.assert_blocked(self.review(intent=intent), "intent_out_of_bounds")

    def test_simulated_approval_must_be_explicit_boolean_true(self):
        _, _, _, context, _ = fixture()
        for value in (False, 1, "yes", None):
            with self.subTest(value=value):
                context["simulated_approval"] = value
                self.assert_blocked(self.review(context=context), "approval_missing")

    def test_invalid_policy_is_rejected(self):
        module = self.module()
        for change in (
            {"source": ""},
            {"run_id": ""},
            {"max_age_ms": 0},
            {"roi": (0, 0, 0, 128)},
            {"max_level": -1},
        ):
            with self.subTest(change=change):
                *_, policy = fixture()
                policy.update(change)
                with self.assertRaises(ValueError):
                    module.review_feedback(*fixture()[:4], policy)

    def test_cli_reports_only_preview_and_blocked_decisions(self):
        first = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        second = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(
            re.findall(r"decision=([A-Z_]+)", first.stdout),
            ["PREVIEW_ONLY", "BLOCKED", "BLOCKED"],
        )
        self.assertIn("reason=stale_or_future_frame", first.stdout)


if __name__ == "__main__":
    unittest.main()
