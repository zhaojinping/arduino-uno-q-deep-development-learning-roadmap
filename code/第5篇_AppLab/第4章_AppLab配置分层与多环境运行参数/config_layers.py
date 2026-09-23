"""Resolve layered application configuration without contacting a device."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


class ConfigError(ValueError):
    """Raised for invalid configuration inputs that cannot be resolved."""


@dataclass(frozen=True)
class ConfigIssue:
    """One deterministic configuration problem."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ConfigResolution:
    """Immutable result of applying layers from left to right."""

    environment: str
    values: tuple[tuple[str, object], ...]
    sources: tuple[tuple[str, str], ...]
    overridden_keys: tuple[str, ...]
    issues: tuple[ConfigIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    def as_dict(self) -> dict[str, object]:
        """Return a copy suitable for passing to the next local stage."""
        return dict(self.values)


def _issue(issues: list[ConfigIssue], code: str, path: str, message: str) -> None:
    issues.append(ConfigIssue(code, path, message))


def _matches(value: object, expected: type | tuple[type, ...]) -> bool:
    if isinstance(expected, tuple):
        return any(type(value) is candidate for candidate in expected)
    return type(value) is expected


def merge_layers(
    environment: str,
    layers: tuple[tuple[str, Mapping[str, object]], ...],
    *,
    schema: Mapping[str, type | tuple[type, ...]],
    required: tuple[str, ...] = (),
    allowed_environments: tuple[str, ...] = (),
    locked_keys: tuple[str, ...] = (),
) -> ConfigResolution:
    """Merge ``layers`` in order, retaining provenance and validation issues.

    The intended precedence is ``base < environment < runtime``. A later layer
    may override a known key unless that key is locked. This is a local policy
    model; it is not an assertion about App Lab's built-in configuration API.
    """
    issues: list[ConfigIssue] = []
    if not isinstance(environment, str) or not environment.strip():
        _issue(issues, "ENVIRONMENT_INVALID", "environment", "environment must not be empty")
        normalized_environment = ""
    else:
        normalized_environment = environment

    if allowed_environments and normalized_environment not in allowed_environments:
        _issue(
            issues,
            "UNKNOWN_ENVIRONMENT",
            "environment",
            "environment is not in the allowed set",
        )

    values: dict[str, object] = {}
    sources: dict[str, str] = {}
    overridden: list[str] = []
    locked = set(locked_keys)

    for layer_name, layer in layers:
        if not isinstance(layer_name, str) or not layer_name.strip():
            _issue(issues, "LAYER_NAME_INVALID", "layers", "layer name must be non-empty")
            continue
        if not isinstance(layer, Mapping):
            _issue(
                issues,
                "LAYER_NOT_MAPPING",
                layer_name,
                "configuration layer must be a mapping",
            )
            continue
        for key, value in layer.items():
            path = f"{layer_name}.{key}"
            if key not in schema:
                _issue(issues, "UNKNOWN_KEY", path, "key is not declared in the schema")
                continue
            if not _matches(value, schema[key]):
                _issue(issues, "TYPE_MISMATCH", path, "value does not match the schema type")
                continue
            if key in values and values[key] != value:
                if key in locked:
                    _issue(
                        issues,
                        "LOCKED_OVERRIDE",
                        path,
                        "a later layer cannot override this locked key",
                    )
                    continue
                if key not in overridden:
                    overridden.append(key)
            values[key] = value
            sources[key] = layer_name

    for key in required:
        if key not in values:
            _issue(issues, "MISSING_REQUIRED", key, "required key is missing after merge")

    return ConfigResolution(
        normalized_environment,
        tuple(sorted(values.items())),
        tuple(sorted(sources.items())),
        tuple(overridden),
        tuple(issues),
    )


def _format_values(values: Mapping[str, object]) -> str:
    return ",".join(f"{key}={values[key]}" for key in sorted(values))


def _demonstrate() -> None:
    schema = {"APP_MODE": str, "LOG_LEVEL": str, "TARGET_BOARD": str}
    resolved = merge_layers(
        "staging",
        (
            ("base", {"APP_MODE": "production", "LOG_LEVEL": "info", "TARGET_BOARD": "test-q"}),
            ("environment", {"APP_MODE": "staging", "LOG_LEVEL": "debug"}),
        ),
        schema=schema,
        required=("APP_MODE", "TARGET_BOARD"),
        allowed_environments=("development", "staging", "production"),
    )
    print(
        f"SIMULATED env={resolved.environment} valid={str(resolved.valid).lower()} "
        f"values={_format_values(resolved.as_dict())}"
    )
    print(f"SIMULATED overrides={','.join(resolved.overridden_keys)}")

    invalid = merge_layers("staging", (("environment", {"EXTRA": "value"}),), schema=schema)
    issue = invalid.issues[0]
    print(f"SIMULATED invalid={issue.code}:{issue.path}")

    locked = merge_layers(
        "staging",
        (("base", {"TARGET_BOARD": "test-q"}), ("runtime", {"TARGET_BOARD": "现场-q"})),
        schema=schema,
        locked_keys=("TARGET_BOARD",),
    )
    issue = locked.issues[0]
    print(f"SIMULATED locked={issue.code}:{issue.path}")


if __name__ == "__main__":
    _demonstrate()
