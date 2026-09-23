"""Analyze a declared inference benchmark record without running a model."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class BenchmarkInputError(ValueError):
    """Raised when a benchmark record violates the teaching schema."""


_RUN_KEYS = frozenset(
    {
        "schema_version",
        "run_id",
        "environment",
        "warmup_count",
        "measured_count",
        "samples",
    }
)
_ENVIRONMENT_KEYS = frozenset(
    {
        "platform_id",
        "os_image_id",
        "runtime_id",
        "execution_provider_id",
        "artifact_id",
        "input_shape",
        "batch_size",
        "thread_count",
    }
)
_SAMPLE_KEYS = frozenset({"index", "phase", "latency_ms", "rss_mib"})


def _object_with_exact_keys(value: object, expected: frozenset[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise BenchmarkInputError(f"{where} must be a JSON object")
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected fields: {', '.join(extra)}")
        raise BenchmarkInputError(f"{where}: {'; '.join(details)}")
    return value


def _nonempty_string(value: object, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BenchmarkInputError(f"{where} must be a non-empty string")
    return value


def _integer(value: object, where: str, *, allow_zero: bool = False) -> int:
    if type(value) is not int or value < (0 if allow_zero else 1):
        qualifier = "non-negative" if allow_zero else "positive"
        raise BenchmarkInputError(f"{where} must be a {qualifier} integer")
    return value


def _finite_number(value: object, where: str, *, strictly_positive: bool) -> float:
    if type(value) not in (int, float):
        raise BenchmarkInputError(f"{where} must be a finite number, not a boolean or other type")
    try:
        finite = math.isfinite(value)
        number = float(value)
    except OverflowError as exc:
        raise BenchmarkInputError(f"{where} must be a finite number") from exc
    if not finite or (strictly_positive and number <= 0):
        condition = "finite and greater than zero" if strictly_positive else "finite"
        raise BenchmarkInputError(f"{where} must be {condition}")
    return number


def percentile_nearest_rank(values: Sequence[float], percentile: float) -> float:
    """Return the nearest-rank quantile for a fractional percentile in (0, 1]."""
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence) or not values:
        raise BenchmarkInputError("values must be a non-empty sequence of finite numbers")
    if type(percentile) not in (int, float):
        raise BenchmarkInputError("percentile must be a finite number in (0, 1]")
    try:
        valid_percentile = math.isfinite(percentile) and 0 < percentile <= 1
    except OverflowError:
        valid_percentile = False
    if not valid_percentile:
        raise BenchmarkInputError("percentile must be a finite number in (0, 1]")

    ordered = sorted(
        _finite_number(value, f"values[{index}]", strictly_positive=False)
        for index, value in enumerate(values)
    )
    rank = math.ceil(float(percentile) * len(ordered))
    return ordered[rank - 1]


def _validate_run(run: Mapping[str, object]) -> tuple[str, dict[str, object], int, int, list[dict[str, object]]]:
    record = _object_with_exact_keys(run, _RUN_KEYS, "run")
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise BenchmarkInputError("schema_version must be integer 1")
    run_id = _nonempty_string(record["run_id"], "run_id")

    raw_environment = _object_with_exact_keys(record["environment"], _ENVIRONMENT_KEYS, "environment")
    environment: dict[str, object] = {
        key: _nonempty_string(raw_environment[key], f"environment.{key}")
        for key in (
            "platform_id",
            "os_image_id",
            "runtime_id",
            "execution_provider_id",
            "artifact_id",
        )
    }
    input_shape = raw_environment["input_shape"]
    if not isinstance(input_shape, list) or not input_shape:
        raise BenchmarkInputError("environment.input_shape must be a non-empty array of positive integers")
    environment["input_shape"] = [
        _integer(dimension, f"environment.input_shape[{index}]")
        for index, dimension in enumerate(input_shape)
    ]
    environment["batch_size"] = _integer(raw_environment["batch_size"], "environment.batch_size")
    environment["thread_count"] = _integer(raw_environment["thread_count"], "environment.thread_count")

    warmup_count = _integer(record["warmup_count"], "warmup_count", allow_zero=True)
    measured_count = _integer(record["measured_count"], "measured_count")
    raw_samples = record["samples"]
    if not isinstance(raw_samples, list):
        raise BenchmarkInputError("samples must be a JSON array")
    if len(raw_samples) != warmup_count + measured_count:
        raise BenchmarkInputError("sample row count must equal warmup_count + measured_count")

    samples: list[dict[str, object]] = []
    for offset, raw_sample in enumerate(raw_samples, start=1):
        sample = _object_with_exact_keys(raw_sample, _SAMPLE_KEYS, f"samples[{offset - 1}]")
        if _integer(sample["index"], f"samples[{offset - 1}].index") != offset:
            raise BenchmarkInputError("sample indices must be contiguous and one-based")
        expected_phase = "warmup" if offset <= warmup_count else "measured"
        if sample["phase"] != expected_phase:
            raise BenchmarkInputError(
                f"samples[{offset - 1}].phase must be {expected_phase!r} at this position"
            )
        samples.append(
            {
                "index": offset,
                "phase": expected_phase,
                "latency_ms": _finite_number(
                    sample["latency_ms"], f"samples[{offset - 1}].latency_ms", strictly_positive=True
                ),
                "rss_mib": _finite_number(
                    sample["rss_mib"], f"samples[{offset - 1}].rss_mib", strictly_positive=True
                ),
            }
        )
    return run_id, environment, warmup_count, measured_count, samples


def analyze_run(run: Mapping[str, object]) -> dict[str, object]:
    """Validate one run record and return descriptive, threshold-free statistics."""
    run_id, environment, warmup_count, measured_count, samples = _validate_run(run)
    measured_samples = [sample for sample in samples if sample["phase"] == "measured"]
    latencies = [float(sample["latency_ms"]) for sample in measured_samples]
    rss_values = [float(sample["rss_mib"]) for sample in measured_samples]
    latency_scale = max(latencies)
    mean_latency = latency_scale * statistics.fmean(value / latency_scale for value in latencies)

    return {
        "schema_version": 1,
        "run_id": run_id,
        "status": "REPORT_ONLY",
        "report_only": True,
        "thresholds_applied": False,
        "environment": environment,
        "warmup_count": warmup_count,
        "measured_count": measured_count,
        "latency_ms": {
            "quantile_method": "nearest_rank",
            "p50_nearest_rank": percentile_nearest_rank(latencies, 0.50),
            "p95_nearest_rank": percentile_nearest_rank(latencies, 0.95),
            "mean": mean_latency,
            "max": max(latencies),
        },
        "memory_mib": {
            "measurement": "maximum of supplied measured-sample RSS observations; not a guaranteed process peak",
            "observed_max_rss": max(rss_values),
        },
    }


def load_run(path: Path) -> dict[str, object]:
    """Read a JSON run without modifying it, converting file/JSON errors to input errors."""
    try:
        with path.open("r", encoding="utf-8") as input_file:
            value = json.load(input_file)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BenchmarkInputError(f"cannot read valid UTF-8 JSON input: {exc}") from exc
    if not isinstance(value, dict):
        raise BenchmarkInputError("input root must be a JSON object")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON benchmark run record")
    arguments = parser.parse_args(argv)
    try:
        report = analyze_run(load_run(arguments.input))
    except BenchmarkInputError as exc:
        print(json.dumps({"status": "BLOCKED", "errors": [str(exc)]}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
