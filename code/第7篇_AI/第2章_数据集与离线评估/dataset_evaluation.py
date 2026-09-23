"""Offline teaching example: grouped synthetic data and review-only metrics."""

import csv
import json
import math
from pathlib import Path


FIELDS = {"sample_id", "group_id", "split", "label", "color_fraction", "shape_score"}
SPLITS = ("train", "validation", "test")
LABELS = ("candidate_like", "other")


def _feature(row, name):
    value = row[name]
    if isinstance(value, bool):
        raise ValueError(f"invalid {name}")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"invalid {name}") from exc
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError(f"invalid {name}")
    return number


def audit_samples(rows):
    """Normalize CSV-like records and reject missing or leaked sample evidence."""
    group_splits = {}
    seen_ids = set()
    labels_by_split = {split: set() for split in SPLITS}
    normalized = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError("sample fields do not match schema")
        for name in ("sample_id", "group_id"):
            if not isinstance(row[name], str) or not row[name].strip():
                raise ValueError(f"invalid {name}")
        sample_id = row["sample_id"].strip()
        if sample_id in seen_ids:
            raise ValueError("duplicate sample_id")
        seen_ids.add(sample_id)
        group_id = row["group_id"].strip()
        split = row["split"]
        if split not in SPLITS:
            raise ValueError("invalid split")
        if row["label"] not in LABELS:
            raise ValueError("invalid label")
        if group_id in group_splits and group_splits[group_id] != split:
            raise ValueError("group appears in multiple splits")
        group_splits[group_id] = split
        labels_by_split[split].add(row["label"])
        normalized.append({
            "sample_id": sample_id,
            "group_id": group_id,
            "split": split,
            "label": row["label"],
            "color_fraction": _feature(row, "color_fraction"),
            "shape_score": _feature(row, "shape_score"),
        })
    if any(labels_by_split[split] != set(LABELS) for split in SPLITS):
        raise ValueError("each split needs both labels")
    return normalized


def fit_centroids(rows):
    """Fit class means using only rows explicitly assigned to training."""
    centroids = {}
    for label in LABELS:
        members = [row for row in rows if row["split"] == "train" and row["label"] == label]
        if not members:
            raise ValueError("training split needs both labels")
        centroids[label] = tuple(
            sum(row[name] for row in members) / len(members)
            for name in ("color_fraction", "shape_score")
        )
    return centroids


def score(features, centroids):
    """Squared distance to other minus squared distance to candidate; not a probability."""
    def squared_distance(center):
        return sum((value - target) ** 2 for value, target in zip(features, center))

    return squared_distance(centroids["other"]) - squared_distance(centroids["candidate_like"])


def classify(raw_score, threshold):
    """Return a label only when the raw score clears an absolute gate."""
    if abs(raw_score) < threshold:
        return None
    return "candidate_like" if raw_score >= 0 else "other"


def evaluate_rows(rows, centroids, threshold):
    """Count decisions and abstentions separately on already-audited rows."""
    counts = {
        "tp": 0, "fp": 0, "tn": 0, "fn": 0,
        "abstain_positive": 0, "abstain_negative": 0,
        "decided": 0, "total": 0,
    }
    samples = []
    for row in rows:
        features = (row["color_fraction"], row["shape_score"])
        raw_score = score(features, centroids)
        prediction = classify(raw_score, threshold)
        truth = row["label"]
        if prediction is None:
            key = "abstain_positive" if truth == "candidate_like" else "abstain_negative"
        elif prediction == "candidate_like":
            key = "tp" if truth == "candidate_like" else "fp"
        else:
            key = "fn" if truth == "candidate_like" else "tn"
        counts[key] += 1
        counts["total"] += 1
        if prediction is not None:
            counts["decided"] += 1
        samples.append({
            "sample_id": row["sample_id"], "truth": truth,
            "raw_score": round(raw_score, 6), "prediction": prediction,
        })

    def ratio(numerator, denominator):
        return numerator / denominator if denominator else None

    metrics = {
        "coverage": ratio(counts["decided"], counts["total"]),
        "precision_decided": ratio(counts["tp"], counts["tp"] + counts["fp"]),
        "recall_decided": ratio(counts["tp"], counts["tp"] + counts["fn"]),
        "accuracy_decided": ratio(counts["tp"] + counts["tn"], counts["decided"]),
    }
    return {"counts": counts, "metrics": metrics, "samples": samples}


def select_threshold(validation_rows, centroids):
    """Choose only on validation: zero observed FP, then maximum coverage."""
    if not validation_rows:
        raise ValueError("validation split is empty")
    trials = []
    eligible = []
    for threshold in (0.0, 0.12, 0.36):
        result = evaluate_rows(validation_rows, centroids, threshold)
        trials.append({"threshold": threshold, "counts": result["counts"]})
        if result["counts"]["fp"] == 0:
            eligible.append((result["counts"]["decided"], -threshold, threshold))
    if not eligible:
        raise ValueError("no validation gate yields zero false positives")
    return max(eligible)[2], trials


def load_csv(path):
    """Read local synthetic CSV records without touching devices or network."""
    with open(path, newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def run_experiment(rows):
    """Audit, fit on train, choose on validation, then evaluate untouched test."""
    records = audit_samples(rows)
    by_split = {split: [row for row in records if row["split"] == split] for split in SPLITS}
    centroids = fit_centroids(by_split["train"])
    threshold, trials = select_threshold(by_split["validation"], centroids)
    groups = {
        split: sorted({row["group_id"] for row in by_split[split]})
        for split in SPLITS
    }
    return {
        "source": "synthetic",
        "feature_schema": "vision-features-v1",
        "model_kind": "nearest-centroid-teaching-example",
        "dataset": {
            "total": len(records),
            "splits": {split: len(by_split[split]) for split in SPLITS},
            "groups": groups,
        },
        "centroids": centroids,
        "validation_trials": trials,
        "chosen_threshold": threshold,
        "validation": evaluate_rows(by_split["validation"], centroids, threshold),
        "test": evaluate_rows(by_split["test"], centroids, threshold),
        "disposition": "REPORT_ONLY",
    }


def main():
    data_path = Path(__file__).with_name("synthetic_samples.csv")
    report = run_experiment(load_csv(data_path))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False, indent=2))


if __name__ == "__main__":
    main()
