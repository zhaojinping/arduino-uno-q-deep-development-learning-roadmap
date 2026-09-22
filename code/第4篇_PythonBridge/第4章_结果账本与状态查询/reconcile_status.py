"""Public type skeleton for safe result reconciliation."""
from __future__ import annotations

from dataclasses import dataclass
from ledger import RequestRecord


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
    target: str | None
    reason: str


def reconcile(record: RequestRecord, observation: Observation, now: float) -> Decision:
    raise NotImplementedError("status reconciliation is not implemented in Task 1")
