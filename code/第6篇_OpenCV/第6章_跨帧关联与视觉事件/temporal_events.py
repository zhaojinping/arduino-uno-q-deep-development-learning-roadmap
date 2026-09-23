"""A synthetic, fail-closed temporal gate for Chapter 6.

This example consumes already extracted pixel candidates. It does not open a
camera, run OpenCV, infer real-world identity, or command a board.
"""

import math


def _finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


class TemporalGate:
    """Apply strict source, order, time and displacement gates to one candidate stream."""

    def __init__(self, expected_source, min_hits, max_step_px, max_gap_ms):
        if not isinstance(expected_source, str) or not expected_source.strip():
            raise ValueError("expected_source must be a nonempty string")
        if not isinstance(min_hits, int) or isinstance(min_hits, bool) or min_hits < 2:
            raise ValueError("min_hits must be an integer of at least 2")
        if not _finite_number(max_step_px) or max_step_px <= 0:
            raise ValueError("max_step_px must be finite and positive")
        if not isinstance(max_gap_ms, int) or isinstance(max_gap_ms, bool) or max_gap_ms <= 0:
            raise ValueError("max_gap_ms must be a positive integer")
        self.expected_source = expected_source
        self.min_hits = min_hits
        self.max_step_px = max_step_px
        self.max_gap_ms = max_gap_ms
        self._last_frame_id = None
        self._last_timestamp_ms = None
        self._clear_track()

    def _clear_track(self):
        self._hits = 0
        self._centroid = None

    def _result(self, status, frame_id):
        return {
            "status": status,
            "frame_id": frame_id,
            "hits": self._hits,
            "centroid": self._centroid,
        }

    def _validate(self, sample):
        if not isinstance(sample, dict):
            raise ValueError("sample must be a dictionary")
        if sample.get("source") != self.expected_source:
            raise ValueError("sample source differs from expected_source")
        frame_id = sample.get("frame_id")
        timestamp_ms = sample.get("timestamp_ms")
        if not isinstance(frame_id, int) or isinstance(frame_id, bool) or frame_id < 1:
            raise ValueError("frame_id must be a positive integer")
        if not isinstance(timestamp_ms, int) or isinstance(timestamp_ms, bool) or timestamp_ms < 0:
            raise ValueError("timestamp_ms must be a nonnegative integer")
        if "candidate" not in sample:
            raise ValueError("candidate field is required")
        candidate = sample["candidate"]
        if candidate is None:
            return frame_id, timestamp_ms, None
        if not isinstance(candidate, dict):
            raise ValueError("candidate must be a dictionary or None")
        centroid = candidate.get("centroid")
        if not isinstance(centroid, (tuple, list)) or len(centroid) != 2:
            raise ValueError("centroid must have two pixel coordinates")
        if not all(_finite_number(value) and value >= 0 for value in centroid):
            raise ValueError("centroid coordinates must be finite and nonnegative")
        area = candidate.get("area")
        if not _finite_number(area) or area <= 0:
            raise ValueError("candidate area must be finite and positive")
        return frame_id, timestamp_ms, tuple(centroid)

    def process(self, sample):
        """Return a state event. Any discontinuity clears reusable position."""
        try:
            frame_id, timestamp_ms, centroid = self._validate(sample)
        except ValueError:
            self._clear_track()
            raise

        if self._last_frame_id is not None:
            if frame_id <= self._last_frame_id or timestamp_ms <= self._last_timestamp_ms:
                self._clear_track()
                return self._result("REJECTED_ORDER", frame_id)
            if frame_id != self._last_frame_id + 1 or timestamp_ms - self._last_timestamp_ms > self.max_gap_ms:
                self._last_frame_id = frame_id
                self._last_timestamp_ms = timestamp_ms
                self._clear_track()
                return self._result("REJECTED_GAP", frame_id)

        self._last_frame_id = frame_id
        self._last_timestamp_ms = timestamp_ms
        if centroid is None:
            status = "LOST" if self._hits >= self.min_hits else "NO_CANDIDATE"
            self._clear_track()
            return self._result(status, frame_id)
        if self._centroid is not None and math.hypot(
            centroid[0] - self._centroid[0], centroid[1] - self._centroid[1]
        ) > self.max_step_px:
            self._clear_track()
            return self._result("REJECTED_JUMP", frame_id)
        self._hits += 1
        self._centroid = centroid
        if self._hits < self.min_hits:
            status = "TENTATIVE"
        elif self._hits == self.min_hits:
            status = "STABLE"
        else:
            status = "CONTINUING"
        return self._result(status, frame_id)


def _demo_frame(frame_id, timestamp_ms, xy):
    return {
        "source": "synthetic",
        "frame_id": frame_id,
        "timestamp_ms": timestamp_ms,
        "candidate": None if xy is None else {"centroid": xy, "area": 100.0},
    }


def main():
    gate = TemporalGate("synthetic", min_hits=3, max_step_px=10.0, max_gap_ms=100)
    samples = (
        _demo_frame(1, 0, (10.0, 10.0)),
        _demo_frame(2, 40, (13.0, 14.0)),
        _demo_frame(3, 80, (16.0, 18.0)),
        _demo_frame(4, 120, None),
        _demo_frame(5, 160, (100.0, 100.0)),
        _demo_frame(6, 200, (101.0, 101.0)),
        _demo_frame(7, 240, (102.0, 102.0)),
        _demo_frame(8, 280, (140.0, 140.0)),
    )
    for sample in samples:
        result = gate.process(sample)
        print(
            f"frame={sample['frame_id']} timestamp_ms={sample['timestamp_ms']} "
            f"status={result['status']} hits={result['hits']} "
            f"centroid={result['centroid']}"
        )


if __name__ == "__main__":
    main()
