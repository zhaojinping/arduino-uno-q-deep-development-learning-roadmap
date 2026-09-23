"""Resolve App Brick and port requirements against a supplied local snapshot."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class BrickRequirement:
    """One normalized requirement declared by an App."""

    brick_id: str
    model: str | None = None
    devices: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrickCapability:
    """A local, externally supplied capability snapshot for one Brick."""

    brick_id: str
    models: tuple[str, ...] = ()
    devices: tuple[str, ...] = ()


@dataclass(frozen=True)
class DeployabilityDecision:
    """Offline deployability result; it is not a device deployment receipt."""

    action: str
    reason: str
    missing: tuple[str, ...] = ()
    conflicts: tuple[int, ...] = ()


def _unknown(capabilities: object, occupied_ports: object) -> DeployabilityDecision:
    missing_sources: list[str] = []
    if capabilities is None:
        missing_sources.append("Brick inventory is unavailable")
    if occupied_ports is None:
        missing_sources.append("port inventory is unavailable")
    return DeployabilityDecision("UNKNOWN", "; ".join(missing_sources))


def resolve_deployability(
    requirements: tuple[BrickRequirement, ...],
    capabilities: Mapping[str, BrickCapability] | None,
    requested_ports: tuple[int, ...],
    occupied_ports: Mapping[int, str] | None,
) -> DeployabilityDecision:
    """Compare declared requirements with a caller-provided local snapshot.

    ``None`` deliberately means that the relevant inventory is unknown. An empty
    mapping means the inventory was observed and contains no matching item.
    """
    if capabilities is None or occupied_ports is None:
        return _unknown(capabilities, occupied_ports)

    missing_bricks: list[str] = []
    missing_models: list[str] = []
    missing_devices: list[str] = []
    for requirement in requirements:
        capability = capabilities.get(requirement.brick_id)
        if capability is None:
            missing_bricks.append(requirement.brick_id)
            continue
        if requirement.model and requirement.model not in capability.models:
            missing_models.append(f"{requirement.brick_id}:model:{requirement.model}")
        for device in requirement.devices:
            if device not in capability.devices:
                missing_devices.append(f"{requirement.brick_id}:device:{device}")

    conflicts = tuple(sorted({port for port in requested_ports if port in occupied_ports}))
    missing = tuple(missing_bricks + missing_models + missing_devices)
    if missing_bricks:
        action = "MISSING_BRICK"
        reason = "one or more declared Bricks are absent from the snapshot"
    elif missing_models:
        action = "MISSING_MODEL"
        reason = "one or more requested models are absent from the Brick snapshot"
    elif missing_devices:
        action = "MISSING_DEVICE"
        reason = "one or more requested devices are absent from the Brick snapshot"
    elif conflicts:
        action = "CONFLICTING_PORT"
        reason = "one or more requested ports are occupied"
    elif missing or conflicts:
        action = "NOT_READY"
        reason = "the supplied snapshot does not satisfy all requirements"
    else:
        action = "READY"
        reason = "all declared Bricks, models, devices and ports are available"
    return DeployabilityDecision(action, reason, missing, conflicts)


def _demonstrate() -> None:
    requirements = (
        BrickRequirement("arduino:objectdetection", "yolo-v8", ("remote_camera_0",)),
    )
    capabilities = {
        "arduino:objectdetection": BrickCapability(
            "arduino:objectdetection", ("yolo-v8",), ("remote_camera_0",)
        )
    }
    ready = resolve_deployability(requirements, capabilities, (5000,), {})
    print(f"SIMULATED deploy={ready.action} missing=none conflicts=none")

    missing_model = resolve_deployability(
        requirements,
        {
            "arduino:objectdetection": BrickCapability(
                "arduino:objectdetection", ("yolo-v7",), ("remote_camera_0",)
            )
        },
        (),
        {},
    )
    print(
        f"SIMULATED deploy={missing_model.action} "
        f"missing={','.join(missing_model.missing)}"
    )

    conflict = resolve_deployability(requirements, capabilities, (5000,), {5000: "web"})
    print(f"SIMULATED deploy={conflict.action} conflicts={','.join(map(str, conflict.conflicts))}")

    unknown = resolve_deployability(requirements, None, (5000,), None)
    print(f"SIMULATED deploy={unknown.action} reason={unknown.reason}")


if __name__ == "__main__":
    _demonstrate()
