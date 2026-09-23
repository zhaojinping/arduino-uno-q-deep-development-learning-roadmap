"""Compare offline reference and candidate inference outputs for review only."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


TOP_LEVEL_FIELDS = {
    "schema_version", "atol", "rtol", "min_margin", "reference", "candidate"
}
RECORD_FIELDS = {"sample_id", "preprocess_id", "labels", "scores"}


def _nonempty_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"invalid {name}")
    return value


def _finite_nonnegative(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"invalid {name}")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"invalid {name}") from exc
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"invalid {name}")
    return number


def _finite_score(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("invalid score")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError("invalid score") from exc
    if not math.isfinite(number):
        raise ValueError("invalid score")
    return number


def _validate_records(records: Any, side: str) -> dict[str, dict[str, Any]]:
    if not isinstance(records, list) or not records:
        raise ValueError(f"{side} must be a non-empty list")

    by_id = {}
    for record in records:
        if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
            raise ValueError(f"invalid {side} record fields")
        sample_id = _nonempty_text(record["sample_id"], "sample_id")
        if sample_id in by_id:
            raise ValueError("duplicate sample_id")
        preprocess_id = _nonempty_text(record["preprocess_id"], "preprocess_id")

        labels = record["labels"]
        if (not isinstance(labels, list) or len(labels) < 2
                or any(not isinstance(label, str) or not label.strip()
                       or label != label.strip() for label in labels)
                or len(set(labels)) != len(labels)):
            raise ValueError("invalid labels")

        raw_scores = record["scores"]
        if not isinstance(raw_scores, list) or len(raw_scores) != len(labels):
            raise ValueError("score count must match labels")
        scores = [_finite_score(score) for score in raw_scores]
        by_id[sample_id] = {
            "preprocess_id": preprocess_id,
            "labels": list(labels),
            "scores": scores,
        }
    return by_id


def _prediction(labels: list[str], scores: list[float], min_margin: float):
    winner_index = max(range(len(scores)), key=scores.__getitem__)
    ranked = sorted(scores, reverse=True)
    margin = ranked[0] - ranked[1]
    if not math.isfinite(margin):
        raise ValueError("non-finite score margin")
    label = labels[winner_index] if margin > min_margin else None
    return labels[winner_index], label, margin


def compare_payload(payload: Any) -> dict[str, Any]:
    """Validate and compare two sets of paired class scores without running a model."""
    if not isinstance(payload, dict) or set(payload) != TOP_LEVEL_FIELDS:
        raise ValueError("input fields do not match schema")
    version = payload["schema_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        raise ValueError("unsupported schema_version")

    atol = _finite_nonnegative(payload["atol"], "atol")
    rtol = _finite_nonnegative(payload["rtol"], "rtol")
    min_margin = _finite_nonnegative(payload["min_margin"], "min_margin")
    reference = _validate_records(payload["reference"], "reference")
    candidate = _validate_records(payload["candidate"], "candidate")
    if set(reference) != set(candidate):
        raise ValueError("sample_id sets differ")

    sample_results = []
    compared_values = 0
    values_over_tolerance = 0
    max_absolute_error = 0.0
    argmax_changed_samples = 0
    decision_changed_samples = 0
    reference_abstentions = 0
    candidate_abstentions = 0

    for sample_id in sorted(reference):
        expected = reference[sample_id]
        actual = candidate[sample_id]
        if expected["preprocess_id"] != actual["preprocess_id"]:
            raise ValueError(f"preprocess_id differs for sample_id {sample_id}")
        if expected["labels"] != actual["labels"]:
            raise ValueError(f"labels differ for sample_id {sample_id}")

        sample_error_count = 0
        sample_max_error = 0.0
        for expected_score, actual_score in zip(expected["scores"], actual["scores"]):
            error = abs(actual_score - expected_score)
            if not math.isfinite(error):
                raise ValueError("non-finite score difference")
            tolerance = atol + rtol * abs(expected_score)
            if not math.isfinite(tolerance):
                raise ValueError("non-finite tolerance")
            compared_values += 1
            sample_max_error = max(sample_max_error, error)
            max_absolute_error = max(max_absolute_error, error)
            if error > tolerance:
                sample_error_count += 1
                values_over_tolerance += 1

        reference_argmax, reference_decision, reference_margin = _prediction(
            expected["labels"], expected["scores"], min_margin
        )
        candidate_argmax, candidate_decision, candidate_margin = _prediction(
            actual["labels"], actual["scores"], min_margin
        )
        argmax_changed = reference_argmax != candidate_argmax
        decision_changed = reference_decision != candidate_decision
        argmax_changed_samples += int(argmax_changed)
        decision_changed_samples += int(decision_changed)
        reference_abstentions += int(reference_decision is None)
        candidate_abstentions += int(candidate_decision is None)
        sample_results.append({
            "sample_id": sample_id,
            "values_over_tolerance": sample_error_count,
            "max_absolute_error": round(sample_max_error, 12),
            "reference_argmax": reference_argmax,
            "candidate_argmax": candidate_argmax,
            "argmax_changed": argmax_changed,
            "reference_decision": reference_decision,
            "candidate_decision": candidate_decision,
            "decision_changed": decision_changed,
            "reference_margin": round(reference_margin, 12),
            "candidate_margin": round(candidate_margin, 12),
        })

    requires_review = bool(
        values_over_tolerance or argmax_changed_samples or decision_changed_samples
    )
    return {
        "schema_version": 1,
        "decision": "REVIEW_REQUIRED" if requires_review else "MATCH_WITHIN_TOLERANCE",
        "report_only": True,
        "tolerance": {"atol": atol, "rtol": rtol, "min_margin": min_margin},
        "summary": {
            "sample_count": len(sample_results),
            "compared_values": compared_values,
            "values_over_tolerance": values_over_tolerance,
            "max_absolute_error": round(max_absolute_error, 12),
            "argmax_changed_samples": argmax_changed_samples,
            "decision_changed_samples": decision_changed_samples,
            "reference_abstentions": reference_abstentions,
            "candidate_abstentions": candidate_abstentions,
        },
        "samples": sample_results,
        "limitations": [
            "Scores are compared only; no model, preprocessing pipeline, or runtime is executed.",
            "Matching sample and preprocessing identifiers do not prove identical tensor inputs.",
            "MATCH_WITHIN_TOLERANCE is not target compatibility or deployment acceptance.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON file with reference and candidate outputs")
    args = parser.parse_args(argv)

    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = compare_payload(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        report = {
            "schema_version": 1,
            "decision": "BLOCKED",
            "report_only": True,
            "errors": [str(exc)],
        }
        exit_code = 1
    else:
        exit_code = 0

    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
