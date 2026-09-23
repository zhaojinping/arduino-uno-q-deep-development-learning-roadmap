"""Review a synthetic visual event without sending any hardware request.

The returned preview is documentation data, not an RPC payload. A real system
needs separate authentication, duplicate suppression, MCU-side guards and
physical acceptance tests.
"""

import math


def _integer(value, minimum=0):
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _point(value):
    return (
        isinstance(value, (tuple, list))
        and len(value) == 2
        and all(_number(coordinate) and coordinate >= 0 for coordinate in value)
    )


def _validate_policy(policy):
    if not isinstance(policy, dict):
        raise ValueError("policy must be a dictionary")
    if not isinstance(policy.get("source"), str) or not policy["source"].strip():
        raise ValueError("policy source must be nonempty")
    if not isinstance(policy.get("run_id"), str) or not policy["run_id"].strip():
        raise ValueError("policy run_id must be nonempty")
    if not _integer(policy.get("max_age_ms"), 1):
        raise ValueError("max_age_ms must be a positive integer")
    roi = policy.get("roi")
    if (
        not isinstance(roi, (tuple, list))
        or len(roi) != 4
        or not all(_integer(value) for value in roi)
        or roi[2] < 1
        or roi[3] < 1
    ):
        raise ValueError("roi must be (x, y, positive width, positive height)")
    if not _integer(policy.get("max_level")) or policy["max_level"] > 100:
        raise ValueError("max_level must be an integer from 0 to 100")


def _blocked(reason):
    return {"decision": "BLOCKED", "reason": reason, "preview": None}


def review_feedback(frame, event, intent, context, policy):
    """Return PREVIEW_ONLY or BLOCKED. No camera, Bridge or MCU access occurs."""
    _validate_policy(policy)
    if not all(isinstance(value, dict) for value in (frame, event, intent, context)):
        return _blocked("malformed_record")

    source = frame.get("source")
    run_id = frame.get("run_id")
    frame_id = frame.get("frame_id")
    timestamp_ms = frame.get("timestamp_ms")
    now_ms = context.get("now_ms")
    if (
        not isinstance(source, str)
        or not isinstance(run_id, str)
        or not _integer(frame_id, 1)
        or not _integer(timestamp_ms)
        or not _integer(now_ms)
    ):
        return _blocked("malformed_record")
    if source != policy["source"] or run_id != policy["run_id"]:
        return _blocked("source_or_session_mismatch")

    if event.get("status") not in ("STABLE", "CONTINUING") or not _integer(event.get("hits"), 3):
        return _blocked("event_not_stable")
    candidate = frame.get("candidate")
    if candidate is None:
        return _blocked("event_frame_mismatch")
    if (
        not isinstance(candidate, dict)
        or not _point(candidate.get("centroid"))
        or not _point(event.get("centroid"))
        or not _number(candidate.get("area"))
        or candidate["area"] <= 0
        or not _integer(event.get("frame_id"), 1)
    ):
        return _blocked("malformed_record")
    if (
        event["frame_id"] != frame_id
        or tuple(event["centroid"]) != tuple(candidate["centroid"])
    ):
        return _blocked("event_frame_mismatch")

    age_ms = now_ms - timestamp_ms
    if age_ms < 0 or age_ms > policy["max_age_ms"]:
        return _blocked("stale_or_future_frame")
    x, y = event["centroid"]
    left, top, width, height = policy["roi"]
    if not (left <= x < left + width and top <= y < top + height):
        return _blocked("outside_roi")
    if (
        intent.get("kind") != "indicator"
        or not _integer(intent.get("level"))
        or intent["level"] > policy["max_level"]
    ):
        return _blocked("intent_out_of_bounds")
    if context.get("simulated_approval") is not True:
        return _blocked("approval_missing")

    return {
        "decision": "PREVIEW_ONLY",
        "reason": "requires_separate_hardware_review",
        "preview": {
            "kind": "indicator",
            "level": intent["level"],
            "run_id": run_id,
            "frame_id": frame_id,
        },
    }


def main():
    frame = {
        "source": "synthetic",
        "run_id": "demo-001",
        "frame_id": 3,
        "timestamp_ms": 80,
        "candidate": {"centroid": (16.0, 18.0), "area": 100.0},
    }
    event = {"status": "STABLE", "frame_id": 3, "hits": 3, "centroid": (16.0, 18.0)}
    intent = {"kind": "indicator", "level": 12}
    policy = {
        "source": "synthetic",
        "run_id": "demo-001",
        "max_age_ms": 100,
        "roi": (0, 0, 160, 128),
        "max_level": 20,
    }
    examples = (
        ("fresh", {"now_ms": 100, "simulated_approval": True}),
        ("stale", {"now_ms": 181, "simulated_approval": True}),
        ("unapproved", {"now_ms": 100, "simulated_approval": False}),
    )
    for name, context in examples:
        result = review_feedback(frame, event, intent, context, policy)
        print(
            f"case={name} decision={result['decision']} "
            f"reason={result['reason']} preview={result['preview']}"
        )


if __name__ == "__main__":
    main()
