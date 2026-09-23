"""TDD contract for the local App descriptor validation model."""
from __future__ import annotations

import unittest

from deployment_contract import validate_manifest


class DeploymentContractTests(unittest.TestCase):
    def test_valid_manifest_normalizes_ports_and_bricks(self) -> None:
        report = validate_manifest(
            {
                "name": "Smart Garden",
                "ports": [5000],
                "bricks": [
                    {"arduino:dbstorage": {"variables": {"DB_PASSWORD": "${DB_PASSWORD}"}}},
                    {"arduino:objectdetection": {"model": "yolo-v8", "devices": ["remote_camera_0"]}},
                ],
            }
        )

        self.assertTrue(report.valid)
        self.assertEqual(report.ports, (5000,))
        self.assertEqual(
            report.brick_ids,
            ("arduino:dbstorage", "arduino:objectdetection"),
        )
        self.assertEqual(report.issues, ())

    def test_port_must_be_an_integer_in_range(self) -> None:
        report = validate_manifest({"ports": [0, True, 70000]})

        self.assertFalse(report.valid)
        self.assertEqual(
            [issue.code for issue in report.issues],
            ["PORT_INVALID", "PORT_INVALID", "PORT_INVALID"],
        )

    def test_duplicate_ports_are_rejected(self) -> None:
        report = validate_manifest({"ports": [5000, 5000]})

        self.assertFalse(report.valid)
        self.assertEqual([issue.code for issue in report.issues], ["PORT_DUPLICATE"])

    def test_brick_variables_and_devices_have_declared_types(self) -> None:
        report = validate_manifest(
            {
                "bricks": [
                    {
                        "arduino:camera": {
                            "variables": {"MODE": 1},
                            "devices": ["camera_0", 2],
                        }
                    }
                ]
            }
        )

        self.assertFalse(report.valid)
        self.assertEqual(
            [issue.code for issue in report.issues],
            ["VARIABLE_VALUE_INVALID", "DEVICE_INVALID"],
        )

    def test_brick_options_are_checked_without_guessing_secret_values(self) -> None:
        report = validate_manifest(
            {
                "bricks": [
                    {"arduino:dbstorage": {"variables": {"PASSWORD": "literal"}}},
                    {"arduino:vision": {"unknown": "value"}},
                ]
            }
        )

        self.assertFalse(report.valid)
        self.assertEqual([issue.code for issue in report.issues], ["BRICK_OPTION_UNKNOWN"])


if __name__ == "__main__":
    unittest.main()
