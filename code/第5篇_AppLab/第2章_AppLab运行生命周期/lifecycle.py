"""Model an App Lab run lifecycle without starting an App or a device."""
from __future__ import annotations

from dataclasses import dataclass


class LifecycleError(ValueError):
    """Raised when a local lifecycle transition is not allowed."""


ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "IMPORTED": frozenset({"PREPARING", "FAILED"}),
    "PREPARING": frozenset({"STARTING", "FAILED"}),
    "STARTING": frozenset({"RUNNING", "FAILED"}),
    "RUNNING": frozenset({"STOPPING", "FAILED"}),
    "STOPPING": frozenset({"STOPPED", "FAILED"}),
    "STOPPED": frozenset(),
    "FAILED": frozenset(),
}


@dataclass(frozen=True)
class RunLifecycle:
    """Immutable local projection of one App run."""

    run_id: str
    phase: str
    history: tuple[str, ...]


def new_session(run_id: str) -> RunLifecycle:
    """Create a new run at the imported phase."""
    if not run_id.strip():
        raise LifecycleError("run_id must not be empty")
    return RunLifecycle(run_id=run_id, phase="IMPORTED", history=("IMPORTED",))


def advance(session: RunLifecycle, target: str) -> RunLifecycle:
    """Return a new session after one allowed phase transition."""
    if target not in ALLOWED_TRANSITIONS:
        raise LifecycleError(f"unknown target phase: {target}")
    if target not in ALLOWED_TRANSITIONS[session.phase]:
        raise LifecycleError(f"{session.phase} cannot advance to {target}")
    return RunLifecycle(
        run_id=session.run_id,
        phase=target,
        history=session.history + (target,),
    )


def _demonstrate() -> None:
    running = new_session("run-001")
    for phase in ("PREPARING", "STARTING", "RUNNING"):
        running = advance(running, phase)
    print(
        f"SIMULATED session={running.run_id} phase={running.phase} "
        f"history={'>'.join(running.history)}"
    )

    try:
        advance(new_session("run-002"), "STOPPED")
    except LifecycleError as error:
        print(f"SIMULATED rejected={error}")

    stopped = running
    for phase in ("STOPPING", "STOPPED"):
        stopped = advance(stopped, phase)
    print(
        f"SIMULATED terminal={stopped.phase} "
        f"history={'>'.join(stopped.history)}"
    )


if __name__ == "__main__":
    _demonstrate()
