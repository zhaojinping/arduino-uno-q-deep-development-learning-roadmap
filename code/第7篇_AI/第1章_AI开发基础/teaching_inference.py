"""A hand-set, offline linear scoring example; not a trained or validated model."""

import json
import math


IDENTITY_FIELDS = (
    "source", "run_id", "sample_id", "feature_schema", "timestamp_ms", "observed_at_ms"
)


def _metadata(sample):
    record = sample if isinstance(sample, dict) else {}
    return {key: record.get(key) for key in IDENTITY_FIELDS}


def _valid_text(value):
    return isinstance(value, str) and bool(value.strip())


def _valid_time(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _valid_feature(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0 <= value <= 1
        and math.isfinite(value)
    )


def _reject(reason, sample):
    return {
        **_metadata(sample),
        "decision": "REJECTED",
        "reason": reason,
        "evaluated": False,
        "label": None,
        "margin": None,
        "model_id": "hand-set-linear-v1",
    }


def evaluate(sample):
    if (
        not isinstance(sample, dict)
        or not all(_valid_text(sample.get(key)) for key in ("source", "run_id", "sample_id", "feature_schema"))
        or not all(_valid_time(sample.get(key)) for key in ("timestamp_ms", "observed_at_ms"))
    ):
        return _reject("malformed_sample", sample)
    if sample["source"] != "synthetic" or sample["run_id"] != "ai-demo-001":
        return _reject("source_or_session_mismatch", sample)
    if sample["feature_schema"] != "vision-features-v1":
        return _reject("feature_schema_mismatch", sample)
    age_ms = sample["observed_at_ms"] - sample["timestamp_ms"]
    if age_ms < 0 or age_ms > 100:
        return _reject("stale_or_future_sample", sample)
    features = sample.get("features")
    if (
        not isinstance(features, dict)
        or set(features) != {"color_fraction", "shape_score"}
        or not all(_valid_feature(value) for value in features.values())
    ):
        return _reject("invalid_features", sample)
    margin = 2.0 * features["color_fraction"] + features["shape_score"] - 1.5
    uncertain = abs(margin) < 0.5
    return {
        **_metadata(sample),
        "decision": "ABSTAIN" if uncertain else "REPORT_ONLY",
        "label": None if uncertain else ("candidate_like" if margin >= 0 else "other"),
        "margin": round(margin, 6),
        "evaluated": True,
        "model_id": "hand-set-linear-v1",
        "reason": "insufficient_margin" if uncertain else "teaching_weights_unvalidated",
    }


def run_demo():
    """Return six synthetic, reproducible review records; no I/O occurs."""
    examples = (
        ("clear_candidate", {"color_fraction": 0.8, "shape_score": 0.8}, {}),
        ("clear_other", {"color_fraction": 0.1, "shape_score": 0.1}, {}),
        ("borderline", {"color_fraction": 0.5, "shape_score": 0.5}, {}),
        ("stale", {"color_fraction": 0.8, "shape_score": 0.8}, {"observed_at_ms": 250}),
        ("wrong_run", {"color_fraction": 0.8, "shape_score": 0.8}, {"run_id": "old-run"}),
        ("invalid_feature", {"color_fraction": None, "shape_score": 0.8}, {}),
    )
    records = []
    for name, features, changes in examples:
        sample = {
            "source": "synthetic",
            "run_id": "ai-demo-001",
            "sample_id": name,
            "feature_schema": "vision-features-v1",
            "timestamp_ms": 100,
            "observed_at_ms": 120,
            "features": features,
        }
        sample.update(changes)
        records.append({"case": name, **evaluate(sample)})
    return records


def main():
    for record in run_demo():
        print(json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
