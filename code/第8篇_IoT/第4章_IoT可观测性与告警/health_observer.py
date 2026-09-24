"""Evaluate synthetic IoT health snapshots without connecting to devices."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from typing import Any


SCOPE = "LOCAL_SYNTHETIC_ONLY"
MAX_INPUT_BYTES = 64 * 1024
MAX_ROWS = 100
MAX_AGE_SECONDS = 90
MAX_PUBLISH_AGE_SECONDS = 300
MAX_OLDEST_EVENT_AGE_SECONDS = 600
QUEUE_PRESSURE_RATIO = 0.8
RETRY_WARNING_COUNT = 3
REQUIRED_FIELDS = {
    "device_id",
    "boot_id",
    "observed_at_utc",
    "last_publish_at_utc",
    "queue_depth",
    "queue_capacity",
    "oldest_event_age_seconds",
    "retries_5m",
    "rejected_5m",
}


def _utc_time(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z") or "T" not in value:
        raise ValueError(f"{field} must be a UTC ISO 8601 timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid UTC timestamp") from exc
    if parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def _nonempty_string(snapshot: dict[str, Any], field: str) -> str:
    value = snapshot.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _bounded_integer(
    snapshot: dict[str, Any], field: str, *, minimum: int, maximum: int
) -> int:
    value = snapshot.get(field)
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{field} must be an integer from {minimum} to {maximum}")
    return value


def _finding(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "level": "WARNING", "message": message, **details}


def _result(
    snapshot: dict[str, Any], health: str, action: str, findings: list[dict[str, Any]], **extra: Any
) -> dict[str, Any]:
    return {
        "scope": SCOPE,
        "device_id": snapshot["device_id"],
        "boot_id": snapshot["boot_id"],
        "health": health,
        "action": action,
        "findings": findings,
        **extra,
    }


def evaluate_snapshot(
    snapshot: object, *, now_utc: str, expected_device_id: str
) -> dict[str, Any]:
    """Validate and classify one snapshot against explicit, deterministic time."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a JSON object")
    missing = REQUIRED_FIELDS - snapshot.keys()
    extra = snapshot.keys() - REQUIRED_FIELDS
    if missing or extra:
        raise ValueError(f"snapshot fields mismatch; missing={sorted(missing)}, extra={sorted(extra)}")

    device_id = _nonempty_string(snapshot, "device_id")
    boot_id = _nonempty_string(snapshot, "boot_id")
    observed_at = _utc_time(snapshot["observed_at_utc"], "observed_at_utc")
    reference_time = _utc_time(now_utc, "now_utc")
    publish_value = snapshot["last_publish_at_utc"]
    last_publish_at = (
        None
        if publish_value is None
        else _utc_time(publish_value, "last_publish_at_utc")
    )

    queue_depth = _bounded_integer(snapshot, "queue_depth", minimum=0, maximum=1_000_000)
    queue_capacity = _bounded_integer(snapshot, "queue_capacity", minimum=1, maximum=1_000_000)
    oldest_age = _bounded_integer(
        snapshot, "oldest_event_age_seconds", minimum=0, maximum=31_536_000
    )
    retries = _bounded_integer(snapshot, "retries_5m", minimum=0, maximum=1_000_000)
    rejected = _bounded_integer(snapshot, "rejected_5m", minimum=0, maximum=1_000_000)
    if queue_depth > queue_capacity:
        raise ValueError("queue_depth cannot exceed queue_capacity")
    if queue_depth == 0 and oldest_age != 0:
        raise ValueError("oldest_event_age_seconds must be zero when queue_depth is zero")
    if queue_depth > 0 and oldest_age == 0:
        raise ValueError("oldest_event_age_seconds must be positive when the queue is non-empty")
    if last_publish_at is not None and last_publish_at > observed_at:
        return _result(
            snapshot,
            "UNKNOWN",
            "RECONCILE_TIME_AND_IDENTITY",
            [_finding("FUTURE_PUBLISH_TIME", "last publish time is later than the snapshot")],
        )

    if device_id != expected_device_id:
        return _result(
            snapshot,
            "UNKNOWN",
            "RECONCILE_TIME_AND_IDENTITY",
            [_finding("IDENTITY_MISMATCH", "snapshot does not match the expected device")],
        )

    age_seconds = (reference_time - observed_at).total_seconds()
    if age_seconds < 0:
        return _result(
            snapshot,
            "UNKNOWN",
            "RECONCILE_TIME_AND_IDENTITY",
            [_finding("FUTURE_SNAPSHOT", "snapshot time is later than the reference time")],
            snapshot_age_seconds=age_seconds,
        )
    if age_seconds > MAX_AGE_SECONDS:
        return _result(
            snapshot,
            "STALE",
            "VERIFY_COLLECTION_PATH",
            [_finding("SNAPSHOT_STALE", "health snapshot is older than the allowed window")],
            snapshot_age_seconds=age_seconds,
        )

    queue_ratio = queue_depth / queue_capacity
    publish_age = (
        None
        if last_publish_at is None
        else (reference_time - last_publish_at).total_seconds()
    )
    findings: list[dict[str, Any]] = []
    if queue_ratio >= QUEUE_PRESSURE_RATIO:
        findings.append(
            _finding(
                "QUEUE_PRESSURE",
                "queued events have reached the teaching pressure threshold",
                queue_utilization_ratio=round(queue_ratio, 3),
                threshold=QUEUE_PRESSURE_RATIO,
            )
        )
    if queue_depth > 0 and oldest_age > MAX_OLDEST_EVENT_AGE_SECONDS:
        findings.append(
            _finding(
                "OLDEST_EVENT_DELAYED",
                "oldest queued event age exceeded the teaching window",
                oldest_event_age_seconds=oldest_age,
                threshold_seconds=MAX_OLDEST_EVENT_AGE_SECONDS,
            )
        )
    if publish_age is None:
        findings.append(_finding("PUBLISH_NEVER_SEEN", "no successful publish time is recorded"))
    elif publish_age > MAX_PUBLISH_AGE_SECONDS:
        findings.append(
            _finding(
                "PUBLISH_STALE",
                "last successful publish is older than the teaching window",
                publish_age_seconds=publish_age,
                threshold_seconds=MAX_PUBLISH_AGE_SECONDS,
            )
        )
    if retries >= RETRY_WARNING_COUNT:
        findings.append(
            _finding(
                "RETRIES_ELEVATED",
                "retry attempts in the five-minute window reached the teaching threshold",
                retries_5m=retries,
                threshold=RETRY_WARNING_COUNT,
            )
        )
    if rejected > 0:
        findings.append(
            _finding(
                "EVENTS_REJECTED",
                "one or more events were rejected in the five-minute window",
                rejected_5m=rejected,
            )
        )

    health = "DEGRADED" if findings else "HEALTHY"
    action = "INVESTIGATE_AND_PRESERVE_QUEUE" if findings else "CONTINUE_MONITORING"
    return _result(
        snapshot,
        health,
        action,
        findings,
        snapshot_age_seconds=age_seconds,
        queue_utilization_ratio=round(queue_ratio, 3),
        oldest_event_age_seconds=oldest_age,
        publish_age_seconds=publish_age,
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_jsonl(text: str) -> list[dict[str, Any]]:
    """Load a bounded JSONL document and reject ambiguous duplicate keys."""
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) > MAX_ROWS:
        raise ValueError(f"input exceeds maximum row count ({MAX_ROWS})")
    rows = []
    for number, line in enumerate(lines, start=1):
        try:
            item = json.loads(line, object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"line {number}: {exc}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"line {number}: each row must be a JSON object")
        rows.append(item)
    if not rows:
        raise ValueError("input must contain at least one JSON object")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshots", required=True, type=Path)
    parser.add_argument("--expected-device-id", required=True)
    parser.add_argument("--now-utc", required=True, help="fixed UTC reference time ending in Z")
    args = parser.parse_args()
    try:
        if args.snapshots.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
        rows = load_jsonl(args.snapshots.read_text(encoding="utf-8"))
        reports = [
            evaluate_snapshot(
                row,
                now_utc=args.now_utc,
                expected_device_id=args.expected_device_id,
            )
            for row in rows
        ]
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"INPUT_ERROR: {exc}", file=sys.stderr)
        return 2
    for report in reports:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
