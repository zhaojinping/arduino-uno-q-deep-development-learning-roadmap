"""SQLite-backed local result ledger for Python Bridge requests."""
from __future__ import annotations

import sqlite3
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


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
    source: str
    observed_at: float | None = None
    detail: str = ""


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


_ALLOWED_TRANSITIONS = {
    State.PENDING: {State.SENT, State.EXPIRED},
    State.SENT: {State.UNKNOWN, State.APPLIED, State.REJECTED, State.EXPIRED},
    State.UNKNOWN: {
        State.APPLIED,
        State.REJECTED,
        State.EXPIRED,
        State.NOT_APPLIED_FINAL,
    },
}


class Ledger:
    """Append-only event ledger with a SQLite current-state projection."""

    def __init__(self, database: str | Path) -> None:
        self.database = Path(database)
        self._connection: sqlite3.Connection | None = sqlite3.connect(str(self.database))
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize_schema()

    def create(self, request: RequestSpec, *, now: float | None = None) -> RequestRecord:
        recorded_at = time.time() if now is None else now
        connection = self._require_connection()
        try:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    """
                    INSERT INTO requests (
                        request_id, operation_key, operation, payload_digest, generation,
                        created_at, expires_at, state, updated_at,
                        evidence_kind, evidence_source, evidence_observed_at, evidence_detail
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL)
                    """,
                    (
                        request.request_id,
                        request.operation_key,
                        request.operation,
                        request.payload_digest,
                        request.generation,
                        request.created_at,
                        request.expires_at,
                        State.PENDING.value,
                        recorded_at,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO request_events (
                        request_id, sequence, from_state, to_state,
                        evidence_kind, evidence_source, evidence_observed_at, evidence_detail,
                        recorded_at
                    ) VALUES (?, 1, NULL, ?, NULL, NULL, NULL, NULL, ?)
                    """,
                    (request.request_id, State.PENDING.value, recorded_at),
                )
        except sqlite3.IntegrityError as error:
            raise LedgerConflict("request ID already exists") from error
        return RequestRecord(request, State.PENDING, recorded_at)

    def transition(
        self,
        request_id: str,
        *,
        expected: State,
        target: State,
        evidence: Evidence | None = None,
        now: float | None = None,
    ) -> RequestRecord:
        recorded_at = time.time() if now is None else now
        connection = self._require_connection()
        try:
            expected_state = State(expected)
            target_state = State(target)
        except ValueError as error:
            raise LedgerConflict("unknown state") from error

        with connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM requests WHERE request_id = ?", (request_id,)
            ).fetchone()
            if row is None:
                raise LedgerConflict("request does not exist")

            current_state = State(row["state"])
            if current_state != expected_state:
                raise LedgerConflict("request is not in the expected state")
            if target_state not in _ALLOWED_TRANSITIONS.get(current_state, set()):
                raise LedgerConflict("state transition is not allowed")
            if target_state == State.SENT and (evidence is None or evidence.kind != "send"):
                raise LedgerConflict("SENT requires send evidence")

            sequence = connection.execute(
                "SELECT COALESCE(MAX(sequence), 0) + 1 FROM request_events WHERE request_id = ?",
                (request_id,),
            ).fetchone()[0]
            evidence_values = self._evidence_values(evidence)
            connection.execute(
                """
                UPDATE requests
                SET state = ?, updated_at = ?, evidence_kind = ?, evidence_source = ?,
                    evidence_observed_at = ?, evidence_detail = ?
                WHERE request_id = ?
                """,
                (target_state.value, recorded_at, *evidence_values, request_id),
            )
            connection.execute(
                """
                INSERT INTO request_events (
                    request_id, sequence, from_state, to_state,
                    evidence_kind, evidence_source, evidence_observed_at, evidence_detail,
                    recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    sequence,
                    current_state.value,
                    target_state.value,
                    *evidence_values,
                    recorded_at,
                ),
            )
        return RequestRecord(self._request_from_row(row), target_state, recorded_at)

    def get(self, request_id: str) -> RequestRecord | None:
        row = self._require_connection().execute(
            "SELECT * FROM requests WHERE request_id = ?", (request_id,)
        ).fetchone()
        if row is None:
            return None
        return RequestRecord(self._request_from_row(row), State(row["state"]), row["updated_at"])

    def events(self, request_id: str) -> tuple[LedgerEvent, ...]:
        rows = self._require_connection().execute(
            "SELECT * FROM request_events WHERE request_id = ? ORDER BY sequence", (request_id,)
        ).fetchall()
        return tuple(self._event_from_row(row) for row in rows)

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> Ledger:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def _initialize_schema(self) -> None:
        connection = self._require_connection()
        connection.row_factory = sqlite3.Row
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    request_id TEXT PRIMARY KEY,
                    operation_key TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    payload_digest TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    state TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    evidence_kind TEXT,
                    evidence_source TEXT,
                    evidence_observed_at REAL,
                    evidence_detail TEXT
                );
                CREATE TABLE IF NOT EXISTS request_events (
                    request_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    from_state TEXT,
                    to_state TEXT NOT NULL,
                    evidence_kind TEXT,
                    evidence_source TEXT,
                    evidence_observed_at REAL,
                    evidence_detail TEXT,
                    recorded_at REAL NOT NULL,
                    PRIMARY KEY (request_id, sequence),
                    FOREIGN KEY (request_id) REFERENCES requests(request_id)
                );
                """
            )

    def _require_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("ledger is closed")
        return self._connection

    @staticmethod
    def _evidence_values(evidence: Evidence | None) -> tuple[str | None, str | None, float | None, str | None]:
        if evidence is None:
            return (None, None, None, None)
        return (evidence.kind, evidence.source, evidence.observed_at, evidence.detail)

    @staticmethod
    def _request_from_row(row: sqlite3.Row) -> RequestSpec:
        return RequestSpec(
            row["request_id"],
            row["operation_key"],
            row["operation"],
            row["payload_digest"],
            row["generation"],
            row["created_at"],
            row["expires_at"],
        )

    @classmethod
    def _event_from_row(cls, row: sqlite3.Row) -> LedgerEvent:
        evidence = None
        if row["evidence_kind"] is not None:
            evidence = Evidence(
                row["evidence_kind"],
                row["evidence_source"],
                row["evidence_observed_at"],
                row["evidence_detail"],
            )
        from_state = State(row["from_state"]) if row["from_state"] is not None else None
        return LedgerEvent(
            row["request_id"],
            from_state,
            State(row["to_state"]),
            evidence,
            row["recorded_at"],
        )


def _demonstrate() -> None:
    request = RequestSpec("simulated-001", "output:led:1", "set_output", "sha256:demo", 1, 10.0, 30.0)
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "ledger.sqlite3"
        ledger = Ledger(database)
        ledger.create(request, now=10.0)
        ledger.transition(
            request.request_id,
            expected=State.PENDING,
            target=State.SENT,
            evidence=Evidence("send", "simulator", 11.0),
            now=11.0,
        )
        ledger.transition(
            request.request_id,
            expected=State.SENT,
            target=State.UNKNOWN,
            evidence=Evidence("lost-response", "simulator", 12.0),
            now=12.0,
        )
        print(f"SIMULATED current={ledger.get(request.request_id).state.value} events={len(ledger.events(request.request_id))}")
        ledger.close()

        reopened = Ledger(database)
        print(f"SIMULATED restart_state={reopened.get(request.request_id).state.value} events={len(reopened.events(request.request_id))}")
        reopened.transition(
            request.request_id,
            expected=State.UNKNOWN,
            target=State.APPLIED,
            evidence=Evidence("authoritative-query", "simulator", 13.0),
            now=13.0,
        )
        print(f"SIMULATED applied={reopened.get(request.request_id).state.value} events={len(reopened.events(request.request_id))}")
        reopened.close()


if __name__ == "__main__":
    _demonstrate()
