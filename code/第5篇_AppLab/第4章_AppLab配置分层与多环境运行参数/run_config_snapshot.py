"""Build a deterministic, redacted snapshot for one App run."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json


class SnapshotError(ValueError):
    """Raised when a run configuration cannot be safely snapshotted."""


JSON_SCALARS = (str, int, float, bool, type(None))


@dataclass(frozen=True)
class ConfigSnapshot:
    """Immutable public view of one run's redacted configuration."""

    run_id: str
    environment: str
    _redacted_values: tuple[tuple[str, object], ...]
    redacted_keys: tuple[str, ...]
    fingerprint: str

    @property
    def redacted_values(self) -> dict[str, object]:
        return dict(self._redacted_values)

    def to_dict(self) -> dict[str, object]:
        return {
            "environment": self.environment,
            "run_id": self.run_id,
            "values": self.redacted_values,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )


def _canonical_json(environment: str, run_id: str, values: Mapping[str, object]) -> str:
    payload = {"environment": environment, "run_id": run_id, "values": dict(values)}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_snapshot(
    run_id: str,
    environment: str,
    values: Mapping[str, object],
    secret_keys: tuple[str, ...] = (),
) -> ConfigSnapshot:
    """Return a stable snapshot whose public payload never contains secret values."""
    if not isinstance(run_id, str) or not run_id.strip():
        raise SnapshotError("run_id must not be empty")
    if not isinstance(environment, str) or not environment.strip():
        raise SnapshotError("environment must not be empty")
    if not isinstance(values, Mapping):
        raise SnapshotError("values must be a mapping")

    for key, value in values.items():
        if not isinstance(key, str) or not key.strip():
            raise SnapshotError("configuration keys must be non-empty strings")
        if not any(type(value) is scalar for scalar in JSON_SCALARS):
            raise SnapshotError(f"{key} must be a JSON scalar")

    normalized_secret_keys = tuple(sorted(secret_keys))
    for key in normalized_secret_keys:
        if key not in values:
            raise SnapshotError(f"secret key is missing: {key}")

    redacted = dict(values)
    for key in normalized_secret_keys:
        redacted[key] = "<redacted>"
    ordered = tuple(sorted(redacted.items()))
    canonical = _canonical_json(environment, run_id, dict(ordered))
    fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return ConfigSnapshot(run_id, environment, ordered, normalized_secret_keys, fingerprint)


def _demonstrate() -> None:
    snapshot = build_snapshot(
        "run-042",
        "staging",
        {"APP_MODE": "staging", "DB_PASSWORD": "do-not-print", "LOG_LEVEL": "debug"},
        secret_keys=("DB_PASSWORD",),
    )
    print(
        f"SIMULATED snapshot={snapshot.run_id} env={snapshot.environment} "
        f"redacted={','.join(snapshot.redacted_keys)}"
    )
    print(f"SIMULATED payload={snapshot.to_json()}")
    print(f"SIMULATED fingerprint={snapshot.fingerprint[:12]}")


if __name__ == "__main__":
    _demonstrate()
