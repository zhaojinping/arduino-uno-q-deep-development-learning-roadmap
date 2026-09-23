"""Executable contract for the App Lab project-layout lesson."""
from __future__ import annotations

import unittest

from app_contract import AppContractError, validate_layout


class AppContractTests(unittest.TestCase):
    def test_python_only_app_has_required_manifest_and_entrypoint(self) -> None:
        result = validate_layout(
            {"name": "Demo", "description": "Local contract"},
            {"app.yaml", "python/main.py", "README.md", "data/state.json"},
        )

        self.assertEqual(result.mode, "PYTHON_ONLY")
        self.assertEqual(result.required, ("app.yaml", "python/main.py"))
        self.assertEqual(result.optional, ())

    def test_app_with_sketch_requires_both_sketch_files(self) -> None:
        result = validate_layout(
            {"name": "Demo", "bricks": ["arduino:web_ui"]},
            {"app.yaml", "python/main.py", "sketch/sketch.ino", "sketch/sketch.yaml"},
        )

        self.assertEqual(result.mode, "PYTHON_AND_SKETCH")
        self.assertEqual(result.optional, ("sketch/sketch.ino", "sketch/sketch.yaml"))

    def test_partial_sketch_fails_closed(self) -> None:
        with self.assertRaisesRegex(AppContractError, "sketch/sketch.yaml"):
            validate_layout(
                {"name": "Demo"},
                {"app.yaml", "python/main.py", "sketch/sketch.ino"},
            )

    def test_missing_python_entrypoint_fails_closed(self) -> None:
        with self.assertRaisesRegex(AppContractError, "python/main.py"):
            validate_layout({"name": "Demo"}, {"app.yaml"})

    def test_ports_and_bricks_are_checked_without_parsing_yaml(self) -> None:
        with self.assertRaisesRegex(AppContractError, "ports"):
            validate_layout({"name": "Demo", "ports": [0]}, {"app.yaml", "python/main.py"})

        with self.assertRaisesRegex(AppContractError, "bricks"):
            validate_layout({"name": "Demo", "bricks": [3]}, {"app.yaml", "python/main.py"})

    def test_reserved_directories_do_not_change_app_mode(self) -> None:
        result = validate_layout(
            {"name": "Demo"},
            {"app.yaml", "python/main.py", "data/cache.db", ".cache/venv"},
        )

        self.assertEqual(result.mode, "PYTHON_ONLY")


if __name__ == "__main__":
    unittest.main()
