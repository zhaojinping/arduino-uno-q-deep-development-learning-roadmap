"""Report-only validation for a submitted AI-readiness evidence manifest."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


MAX_MANIFEST_BYTES = 16 * 1024
GATE_KEYS = (
    "task_definition",
    "dataset_evaluation",
    "model_artifact",
    "inference_regression",
    "performance_budget",
    "quantization_evaluation",
    "tool_call_safety",
    "target_acceptance",
)
_ALLOWED_STATUSES = frozenset(
    {"CLAIMED_PASS", "BLOCKED", "NOT_RUN", "REVIEW_REQUIRED"}
)
_REPORT_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,47}\Z")
_EVIDENCE_REFERENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}\Z")


class ManifestParseError(ValueError):
    """Raised when raw manifest bytes cannot be safely parsed as JSON."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class _DuplicateJSONKeyError(ValueError):
    pass


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJSONKeyError
        result[key] = value
    return result


def _reject_non_json_constant(_value: str) -> None:
    raise ValueError("non-standard JSON constant")


def parse_manifest_json(raw: object) -> object:
    """Parse bounded UTF-8 JSON while rejecting duplicate keys and NaN values."""
    if type(raw) is not bytes:
        raise ManifestParseError("INPUT_NOT_BYTES")
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ManifestParseError("MANIFEST_TOO_LARGE")
    try:
        source = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise ManifestParseError("INVALID_UTF8") from None

    try:
        return json.loads(
            source,
            object_pairs_hook=_object_without_duplicate_keys,
            parse_constant=_reject_non_json_constant,
        )
    except _DuplicateJSONKeyError:
        raise ManifestParseError("DUPLICATE_JSON_KEY") from None
    except (json.JSONDecodeError, ValueError, RecursionError):
        raise ManifestParseError("INVALID_JSON") from None


def _empty_counts() -> dict[str, int]:
    return {
        "claimed_pass": 0,
        "blocked": 0,
        "not_run": 0,
        "review_required": 0,
    }


def _invalid_report(reason: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "report_id": None,
        "scope": "REPORT_ONLY",
        "decision": "INVALID_MANIFEST",
        "reason": reason,
        "deployment_authorized": False,
        "evidence_independently_verified": False,
        "counts": _empty_counts(),
        "gates": [],
    }


def evaluate_manifest(manifest: object) -> dict[str, Any]:
    """Validate manifest shape and summarize claims without authorizing release."""
    if type(manifest) is not dict:
        return _invalid_report("ROOT_NOT_OBJECT")
    if set(manifest) != {"schema_version", "report_id", "gates"}:
        return _invalid_report("ROOT_FIELDS_MISMATCH")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        return _invalid_report("UNSUPPORTED_SCHEMA_VERSION")

    report_id = manifest["report_id"]
    if type(report_id) is not str or _REPORT_ID.fullmatch(report_id) is None:
        return _invalid_report("INVALID_REPORT_ID")

    gates = manifest["gates"]
    if type(gates) is not dict or set(gates) != set(GATE_KEYS):
        return _invalid_report("GATE_SET_MISMATCH")

    counts = _empty_counts()
    gate_results: list[dict[str, str | None]] = []
    status_count_key = {
        "CLAIMED_PASS": "claimed_pass",
        "BLOCKED": "blocked",
        "NOT_RUN": "not_run",
        "REVIEW_REQUIRED": "review_required",
    }

    for gate in GATE_KEYS:
        record = gates[gate]
        if type(record) is not dict or set(record) != {"status", "reference"}:
            return _invalid_report("INVALID_GATE_RECORD")
        status = record["status"]
        reference = record["reference"]
        if type(status) is not str or status not in _ALLOWED_STATUSES:
            return _invalid_report("INVALID_GATE_STATUS")
        if status == "NOT_RUN":
            if reference is not None:
                return _invalid_report("INVALID_EVIDENCE_REFERENCE")
        elif type(reference) is not str or _EVIDENCE_REFERENCE.fullmatch(reference) is None:
            return _invalid_report("INVALID_EVIDENCE_REFERENCE")

        counts[status_count_key[status]] += 1
        gate_results.append(
            {"gate": gate, "status": status, "reference": reference}
        )

    if counts["blocked"]:
        decision = "BLOCKED"
    elif counts["not_run"] or counts["review_required"]:
        decision = "INCOMPLETE"
    else:
        decision = "READY_FOR_HUMAN_REVIEW"

    return {
        "schema_version": 1,
        "report_id": report_id,
        "scope": "REPORT_ONLY",
        "decision": decision,
        "reason": None,
        "deployment_authorized": False,
        "evidence_independently_verified": False,
        "counts": counts,
        "gates": gate_results,
    }


def main() -> int:
    """Read the bundled synthetic manifest and print one JSON report."""
    sample = Path(__file__).with_name("evidence_manifest.json")
    try:
        manifest = parse_manifest_json(sample.read_bytes())
    except OSError:
        report = _invalid_report("SAMPLE_UNAVAILABLE")
        exit_code = 2
    except ManifestParseError as error:
        report = _invalid_report(error.code)
        exit_code = 2
    else:
        report = evaluate_manifest(manifest)
        exit_code = 0 if report["decision"] != "INVALID_MANIFEST" else 2

    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
