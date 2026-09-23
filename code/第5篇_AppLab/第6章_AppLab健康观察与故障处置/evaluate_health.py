"""Evaluate a teaching-only App health snapshot; never control hardware."""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys


def nonempty_string(obj, key):
    if not isinstance(obj, dict):
        raise ValueError("expected a JSON object")
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def utc_time(value):
    if not isinstance(value, str) or not value.endswith("Z") or "T" not in value:
        raise ValueError("timestamps must be UTC ISO 8601 strings ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"invalid UTC timestamp: {value}") from exc
    if parsed.utcoffset() != timedelta(0):
        raise ValueError("timestamp is not UTC")
    return parsed.astimezone(timezone.utc)


def check_names(snapshot, key):
    names = snapshot.get(key)
    if not isinstance(names, list) or any(
        not isinstance(name, str) or not name.strip() for name in names
    ):
        raise ValueError(f"{key} must be a list of non-empty names")
    if len(set(names)) != len(names):
        raise ValueError(f"{key} contains duplicate names")
    return set(names)


def evaluate(snapshot):
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a JSON object")
    if snapshot.get("evidence_kind") != "SIMULATED":
        raise ValueError("this teaching script accepts SIMULATED inputs only")
    run_id = nonempty_string(snapshot, "run_id")
    fingerprint = nonempty_string(snapshot, "config_fingerprint")
    if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        raise ValueError("config_fingerprint must be 64 lowercase hex digits")
    observed_at = utc_time(snapshot.get("observed_at_utc"))
    max_age = snapshot.get("max_age_seconds")
    if type(max_age) is not int or max_age <= 0:
        raise ValueError("max_age_seconds must be a positive integer")
    required = check_names(snapshot, "required_checks")
    optional = check_names(snapshot, "optional_checks")
    if not required or required & optional:
        raise ValueError("required_checks must be non-empty and disjoint")
    expected = required | optional
    observations = snapshot.get("observations")
    if not isinstance(observations, list):
        raise ValueError("observations must be a list")

    checks = {}
    for item in observations:
        name = nonempty_string(item, "name")
        if name not in expected or name in checks:
            raise ValueError(f"unexpected or duplicate check: {name}")
        status = nonempty_string(item, "status")
        if status not in {"PASS", "FAIL", "UNKNOWN"}:
            raise ValueError(f"invalid status for {name}")
        nonempty_string(item, "evidence_ref")
        check_run = nonempty_string(item, "run_id")
        check_fingerprint = nonempty_string(item, "config_fingerprint")
        when = utc_time(item.get("ts_utc"))

        if check_run != run_id or check_fingerprint != fingerprint:
            result = "UNKNOWN_IDENTITY"
        elif when > observed_at:
            result = "UNKNOWN_FUTURE"
        elif observed_at - when > timedelta(seconds=max_age):
            result = "UNKNOWN_STALE"
        else:
            result = status
        checks[name] = result

    for name in expected - checks.keys():
        checks[name] = "UNKNOWN_MISSING"

    if any(checks[name] == "FAIL" for name in required):
        health, action = "FAULT_OBSERVED", "HOLD_AND_DIAGNOSE"
    elif any(checks[name] != "PASS" for name in required):
        health, action = "UNKNOWN", "HOLD_AND_RECONCILE"
    elif any(checks[name] != "PASS" for name in optional):
        health, action = "DEGRADED", "REVIEW_DEGRADED_MODE"
    else:
        health, action = "HEALTHY_OBSERVED", "CONTINUE_MONITORING"

    return {
        "scope": "LOCAL_MODEL",
        "run_id": run_id,
        "health": health,
        "action": action,
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = evaluate(snapshot)
    except (OSError, ValueError) as exc:
        print(f"INPUT_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
