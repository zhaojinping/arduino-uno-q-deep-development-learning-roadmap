"""Public type skeleton for safe result reconciliation."""
from __future__ import annotations

from dataclasses import dataclass
import math
from ledger import RequestRecord, RequestSpec, State


@dataclass(frozen=True)
class Observation:
    request_id: str
    operation_key: str
    operation: str
    payload_digest: str
    kind: str
    source: str
    observed_at: float
    authoritative: bool
    detail: str = ""


@dataclass(frozen=True)
class Decision:
    action: str
    target: State | None
    reason: str


def reconcile(record: RequestRecord, observation: Observation, now: float) -> Decision:
    """Choose a safe next action without changing the ledger."""
    if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now):
        raise ValueError("now must be finite")

    if record.state != State.UNKNOWN:
        return Decision("KEEP_UNKNOWN", None, "record is not UNKNOWN")

    request = record.request
    record_identity = (
        request.request_id,
        request.operation_key,
        request.operation,
        request.payload_digest,
    )
    observation_identity = (
        observation.request_id,
        observation.operation_key,
        observation.operation,
        observation.payload_digest,
    )
    if not _matching_identity(record_identity, observation_identity):
        return Decision("KEEP_UNKNOWN", None, "observation identity does not match")

    if observation.kind == "NOT_FOUND":
        return Decision("KEEP_UNKNOWN", None, "not found is not final proof")

    final_decisions = {
        "APPLIED": ("CLOSE_APPLIED", State.APPLIED),
        "REJECTED": ("CLOSE_REJECTED", State.REJECTED),
        "NOT_APPLIED_FINAL": ("CLOSE_NOT_APPLIED", State.NOT_APPLIED_FINAL),
    }
    if observation.authoritative is True and observation.kind in final_decisions:
        action, target = final_decisions[observation.kind]
        return Decision(action, target, "authoritative final observation")

    if now >= request.expires_at:
        return Decision("STOP_EXPIRED", None, "request has expired without final proof")
    return Decision("KEEP_UNKNOWN", None, "observation is not authoritative final proof")


def _matching_identity(
    record_identity: tuple[str, str, str, str],
    observation_identity: tuple[str, str, str, str],
) -> bool:
    """Reject malformed identities rather than converting or comparing them loosely."""
    values = record_identity + observation_identity
    if any(not isinstance(value, str) or not value for value in values):
        return False
    return record_identity == observation_identity


def _demonstrate() -> None:
    request = RequestSpec(
        "simulated-001", "output:led:1", "set_output", "sha256:demo", 1, 10.0, 30.0
    )
    record = RequestRecord(request, State.UNKNOWN, 12.0)
    identity = (
        request.request_id,
        request.operation_key,
        request.operation,
        request.payload_digest,
    )
    observations = (
        ("not_found", Observation(*identity, "NOT_FOUND", "simulator", 20.0, True), 20.0),
        ("applied", Observation(*identity, "APPLIED", "simulator", 20.0, True), 20.0),
        (
            "expired_not_applied",
            Observation(*identity, "NOT_APPLIED_FINAL", "simulator", 31.0, True),
            31.0,
        ),
        (
            "mismatch",
            Observation("other", request.operation_key, request.operation, request.payload_digest,
                        "APPLIED", "simulator", 20.0, True),
            20.0,
        ),
    )
    for label, observation, now in observations:
        print(f"SIMULATED {label}: {reconcile(record, observation, now).action}")


if __name__ == "__main__":
    _demonstrate()
