"""Public type skeleton for safe result reconciliation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ledger import RequestRecord


@dataclass(frozen=True)
class Observation:
    request_id: str
    operation_key: str
    payload_digest: str
    state: str
    observed_at: float


class Decision(str, Enum):
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    KEEP_UNKNOWN = "KEEP_UNKNOWN"
    NOT_APPLIED_FINAL = "NOT_APPLIED_FINAL"
    EXPIRED = "EXPIRED"


def reconcile(record: RequestRecord, observation: Observation, now: float) -> Decision:
    raise NotImplementedError("status reconciliation is not implemented in Task 1")
