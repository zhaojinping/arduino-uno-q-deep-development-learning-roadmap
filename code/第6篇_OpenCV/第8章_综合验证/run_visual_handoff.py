"""Integrate Chapters 5–7 with synthetic frames and review-only evidence.

The output is deterministic JSON Lines. It never opens a camera, contacts a
Bridge, or sends an MCU command. PREVIEW_ONLY is documentation, not authority.
"""

import importlib.util
import json
from pathlib import Path

import numpy as np


PART_DIR = Path(__file__).resolve().parent.parent


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scene(left):
    frame = np.full((128, 160, 3), 30, dtype=np.uint8)
    if left is not None:
        frame[20:40, left:left + 20] = (0, 180, 0)
    return frame


def _record(case, stage, frame, event, reviewed):
    candidate = frame["candidate"]
    return {
        "case": case,
        "stage": stage,
        "source": frame["source"],
        "run_id": frame["run_id"],
        "frame_id": frame["frame_id"],
        "timestamp_ms": frame["timestamp_ms"],
        "observed_at_ms": frame["observed_at_ms"],
        "candidate": "NO_CANDIDATE" if candidate is None else "PIXEL_CANDIDATE",
        "area_px2": None if candidate is None else candidate["area"],
        "candidate_centroid": None if candidate is None else candidate["centroid"],
        "centroid": event["centroid"],
        "temporal_status": event["status"],
        "hits": event["hits"],
        "decision": reviewed["decision"],
        "reason": reviewed["reason"],
        "preview": reviewed["preview"],
    }


def run_demo():
    """Return eight real pipeline records plus one review-only fault probe."""
    locator = _load_module(
        "chapter5_locate_color",
        PART_DIR / "第5章_颜色分割与目标定位" / "locate_color.py",
    )
    temporal = _load_module(
        "chapter6_temporal_events",
        PART_DIR / "第6章_跨帧关联与视觉事件" / "temporal_events.py",
    )
    reviewer = _load_module(
        "chapter7_review_feedback",
        PART_DIR / "第7章_视觉反馈安全门" / "review_feedback.py",
    )

    gate = temporal.TemporalGate(
        expected_source="synthetic", min_hits=3, max_step_px=10.0, max_gap_ms=100
    )
    policy = {
        "source": "synthetic",
        "run_id": "demo-001",
        "max_age_ms": 100,
        "roi": (0, 0, 160, 128),
        "max_level": 20,
    }
    intent = {"kind": "indicator", "level": 12}
    cases = (
        ("warmup_1", 1, 0, 15, 20),
        ("warmup_2", 2, 40, 18, 60),
        ("fresh_stable", 3, 80, 21, 100),
        ("target_lost", 4, 120, None, 140),
        ("reacquire_1", 5, 160, 100, 180),
        ("reacquire_2", 6, 200, 103, 220),
        ("stale_stable", 7, 240, 106, 400),
        ("jump", 8, 280, 130, 300),
    )

    records = []
    for case, frame_id, timestamp_ms, left, observed_at_ms in cases:
        result = locator.locate_hsv_region(
            _scene(left), locator.GREEN_LOW, locator.GREEN_HIGH,
            min_area=100, kernel_size=3,
        )
        frame = {
            "source": "synthetic",
            "run_id": "demo-001",
            "frame_id": frame_id,
            "timestamp_ms": timestamp_ms,
            "observed_at_ms": observed_at_ms,
            "candidate": result["target"],
        }
        event = gate.process(frame)
        reviewed = reviewer.review_feedback(
            frame, event, intent,
            {"now_ms": observed_at_ms, "simulated_approval": True}, policy,
        )
        records.append(_record(case, "pipeline", frame, event, reviewed))

        if case == "fresh_stable":
            # Fault injection reuses frame 3 and its event. It is not a new
            # capture and must not advance the temporal gate.
            wrong_run = dict(frame, run_id="old-run")
            blocked = reviewer.review_feedback(
                wrong_run, event, intent,
                {"now_ms": observed_at_ms, "simulated_approval": True}, policy,
            )
            records.append(_record("wrong_run_probe", "review_probe", wrong_run, event, blocked))

    return records


def main():
    for record in run_demo():
        print(json.dumps(record, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
