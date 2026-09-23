"""Validate the declarative part of an Arduino App manifest offline."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ContractIssue:
    """One deterministic issue found in an App descriptor."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ContractReport:
    """Normalized result of validating a manifest-shaped mapping."""

    valid: bool
    issues: tuple[ContractIssue, ...]
    ports: tuple[int, ...]
    brick_ids: tuple[str, ...]


def _issue(issues: list[ContractIssue], code: str, path: str, message: str) -> None:
    issues.append(ContractIssue(code, path, message))


def _validate_ports(value: object, issues: list[ContractIssue]) -> tuple[int, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        _issue(issues, "PORTS_NOT_LIST", "ports", "ports must be a list")
        return ()

    ports: list[int] = []
    seen: set[int] = set()
    for index, port in enumerate(value):
        path = f"ports[{index}]"
        if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
            _issue(
                issues,
                "PORT_INVALID",
                path,
                "port must be an integer between 1 and 65535",
            )
            continue
        if port in seen:
            _issue(issues, "PORT_DUPLICATE", path, "port must not be repeated")
            continue
        seen.add(port)
        ports.append(port)
    return tuple(ports)


def _validate_brick(
    value: object,
    index: int,
    issues: list[ContractIssue],
) -> str | None:
    path = f"bricks[{index}]"
    if isinstance(value, str):
        if value.strip():
            return value
        _issue(issues, "BRICK_ID_INVALID", path, "Brick id must not be empty")
        return None

    if not isinstance(value, Mapping):
        _issue(
            issues,
            "BRICK_ENTRY_INVALID",
            path,
            "Brick entry must be an id string or a one-key mapping",
        )
        return None
    if len(value) != 1:
        _issue(
            issues,
            "BRICK_ENTRY_SHAPE",
            path,
            "configured Brick entry must contain exactly one id",
        )
        return None

    brick_id, options = next(iter(value.items()))
    if not isinstance(brick_id, str) or not brick_id.strip():
        _issue(issues, "BRICK_ID_INVALID", path, "Brick id must be a non-empty string")
        return None
    if not isinstance(options, Mapping):
        _issue(
            issues,
            "BRICK_CONFIG_INVALID",
            f"{path}.{brick_id}",
            "Brick options must be a mapping",
        )
        return brick_id

    allowed = {"model", "variables", "devices"}
    for option in options:
        if option not in allowed:
            _issue(
                issues,
                "BRICK_OPTION_UNKNOWN",
                f"{path}.{brick_id}.{option}",
                "unsupported local Brick option",
            )

    model = options.get("model")
    if model is not None and (not isinstance(model, str) or not model.strip()):
        _issue(
            issues,
            "MODEL_INVALID",
            f"{path}.{brick_id}.model",
            "model must be a non-empty string",
        )

    variables = options.get("variables")
    if variables is not None:
        if not isinstance(variables, Mapping):
            _issue(
                issues,
                "VARIABLES_NOT_MAPPING",
                f"{path}.{brick_id}.variables",
                "variables must be a mapping",
            )
        else:
            for key, variable in variables.items():
                variable_path = f"{path}.{brick_id}.variables.{key}"
                if not isinstance(key, str) or not key.strip():
                    _issue(
                        issues,
                        "VARIABLE_KEY_INVALID",
                        variable_path,
                        "variable keys must be non-empty strings",
                    )
                if not isinstance(variable, str):
                    _issue(
                        issues,
                        "VARIABLE_VALUE_INVALID",
                        variable_path,
                        "variable values must be strings",
                    )

    devices = options.get("devices")
    if devices is not None:
        if not isinstance(devices, list):
            _issue(
                issues,
                "DEVICES_NOT_LIST",
                f"{path}.{brick_id}.devices",
                "devices must be a list",
            )
        else:
            for device_index, device in enumerate(devices):
                if not isinstance(device, str) or not device.strip():
                    _issue(
                        issues,
                        "DEVICE_INVALID",
                        f"{path}.{brick_id}.devices[{device_index}]",
                        "device references must be non-empty strings",
                    )
    return brick_id


def _validate_bricks(value: object, issues: list[ContractIssue]) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        _issue(issues, "BRICKS_NOT_LIST", "bricks", "bricks must be a list")
        return ()

    brick_ids: list[str] = []
    for index, brick in enumerate(value):
        brick_id = _validate_brick(brick, index, issues)
        if brick_id is not None:
            brick_ids.append(brick_id)
    return tuple(brick_ids)


def validate_manifest(manifest: Mapping[str, object]) -> ContractReport:
    """Validate ``app.yaml`` fields represented as a Python mapping.

    This function intentionally validates types and local shape only. It does not
    resolve a Brick, inspect a target board, or infer whether a variable is a
    secret; secret classification belongs to the Brick definition and runtime.
    """
    issues: list[ContractIssue] = []
    if not isinstance(manifest, Mapping):
        _issue(issues, "MANIFEST_NOT_MAPPING", "", "manifest must be a mapping")
        return ContractReport(False, tuple(issues), (), ())

    if "name" in manifest and not isinstance(manifest["name"], str):
        _issue(issues, "NAME_INVALID", "name", "name must be a string when present")

    ports = _validate_ports(manifest.get("ports"), issues)
    brick_ids = _validate_bricks(manifest.get("bricks"), issues)
    return ContractReport(not issues, tuple(issues), ports, brick_ids)


def _demonstrate() -> None:
    valid = validate_manifest(
        {
            "name": "Smart Garden",
            "ports": [5000],
            "bricks": [
                {"arduino:dbstorage": {"variables": {"DB_PASSWORD": "${DB_PASSWORD}"}}},
                {"arduino:objectdetection": {"model": "yolo-v8", "devices": ["remote_camera_0"]}},
            ],
        }
    )
    print(
        f"SIMULATED manifest={'VALID' if valid.valid else 'INVALID'} "
        f"ports={','.join(str(port) for port in valid.ports)} "
        f"bricks={','.join(valid.brick_ids)}"
    )

    invalid = validate_manifest({"ports": [0]})
    issue = invalid.issues[0]
    print(f"SIMULATED invalid={issue.code}:{issue.path}")

    typed = validate_manifest(
        {"bricks": [{"arduino:camera": {"variables": {"MODE": 1}}}]}
    )
    issue = typed.issues[0]
    print(f"SIMULATED invalid_type={issue.code}:{issue.path}")


if __name__ == "__main__":
    _demonstrate()
