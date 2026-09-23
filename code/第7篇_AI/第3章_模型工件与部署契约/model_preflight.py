"""Offline metadata and SHA-256 preflight; never loads or runs a model."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


PLACEHOLDERS = {"", "not_selected", "not_pinned", "unknown", "not_applicable"}
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def _mapping(parent, key, path, errors):
    value = parent.get(key) if isinstance(parent, dict) else None
    if not isinstance(value, dict):
        errors.append("FIELD_NOT_OBJECT:" + path + "." + key)
        return {}
    return value


def _required_string(parent, key, path, errors):
    value = parent.get(key) if isinstance(parent, dict) else None
    field = path + "." + key
    if not isinstance(value, str):
        errors.append("MISSING_FIELD:" + field)
        return None
    if not value.strip():
        errors.append("EMPTY_FIELD:" + field)
        return None
    return value.strip()


def _validate_tensor_list(value, field, errors):
    if not isinstance(value, list) or not value:
        errors.append("INVALID_TENSOR_LIST:" + field)
        return
    for index, tensor in enumerate(value):
        item = field + "[" + str(index) + "]"
        if not isinstance(tensor, dict):
            errors.append("TENSOR_NOT_OBJECT:" + item)
            continue
        _required_string(tensor, "name", item, errors)
        _required_string(tensor, "dtype", item, errors)
        shape = tensor.get("shape")
        if not isinstance(shape, list):
            errors.append("MISSING_FIELD:" + item + ".shape")
            continue
        for dimension in shape:
            if type(dimension) is int and dimension >= 0:
                continue
            if isinstance(dimension, str) and dimension.strip():
                continue
            errors.append("INVALID_DIMENSION:" + item + ".shape")
            break


def _validate_manifest(manifest):
    errors = []
    if not isinstance(manifest, dict):
        return ["MANIFEST_ROOT_NOT_OBJECT"]
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        errors.append("SCHEMA_VERSION_UNSUPPORTED")

    model = _mapping(manifest, "model", "manifest", errors)
    model_format = None
    for key in ("name", "version", "format", "license_id"):
        value = _required_string(model, key, "model", errors)
        if key == "format":
            model_format = value
    artifact = _mapping(model, "artifact", "model", errors)
    _required_string(artifact, "path", "model.artifact", errors)
    digest = _required_string(artifact, "sha256", "model.artifact", errors)
    if digest and not SHA256_PATTERN.fullmatch(digest):
        errors.append("INVALID_SHA256:model.artifact.sha256")

    target = _mapping(manifest, "target", "manifest", errors)
    for key in ("board", "execution_plane", "software_release"):
        _required_string(target, key, "target", errors)

    runtime = _mapping(manifest, "runtime", "manifest", errors)
    for key in ("name", "version", "model_format", "execution_provider", "operator_set"):
        _required_string(runtime, key, "runtime", errors)
    runtime_format = runtime.get("model_format")
    if (
        isinstance(model_format, str)
        and isinstance(runtime_format, str)
        and model_format.strip().casefold() != runtime_format.strip().casefold()
    ):
        errors.append("MODEL_RUNTIME_FORMAT_MISMATCH")

    io_contract = _mapping(manifest, "io_contract", "manifest", errors)
    _validate_tensor_list(io_contract.get("inputs"), "io_contract.inputs", errors)
    outputs = io_contract.get("outputs")
    _validate_tensor_list(outputs, "io_contract.outputs", errors)
    labels = io_contract.get("output_labels")
    if (
        not isinstance(labels, list)
        or not labels
        or any(not isinstance(label, str) or not label.strip() for label in labels)
        or len(set(labels)) != len(labels)
    ):
        errors.append("INVALID_OUTPUT_LABELS:io_contract.output_labels")
    elif isinstance(outputs, list) and len(outputs) == 1 and isinstance(outputs[0], dict):
        shape = outputs[0].get("shape")
        if (
            isinstance(shape, list)
            and shape
            and type(shape[-1]) is int
            and shape[-1] != len(labels)
        ):
            errors.append("OUTPUT_LABEL_COUNT_MISMATCH")

    preprocessing = _mapping(manifest, "preprocessing", "manifest", errors)
    _required_string(preprocessing, "version", "preprocessing", errors)
    steps = preprocessing.get("steps")
    if not isinstance(steps, list) or not steps or any(
        not isinstance(step, str) or not step.strip() for step in steps
    ):
        errors.append("INVALID_PREPROCESSING_STEPS:preprocessing.steps")

    evaluation = _mapping(manifest, "evaluation", "manifest", errors)
    for key in ("protocol", "dataset_id", "report_id"):
        _required_string(evaluation, key, "evaluation", errors)

    budget = _mapping(manifest, "resource_budget", "manifest", errors)
    for key in ("peak_memory_bytes", "p95_latency_ms"):
        value = budget.get(key, "__missing__")
        if value == "__missing__":
            errors.append("MISSING_FIELD:resource_budget." + key)
        elif value is not None and (type(value) is not int or value <= 0):
            errors.append("INVALID_RESOURCE_VALUE:resource_budget." + key)

    return errors


def _resolve_artifact(manifest_path, relative_path):
    relative = Path(relative_path)
    if relative.is_absolute():
        return None, "ARTIFACT_PATH_MUST_BE_RELATIVE"
    try:
        root = manifest_path.resolve(strict=True).parent
        artifact = (root / relative).resolve(strict=True)
    except FileNotFoundError:
        return None, "ARTIFACT_NOT_FOUND"
    except (OSError, RuntimeError):
        return None, "ARTIFACT_PATH_UNREADABLE"
    try:
        artifact.relative_to(root)
    except ValueError:
        return None, "ARTIFACT_PATH_OUTSIDE_MANIFEST_DIR"
    if not artifact.is_file():
        return None, "ARTIFACT_NOT_A_FILE"
    return artifact, None


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for block in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _deployment_blockers(manifest):
    blockers = []
    model = manifest["model"]
    target = manifest["target"]
    runtime = manifest["runtime"]
    budget = manifest["resource_budget"]

    if model["format"].lower() == "teaching-fixture-text":
        blockers.append("TEACHING_FIXTURE_NOT_EXECUTABLE_MODEL")
    if any(runtime[key].strip().lower() in PLACEHOLDERS for key in ("name", "version")):
        blockers.append("RUNTIME_NOT_PINNED")
    if target["software_release"].strip().lower() in PLACEHOLDERS:
        blockers.append("TARGET_IMAGE_NOT_PINNED")
    if budget["peak_memory_bytes"] is None or budget["p95_latency_ms"] is None:
        blockers.append("RESOURCE_BUDGET_UNKNOWN")

    blockers.extend(
        [
            "TARGET_RUNTIME_COMPATIBILITY_UNVERIFIED",
            "TARGET_EXECUTION_EVIDENCE_MISSING",
            "MODEL_LICENSE_AND_PROVENANCE_REQUIRE_REVIEW",
            "EVALUATION_EVIDENCE_NOT_VERIFIED",
            "DEPLOYMENT_ACCEPTANCE_NOT_PROVEN",
        ]
    )
    return list(dict.fromkeys(blockers))


def inspect_manifest(manifest_path):
    path = Path(manifest_path)
    checks = {"manifest_schema": "NOT_RUN", "artifact_sha256": "NOT_RUN"}
    errors = []
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "decision": "BLOCKED",
            "checks": checks,
            "errors": ["MANIFEST_INVALID_JSON"],
            "blockers": [],
        }
    except (OSError, UnicodeDecodeError):
        return {
            "decision": "BLOCKED",
            "checks": checks,
            "errors": ["MANIFEST_UNREADABLE"],
            "blockers": [],
        }

    errors.extend(_validate_manifest(manifest))
    checks["manifest_schema"] = "FAIL" if errors else "PASS"
    if errors:
        return {"decision": "BLOCKED", "checks": checks, "errors": errors, "blockers": []}

    artifact, path_error = _resolve_artifact(path, manifest["model"]["artifact"]["path"])
    if path_error:
        checks["artifact_sha256"] = "FAIL"
        errors.append(path_error)
    else:
        try:
            actual_digest = _sha256(artifact)
        except OSError:
            checks["artifact_sha256"] = "FAIL"
            errors.append("ARTIFACT_READ_FAILED")
            return {"decision": "BLOCKED", "checks": checks, "errors": errors, "blockers": []}
        expected_digest = manifest["model"]["artifact"]["sha256"].lower()
        if actual_digest != expected_digest:
            checks["artifact_sha256"] = "FAIL"
            errors.append("ARTIFACT_SHA256_MISMATCH")
        else:
            checks["artifact_sha256"] = "PASS"

    if errors:
        return {"decision": "BLOCKED", "checks": checks, "errors": errors, "blockers": []}

    return {
        "decision": "REVIEW_REQUIRED_NOT_DEPLOYABLE",
        "checks": checks,
        "errors": [],
        "blockers": _deployment_blockers(manifest),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).with_name("model_manifest.json"),
        help="path to the JSON manifest (default: model_manifest.json beside this script)",
    )
    arguments = parser.parse_args(argv)
    report = inspect_manifest(arguments.manifest)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["decision"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
