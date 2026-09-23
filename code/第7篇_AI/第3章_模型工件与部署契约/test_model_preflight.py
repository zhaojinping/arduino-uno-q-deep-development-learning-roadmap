"""Behavioral tests for the offline model-manifest preflight CLI."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("model_preflight.py")
TEACHING_ARTIFACT = b"TEACHING FIXTURE ONLY - NOT AN EXECUTABLE MODEL.\n"


def valid_manifest(artifact_path, artifact_bytes=TEACHING_ARTIFACT):
    return {
        "schema_version": 1,
        "model": {
            "name": "synthetic-two-class-demo",
            "version": "0.1.0",
            "format": "teaching-fixture-text",
            "artifact": {
                "path": artifact_path,
                "sha256": hashlib.sha256(artifact_bytes).hexdigest(),
            },
            "license_id": "NO_MODEL_WEIGHTS_INCLUDED",
        },
        "target": {
            "board": "Arduino UNO Q",
            "execution_plane": "linux_mpu",
            "software_release": "not_pinned",
        },
        "runtime": {
            "name": "not_selected",
            "version": "not_pinned",
            "model_format": "teaching-fixture-text",
            "execution_provider": "not_selected",
            "operator_set": "not_applicable",
        },
        "io_contract": {
            "inputs": [
                {"name": "features", "dtype": "float32", "shape": ["batch", 2]}
            ],
            "outputs": [
                {"name": "scores", "dtype": "float32", "shape": ["batch", 2]}
            ],
            "output_labels": ["candidate_like", "other"],
        },
        "preprocessing": {
            "version": "features-v1",
            "steps": ["two precomputed synthetic features; no image preprocessing"],
        },
        "evaluation": {
            "protocol": "chapter-7-chapter-2-synthetic-example",
            "dataset_id": "synthetic_samples.csv",
            "report_id": "REPORT_ONLY",
        },
        "resource_budget": {"peak_memory_bytes": None, "p95_latency_ms": None},
    }


class ModelPreflightCliTests(unittest.TestCase):
    def run_cli(self, manifest_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--manifest", str(manifest_path)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result, json.loads(result.stdout)

    @staticmethod
    def write_manifest(path, manifest):
        path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_valid_teaching_fixture_never_claims_deployability(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "teaching-artifact.txt"
            artifact.write_bytes(TEACHING_ARTIFACT)
            manifest_path = root / "model_manifest.json"
            self.write_manifest(manifest_path, valid_manifest(artifact.name))

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["decision"], "REVIEW_REQUIRED_NOT_DEPLOYABLE")
        self.assertEqual(report["checks"]["manifest_schema"], "PASS")
        self.assertEqual(report["checks"]["artifact_sha256"], "PASS")
        self.assertIn("TEACHING_FIXTURE_NOT_EXECUTABLE_MODEL", report["blockers"])
        self.assertIn("TARGET_RUNTIME_COMPATIBILITY_UNVERIFIED", report["blockers"])

    def test_declared_runtime_does_not_substitute_for_target_execution_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "candidate.onnx"
            artifact.write_bytes(TEACHING_ARTIFACT)
            manifest = valid_manifest(artifact.name)
            manifest["model"]["format"] = "onnx"
            manifest["runtime"].update(
                {
                    "name": "onnxruntime",
                    "version": "1.20.0",
                    "model_format": "onnx",
                    "execution_provider": "CPUExecutionProvider",
                    "operator_set": "ai.onnx:21",
                }
            )
            manifest["target"]["software_release"] = "Debian-release-pinned-by-example"
            manifest_path = root / "model_manifest.json"
            self.write_manifest(manifest_path, manifest)

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["decision"], "REVIEW_REQUIRED_NOT_DEPLOYABLE")
        self.assertIn("TARGET_RUNTIME_COMPATIBILITY_UNVERIFIED", report["blockers"])

    def test_hash_mismatch_blocks_preflight(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "teaching-artifact.txt"
            artifact.write_bytes(TEACHING_ARTIFACT + b"tampered\n")
            manifest = valid_manifest(artifact.name)
            manifest_path = root / "model_manifest.json"
            self.write_manifest(manifest_path, manifest)

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertEqual(report["checks"]["artifact_sha256"], "FAIL")
        self.assertIn("ARTIFACT_SHA256_MISMATCH", report["errors"])

    def test_model_format_must_match_declared_runtime_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "teaching-artifact.txt"
            artifact.write_bytes(TEACHING_ARTIFACT)
            manifest = valid_manifest(artifact.name)
            manifest["model"]["format"] = "onnx"
            manifest["runtime"]["model_format"] = "tflite"
            manifest_path = root / "model_manifest.json"
            self.write_manifest(manifest_path, manifest)

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertIn("MODEL_RUNTIME_FORMAT_MISMATCH", report["errors"])

    def test_static_output_shape_must_match_label_count(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "teaching-artifact.txt"
            artifact.write_bytes(TEACHING_ARTIFACT)
            manifest = valid_manifest(artifact.name)
            manifest["io_contract"]["output_labels"] = ["candidate_like"]
            manifest_path = root / "model_manifest.json"
            self.write_manifest(manifest_path, manifest)

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertIn("OUTPUT_LABEL_COUNT_MISMATCH", report["errors"])

    def test_zero_length_tensor_dimension_is_metadata_not_runtime_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "teaching-artifact.txt"
            artifact.write_bytes(TEACHING_ARTIFACT)
            manifest = valid_manifest(artifact.name)
            manifest["io_contract"]["inputs"][0]["shape"] = [0, 2]
            manifest_path = root / "model_manifest.json"
            self.write_manifest(manifest_path, manifest)

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["checks"]["manifest_schema"], "PASS")
        self.assertEqual(report["decision"], "REVIEW_REQUIRED_NOT_DEPLOYABLE")

    def test_scalar_tensor_uses_empty_shape(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "teaching-artifact.txt"
            artifact.write_bytes(TEACHING_ARTIFACT)
            manifest = valid_manifest(artifact.name)
            manifest["io_contract"]["inputs"][0]["shape"] = []
            manifest_path = root / "model_manifest.json"
            self.write_manifest(manifest_path, manifest)

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["checks"]["manifest_schema"], "PASS")
        self.assertEqual(report["decision"], "REVIEW_REQUIRED_NOT_DEPLOYABLE")

    def test_artifact_path_cannot_escape_manifest_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_dir = root / "chapter"
            manifest_dir.mkdir()
            (root / "outside.bin").write_bytes(TEACHING_ARTIFACT)
            manifest_path = manifest_dir / "model_manifest.json"
            self.write_manifest(manifest_path, valid_manifest("../outside.bin"))

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertIn("ARTIFACT_PATH_OUTSIDE_MANIFEST_DIR", report["errors"])

    def test_missing_tensor_shape_blocks_preflight(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = root / "teaching-artifact.txt"
            artifact.write_bytes(TEACHING_ARTIFACT)
            manifest = valid_manifest(artifact.name)
            del manifest["io_contract"]["inputs"][0]["shape"]
            manifest_path = root / "model_manifest.json"
            self.write_manifest(manifest_path, manifest)

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertIn("MISSING_FIELD:io_contract.inputs[0].shape", report["errors"])

    def test_invalid_json_is_reported_as_blocked_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "model_manifest.json"
            manifest_path.write_text('{"schema_version":', encoding="utf-8")

            result, report = self.run_cli(manifest_path)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertIn("MANIFEST_INVALID_JSON", report["errors"])
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
