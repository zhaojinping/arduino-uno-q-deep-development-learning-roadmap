"""Offline checks for the structural contract of an Arduino App."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


class AppContractError(ValueError):
    """Raised when an App manifest and its files cannot form a safe project."""


@dataclass(frozen=True)
class LayoutResult:
    mode: str
    required: tuple[str, ...]
    optional: tuple[str, ...]


def validate_layout(
    manifest: Mapping[str, object], files: set[str],
) -> LayoutResult:
    """Validate App Lab's file-level contract without opening a board or YAML parser."""
    if not isinstance(manifest, Mapping):
        raise AppContractError("manifest must be a mapping")
    if "app.yaml" not in files:
        raise AppContractError("missing app.yaml")
    if "python/main.py" not in files:
        raise AppContractError("missing python/main.py")

    ports = manifest.get("ports")
    if ports is not None and (
        not isinstance(ports, list)
        or any(isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535 for port in ports)
    ):
        raise AppContractError("ports must be a list of TCP port integers")

    bricks = manifest.get("bricks")
    if bricks is not None and (
        not isinstance(bricks, list)
        or any(not isinstance(brick, (str, Mapping)) for brick in bricks)
    ):
        raise AppContractError("bricks must be a list of IDs or configurations")

    sketch_files = {"sketch/sketch.ino", "sketch/sketch.yaml"}
    has_sketch_folder = any(path == "sketch" or path.startswith("sketch/") for path in files)
    if not has_sketch_folder:
        return LayoutResult("PYTHON_ONLY", ("app.yaml", "python/main.py"), ())
    missing = sorted(sketch_files - files)
    if missing:
        raise AppContractError(f"missing {missing[0]}")
    return LayoutResult(
        "PYTHON_AND_SKETCH",
        ("app.yaml", "python/main.py"),
        ("sketch/sketch.ino", "sketch/sketch.yaml"),
    )


def _demonstrate() -> None:
    valid = validate_layout(
        {"name": "Contract Demo", "ports": [8080], "bricks": ["arduino:web_ui"]},
        {"app.yaml", "python/main.py", "sketch/sketch.ino", "sketch/sketch.yaml"},
    )
    print(f"SIMULATED valid={valid.mode} app_yaml=present python_main=present")
    print("SIMULATED sketch=optional-present sketch_ino=present sketch_yaml=present")
    print("SIMULATED reserved=data:persistent,.cache:volatile")
    try:
        validate_layout({"name": "Contract Demo"}, {"app.yaml"})
    except AppContractError as error:
        print(f"SIMULATED invalid={error}")


if __name__ == "__main__":
    _demonstrate()
