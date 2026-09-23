"""Correlate normalized App Lab events with a redacted run snapshot."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
import sys

SEVERITIES = {"DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


def _load_object(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _required_text(record: dict[str, object], key: str, label: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}.{key} must be a non-empty string")
    return value


def _validate_utc(value: object, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}.ts_utc must be a non-empty timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{label}.ts_utc must be ISO-8601") from exc
    if parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{label}.ts_utc must be normalized to UTC")


def load_metadata(path: Path) -> dict[str, str]:
    record = _load_object(path, "metadata")
    run_id = _required_text(record, "run_id", "metadata")
    fingerprint = _required_text(record, "config_fingerprint", "metadata")
    if SHA256_RE.fullmatch(fingerprint) is None:
        raise ValueError("metadata.config_fingerprint must be a 64-character lowercase SHA-256")
    return {"run_id": run_id, "config_fingerprint": fingerprint}


def load_events(path: Path) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        label = f"events line {line_number}"
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{label} is not valid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{label} must be a JSON object")
        event_id = _required_text(value, "event_id", label)
        if event_id in seen_ids:
            raise ValueError(f"duplicate event_id: {event_id}")
        seen_ids.add(event_id)
        _validate_utc(value.get("ts_utc"), label)
        _required_text(value, "source", label)
        _required_text(value, "event", label)
        severity = _required_text(value, "severity", label)
        if severity not in SEVERITIES:
            raise ValueError(f"{label}.severity is not supported")
        if "run_id" in value:
            _required_text(value, "run_id", label)
        if "config_fingerprint" in value:
            fingerprint = _required_text(value, "config_fingerprint", label)
            if SHA256_RE.fullmatch(fingerprint) is None:
                raise ValueError(f"{label}.config_fingerprint must be a 64-character lowercase SHA-256")
        events.append(value)
    return events


def correlate(
    events: list[dict[str, object]], metadata: dict[str, str]
) -> dict[str, object]:
    counts: Counter[str] = Counter()
    sources: set[str] = set()
    has_ready_event = False
    run_id = metadata["run_id"]
    expected_fingerprint = metadata["config_fingerprint"]

    for event in events:
        event_run_id = event.get("run_id")
        if event_run_id is None:
            counts["uncorrelated"] += 1
            continue
        if event_run_id != run_id:
            counts["stale"] += 1
            continue
        event_fingerprint = event.get("config_fingerprint")
        if event_fingerprint is not None and event_fingerprint != expected_fingerprint:
            counts["fingerprint_conflict"] += 1
            continue

        counts["correlated"] += 1
        if event_fingerprint is None:
            counts["fingerprint_missing"] += 1
        source = event["source"]
        assert isinstance(source, str)
        sources.add(source)
        severity = event["severity"]
        if severity in {"ERROR", "CRITICAL"}:
            counts["errors"] += 1
        elif severity == "WARN":
            counts["warnings"] += 1
        if event["event"] == "app.ready":
            has_ready_event = True

    if counts["errors"]:
        verdict = "RUNTIME_ERROR"
    elif counts["fingerprint_conflict"]:
        verdict = "EVIDENCE_CONFLICT"
    elif has_ready_event:
        verdict = "RUNNING_NO_ERROR_OBSERVED"
    else:
        verdict = "INCOMPLETE_EVIDENCE"

    return {
        "total": len(events),
        "correlated": counts["correlated"],
        "stale": counts["stale"],
        "uncorrelated": counts["uncorrelated"],
        "fingerprint_conflict": counts["fingerprint_conflict"],
        "fingerprint_missing": counts["fingerprint_missing"],
        "errors": counts["errors"],
        "warnings": counts["warnings"],
        "sources": sorted(sources),
        "verdict": verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    args = parser.parse_args()
    try:
        metadata = load_metadata(args.metadata)
        events = load_events(args.events)
        summary = correlate(events, metadata)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        f"SIMULATED run_id={metadata['run_id']} total={summary['total']} "
        f"correlated={summary['correlated']} stale={summary['stale']} "
        f"uncorrelated={summary['uncorrelated']} "
        f"fingerprint_conflict={summary['fingerprint_conflict']}"
    )
    source_text = ",".join(summary["sources"]) or "none"
    print(
        f"SIMULATED verdict={summary['verdict']} errors={summary['errors']} "
        f"warnings={summary['warnings']} sources={source_text}"
    )
    print(f"SIMULATED fingerprint_missing={summary['fingerprint_missing']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
