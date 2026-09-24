"""Validate a bounded synthetic IoT telemetry payload without networking."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any


MAX_PAYLOAD_BYTES = 4096
_FIELDS = frozenset(
    {
        "schema_version",
        "device_id",
        "boot_id",
        "sequence",
        "event_time",
        "metric",
        "value",
        "unit",
        "quality",
    }
)
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
_METRIC = re.compile(r"[a-z][a-z0-9_]{0,47}\Z")
_UNIT = re.compile(r"[A-Za-z0-9][A-Za-z0-9%/._-]{0,23}\Z")
_RFC3339_PROFILE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?"
    r"(?:Z|[+-][0-9]{2}:[0-9]{2})\Z"
)
_QUALITY = frozenset({"GOOD", "UNCERTAIN", "BAD"})


class _DuplicateKeyError(ValueError):
    pass


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError
        result[key] = value
    return result


def _reject_non_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def _report(result: str, reason: str | None, event_key: str | None) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "scope": "OFFLINE_SCHEMA_ONLY",
        "result": result,
        "reason": reason,
        "event_key": event_key,
    }


def _valid_event_time(value: object) -> bool:
    if type(value) is not str or _RFC3339_PROFILE.fullmatch(value) is None:
        return False
    if value.endswith("-00:00"):
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _parse_payload(raw: bytes) -> object:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise ValueError("INVALID_UTF8") from None

    try:
        return json.loads(
            text,
            object_pairs_hook=_object_without_duplicate_keys,
            parse_constant=_reject_non_json_constant,
        )
    except _DuplicateKeyError:
        raise ValueError("DUPLICATE_JSON_KEY") from None
    except (json.JSONDecodeError, RecursionError, ValueError):
        raise ValueError("INVALID_JSON") from None


def validate_payload(raw: object) -> dict[str, Any]:
    """Return a schema-only decision for one UTF-8 JSON payload."""
    if type(raw) is not bytes:
        return _report("INVALID", "INPUT_NOT_BYTES", None)
    if len(raw) > MAX_PAYLOAD_BYTES:
        return _report("INVALID", "PAYLOAD_TOO_LARGE", None)
    try:
        payload = _parse_payload(raw)
    except ValueError as error:
        return _report("INVALID", str(error), None)

    if type(payload) is not dict:
        return _report("INVALID", "INVALID_ROOT", None)
    if set(payload) != _FIELDS:
        return _report("INVALID", "FIELDS_MISMATCH", None)
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        return _report("INVALID", "UNSUPPORTED_SCHEMA_VERSION", None)

    device_id = payload["device_id"]
    boot_id = payload["boot_id"]
    if (
        type(device_id) is not str
        or _IDENTIFIER.fullmatch(device_id) is None
        or type(boot_id) is not str
        or _IDENTIFIER.fullmatch(boot_id) is None
    ):
        return _report("INVALID", "INVALID_IDENTITY", None)

    sequence = payload["sequence"]
    if type(sequence) is not int or sequence < 0:
        return _report("INVALID", "INVALID_SEQUENCE", None)
    if not _valid_event_time(payload["event_time"]):
        return _report("INVALID", "INVALID_EVENT_TIME", None)

    metric = payload["metric"]
    unit = payload["unit"]
    quality = payload["quality"]
    value = payload["value"]
    valid_number = type(value) is int or (
        type(value) is float and math.isfinite(value)
    )
    if (
        type(metric) is not str
        or _METRIC.fullmatch(metric) is None
        or type(unit) is not str
        or _UNIT.fullmatch(unit) is None
        or type(quality) is not str
        or quality not in _QUALITY
    ):
        return _report("INVALID", "INVALID_READING", None)
    if not valid_number:
        return _report("INVALID", "INVALID_VALUE", None)

    event_key = f"{device_id}/{boot_id}/{sequence}"
    return _report("VALID", None, event_key)


def main() -> int:
    """Validate the bundled synthetic payload and print a JSON report."""
    sample_path = Path(__file__).with_name("telemetry_sample.json")
    try:
        raw = sample_path.read_bytes()
    except OSError:
        report = _report("INVALID", "SAMPLE_UNAVAILABLE", None)
        exit_code = 2
    else:
        report = validate_payload(raw)
        exit_code = 0 if report["result"] == "VALID" else 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
