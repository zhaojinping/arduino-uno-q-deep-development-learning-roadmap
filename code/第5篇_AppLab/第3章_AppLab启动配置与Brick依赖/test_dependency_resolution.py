"""TDD contract for resolving App dependencies against a local snapshot."""
from __future__ import annotations

import unittest

from dependency_resolution import (
    BrickCapability,
    BrickRequirement,
    resolve_deployability,
)


class DependencyResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.requirements = (
            BrickRequirement("arduino:objectdetection", "yolo-v8", ("remote_camera_0",)),
        )
        self.capabilities = {
            "arduino:objectdetection": BrickCapability(
                "arduino:objectdetection", ("yolo-v8",), ("remote_camera_0",)
            )
        }

    def test_ready_requires_brick_model_device_and_free_port(self) -> None:
        decision = resolve_deployability(
            self.requirements,
            self.capabilities,
            requested_ports=(5000,),
            occupied_ports={},
        )

        self.assertEqual(decision.action, "READY")
        self.assertEqual(decision.missing, ())
        self.assertEqual(decision.conflicts, ())

    def test_missing_brick_is_reported(self) -> None:
        decision = resolve_deployability(
            self.requirements,
            {},
            requested_ports=(),
            occupied_ports={},
        )

        self.assertEqual(decision.action, "MISSING_BRICK")
        self.assertEqual(decision.missing, ("arduino:objectdetection",))

    def test_missing_model_is_reported(self) -> None:
        capabilities = {
            "arduino:objectdetection": BrickCapability(
                "arduino:objectdetection", ("yolo-v7",), ("remote_camera_0",)
            )
        }

        decision = resolve_deployability(
            self.requirements, capabilities, requested_ports=(), occupied_ports={}
        )

        self.assertEqual(decision.action, "MISSING_MODEL")
        self.assertEqual(decision.missing, ("arduino:objectdetection:model:yolo-v8",))

    def test_missing_device_is_reported(self) -> None:
        capabilities = {
            "arduino:objectdetection": BrickCapability(
                "arduino:objectdetection", ("yolo-v8",), ()
            )
        }

        decision = resolve_deployability(
            self.requirements, capabilities, requested_ports=(), occupied_ports={}
        )

        self.assertEqual(decision.action, "MISSING_DEVICE")
        self.assertEqual(
            decision.missing,
            ("arduino:objectdetection:device:remote_camera_0",),
        )

    def test_port_conflict_is_reported(self) -> None:
        decision = resolve_deployability(
            self.requirements,
            self.capabilities,
            requested_ports=(5000,),
            occupied_ports={5000: "existing-service"},
        )

        self.assertEqual(decision.action, "CONFLICTING_PORT")
        self.assertEqual(decision.conflicts, (5000,))

    def test_unknown_is_used_when_inventory_is_unavailable(self) -> None:
        decision = resolve_deployability(
            self.requirements,
            None,
            requested_ports=(5000,),
            occupied_ports=None,
        )

        self.assertEqual(decision.action, "UNKNOWN")
        self.assertIn("Brick", decision.reason)


if __name__ == "__main__":
    unittest.main()
