"""Classify App Lab launch logs without claiming hardware success."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LaunchEvidence:
    startup: str
    python_lines: tuple[str, ...]
    sketch_present: bool
    sketch_lines: tuple[str, ...]


@dataclass(frozen=True)
class LaunchDecision:
    action: str
    reason: str


def assess_launch(evidence: LaunchEvidence) -> LaunchDecision:
    """Classify only the local launch evidence supplied by the caller."""
    if evidence.startup != "READY":
        return LaunchDecision("BLOCKED_STARTUP", "startup did not reach READY")
    if any(line.startswith("ERROR") for line in evidence.python_lines):
        return LaunchDecision("PYTHON_RUNTIME_ERROR", "Python log contains an ERROR line")
    if not evidence.python_lines:
        return LaunchDecision("MISSING_PYTHON_LOG", "Python log is empty")
    if not evidence.sketch_present:
        return LaunchDecision("PYTHON_LOG_READY", "Python log is present; no sketch is part of this App")
    if any(line.startswith("ERROR") for line in evidence.sketch_lines):
        return LaunchDecision("SKETCH_RUNTIME_ERROR", "Sketch log contains an ERROR line")
    if not evidence.sketch_lines:
        return LaunchDecision("MISSING_SKETCH_LOG", "Sketch is present but its log is empty")
    return LaunchDecision(
        "SKETCH_LOG_READY_NEEDS_DEVICE_ASSERTION",
        "startup, Python and Sketch logs are present; device behavior remains unproved",
    )


def _demonstrate() -> None:
    cases = (
        ("compile_error", LaunchEvidence("COMPILE_FAILED", (), True, ())),
        ("python_only", LaunchEvidence("READY", ("INFO app started",), False, ())),
        (
            "app_with_sketch",
            LaunchEvidence("READY", ("INFO app started",), True, ("INFO sketch started",)),
        ),
        ("missing_sketch", LaunchEvidence("READY", ("INFO app started",), True, ())),
    )
    for label, evidence in cases:
        print(f"SIMULATED {label}={assess_launch(evidence).action}")


if __name__ == "__main__":
    _demonstrate()
