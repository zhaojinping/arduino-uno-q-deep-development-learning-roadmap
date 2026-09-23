"""TDD contract for deterministic environment configuration layering."""
from __future__ import annotations

import unittest

from config_layers import merge_layers


SCHEMA = {
    "APP_MODE": str,
    "LOG_LEVEL": str,
    "TARGET_BOARD": str,
    "PORT": int,
}


class ConfigLayerTests(unittest.TestCase):
    def test_precedence_is_base_then_environment_then_runtime(self) -> None:
        result = merge_layers(
            "staging",
            (
                ("base", {"APP_MODE": "production", "LOG_LEVEL": "info", "TARGET_BOARD": "test-q"}),
                ("environment", {"APP_MODE": "staging", "LOG_LEVEL": "debug"}),
                ("runtime", {"LOG_LEVEL": "trace"}),
            ),
            schema=SCHEMA,
            required=("APP_MODE", "TARGET_BOARD"),
            allowed_environments=("development", "staging", "production"),
        )

        self.assertTrue(result.valid)
        self.assertEqual(
            result.as_dict(),
            {"APP_MODE": "staging", "LOG_LEVEL": "trace", "TARGET_BOARD": "test-q"},
        )
        self.assertEqual(result.overridden_keys, ("APP_MODE", "LOG_LEVEL"))
        self.assertEqual(dict(result.sources)["LOG_LEVEL"], "runtime")

    def test_unknown_key_and_wrong_type_are_reported(self) -> None:
        result = merge_layers(
            "staging",
            (("environment", {"APP_MODE": 1, "EXTRA": "not-in-schema"}),),
            schema=SCHEMA,
        )

        self.assertFalse(result.valid)
        self.assertEqual(
            [issue.code for issue in result.issues],
            ["TYPE_MISMATCH", "UNKNOWN_KEY"],
        )

    def test_missing_required_and_unknown_environment_are_distinct(self) -> None:
        result = merge_layers(
            "qa",
            (("base", {}),),
            schema=SCHEMA,
            required=("APP_MODE",),
            allowed_environments=("development", "staging", "production"),
        )

        self.assertFalse(result.valid)
        self.assertEqual(
            [issue.code for issue in result.issues],
            ["UNKNOWN_ENVIRONMENT", "MISSING_REQUIRED"],
        )

    def test_locked_key_cannot_be_overridden_by_a_later_layer(self) -> None:
        result = merge_layers(
            "staging",
            (
                ("base", {"TARGET_BOARD": "test-q"}),
                ("runtime", {"TARGET_BOARD": "现场-q"}),
            ),
            schema=SCHEMA,
            locked_keys=("TARGET_BOARD",),
        )

        self.assertFalse(result.valid)
        self.assertEqual(result.as_dict()["TARGET_BOARD"], "test-q")
        self.assertEqual([issue.code for issue in result.issues], ["LOCKED_OVERRIDE"])

    def test_non_mapping_layer_is_rejected(self) -> None:
        result = merge_layers(
            "staging",
            (("environment", ["invalid"]),),  # type: ignore[arg-type]
            schema=SCHEMA,
        )

        self.assertFalse(result.valid)
        self.assertEqual([issue.code for issue in result.issues], ["LAYER_NOT_MAPPING"])


if __name__ == "__main__":
    unittest.main()
