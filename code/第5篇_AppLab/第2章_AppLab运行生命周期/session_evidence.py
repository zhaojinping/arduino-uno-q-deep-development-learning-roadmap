"""Classify run-scoped App Lab evidence without claiming hardware success."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceLine:
    """One normalized log observation associated with a run identifier."""

    run_id: str
    channel: str
    event: str
    message: str


@dataclass(frozen=True)
class EvidenceDecision:
    """Local decision made from the selected run's evidence only."""

    action: str
    reason: str
    channels: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()


def assess_session(
    run_id: str,
    lines: tuple[EvidenceLine, ...],
    required_channels: tuple[str, ...] = ("startup", "python"),
) -> EvidenceDecision:
    """Classify one run while ignoring lines belonging to older runs."""
    current = tuple(line for line in lines if line.run_id == run_id)
    if not current:
        return EvidenceDecision(
            "UNKNOWN_NO_CURRENT_LINES",
            "no evidence belongs to the requested run",
        )

    channels = tuple(sorted({line.channel for line in current}))
    if any(line.event == "STOPPED" for line in current):
        return EvidenceDecision("STOPPED", "current run contains STOPPED", channels)
    for line in current:
        if line.event == "ERROR":
            return EvidenceDecision(
                "FAILED",
                f"{line.channel} emitted ERROR",
                channels,
            )

    missing = tuple(sorted(set(required_channels) - set(channels)))
    if missing:
        return EvidenceDecision(
            "UNKNOWN_INCOMPLETE",
            "required evidence channel is missing",
            channels,
            missing,
        )

    startup_ready = any(
        line.channel == "startup" and line.event == "READY" for line in current
    )
    python_started = any(
        line.channel == "python" and line.event == "STARTED" for line in current
    )
    if not startup_ready or not python_started:
        return EvidenceDecision(
            "UNKNOWN_INCOMPLETE",
            "required startup or Python event is missing",
            channels,
        )

    if "sketch" in required_channels and not any(
        line.channel == "sketch" and line.event == "STARTED" for line in current
    ):
        return EvidenceDecision(
            "UNKNOWN_INCOMPLETE",
            "required Sketch STARTED event is missing",
            channels,
            ("sketch",),
        )
    return EvidenceDecision("RUNNING", "current run has required start evidence", channels)


def _demonstrate() -> None:
    stale_case = assess_session(
        "run-new",
        (
            EvidenceLine("run-old", "python", "ERROR", "old failure"),
            EvidenceLine("run-new", "startup", "READY", "startup ready"),
            EvidenceLine("run-new", "python", "STARTED", "main started"),
        ),
    )
    print(
        f"SIMULATED stale_error={stale_case.action} "
        f"channels={','.join(stale_case.channels)}"
    )

    no_current = assess_session(
        "run-new",
        (EvidenceLine("run-old", "startup", "READY", "old run"),),
    )
    print(f"SIMULATED no_current={no_current.action}")

    failed = assess_session(
        "run-new",
        (
            EvidenceLine("run-new", "startup", "READY", "startup ready"),
            EvidenceLine("run-new", "python", "ERROR", "traceback"),
        ),
    )
    print(f"SIMULATED runtime_error={failed.action}")

    stopped = assess_session(
        "run-new",
        (
            EvidenceLine("run-new", "startup", "READY", "startup ready"),
            EvidenceLine("run-new", "python", "STARTED", "main started"),
            EvidenceLine("run-new", "lifecycle", "STOPPED", "user requested stop"),
        ),
    )
    print(f"SIMULATED stopped={stopped.action}")


if __name__ == "__main__":
    _demonstrate()
