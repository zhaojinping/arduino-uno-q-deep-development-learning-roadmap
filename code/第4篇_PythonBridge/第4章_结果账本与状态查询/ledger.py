"""Public type skeleton for the local Python Bridge result ledger."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class State(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    UNKNOWN = "UNKNOWN"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    NOT_APPLIED_FINAL = "NOT_APPLIED_FINAL"


@dataclass(frozen=True)
class RequestSpec:
    request_id: str
    operation_key: str
    operation: str
    payload_digest: str
    generation: int
    created_at: float
    expires_at: float


@dataclass(frozen=True)
class Evidence:
    kind: str
    detail: str = ""
    observed_at: float | None = None


@dataclass(frozen=True)
class RequestRecord:
    request: RequestSpec
    state: State
    updated_at: float


@dataclass(frozen=True)
class LedgerEvent:
    request_id: str
    from_state: State | None
    to_state: State
    evidence: Evidence | None
    recorded_at: float


class LedgerConflict(Exception):
    """Raised when a ledger operation cannot be applied safely."""


class Ledger:
    """SQLite-backed public ledger API; implementation is supplied by a later task."""

    def __init__(self, database: str) -> None:
        self.database = database

    def create(self, request: RequestSpec, *, now: float | None = None) -> RequestRecord:
        raise NotImplementedError("ledger persistence is not implemented in Task 1")

    def transition(
        self,
        request_id: str,
        *,
        expected: State,
        target: State,
        evidence: Evidence | None = None,
        now: float | None = None,
    ) -> RequestRecord:
        raise NotImplementedError("ledger transitions are not implemented in Task 1")

    def get(self, request_id: str) -> RequestRecord | None:
        raise NotImplementedError("ledger reads are not implemented in Task 1")

    def events(self, request_id: str) -> list[LedgerEvent]:
        raise NotImplementedError("ledger event history is not implemented in Task 1")

    def close(self) -> None:
        """Close hook reserved for the SQLite implementation in a later task."""
        return None
