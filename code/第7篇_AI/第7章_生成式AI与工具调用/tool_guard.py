"""Offline tool-call safety gate using virtual state only."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


_CALL_ID = re.compile(r"[A-Za-z0-9_-]{1,48}\Z")
_ALLOWED_COLORS = frozenset({"off", "green", "amber", "red"})
_EXPECTED_FIELDS = frozenset({"call_id", "name", "arguments"})


@dataclass(frozen=True)
class OperatorApproval:
    """Teaching signal supplied separately from an untrusted tool proposal."""

    call_id: str
    actor: str
    approved: bool


@dataclass
class _CallRecord:
    fingerprint: str
    phase: str


class ToolCallGuard:
    """Validate a narrow tool allowlist and mutate simulated state only."""

    def __init__(self) -> None:
        self._indicator = "off"
        self._write_count = 0
        self._calls: dict[str, _CallRecord] = {}
        self._audit: list[dict[str, Any]] = []

    @property
    def indicator(self) -> str:
        return self._indicator

    @property
    def write_count(self) -> int:
        return self._write_count

    @property
    def audit_log(self) -> list[dict[str, Any]]:
        return [entry.copy() for entry in self._audit]

    def dispatch(
        self, proposal: object, *, approval: OperatorApproval | None = None
    ) -> dict[str, Any]:
        """Validate and simulate a proposed call; never access external I/O."""
        if type(proposal) is not dict:
            return self._finish(None, None, "REJECTED", "REQUEST_NOT_OBJECT")

        raw_call_id = proposal.get("call_id")
        call_id = raw_call_id if type(raw_call_id) is str else None
        raw_name = proposal.get("name")
        name = raw_name if type(raw_name) is str else None
        if call_id is None or _CALL_ID.fullmatch(call_id) is None:
            return self._finish(None, name, "REJECTED", "INVALID_CALL_ID")

        try:
            canonical = json.dumps(
                proposal,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
        except (TypeError, ValueError, RecursionError):
            return self._finish(call_id, name, "REJECTED", "INVALID_JSON_VALUE")
        fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        previous = self._calls.get(call_id)
        if previous is not None:
            if previous.fingerprint != fingerprint:
                return self._finish(call_id, name, "CALL_ID_CONFLICT", "ID_PAYLOAD_MISMATCH")
            if previous.phase != "PENDING_APPROVAL":
                return self._finish(call_id, name, "DUPLICATE_BLOCKED", "CALL_ALREADY_FINAL")

        if frozenset(proposal) != _EXPECTED_FIELDS:
            return self._reject_and_remember(
                call_id, name, fingerprint, "INVALID_FIELDS"
            )
        if name not in {"read_virtual_status", "set_virtual_indicator"}:
            return self._reject_and_remember(call_id, name, fingerprint, "UNKNOWN_TOOL")

        arguments = proposal["arguments"]
        if type(arguments) is not dict:
            return self._reject_and_remember(
                call_id, name, fingerprint, "ARGUMENTS_NOT_OBJECT"
            )

        if name == "read_virtual_status":
            if arguments:
                return self._reject_and_remember(
                    call_id, name, fingerprint, "INVALID_ARGUMENTS"
                )
            if approval is not None:
                return self._reject_and_remember(
                    call_id, name, fingerprint, "APPROVAL_NOT_APPLICABLE"
                )
            self._calls[call_id] = _CallRecord(fingerprint, "FINAL")
            return self._finish(
                call_id,
                name,
                "EXECUTED",
                "OK",
                {"indicator": self._indicator, "scope": "SIMULATED"},
            )

        if frozenset(arguments) != frozenset({"color"}):
            return self._reject_and_remember(
                call_id, name, fingerprint, "INVALID_ARGUMENTS"
            )
        color = arguments["color"]
        if type(color) is not str or color not in _ALLOWED_COLORS:
            return self._reject_and_remember(
                call_id, name, fingerprint, "INVALID_ARGUMENTS"
            )

        if approval is None:
            self._calls[call_id] = _CallRecord(fingerprint, "PENDING_APPROVAL")
            return self._finish(
                call_id, name, "APPROVAL_REQUIRED", "OPERATOR_APPROVAL_REQUIRED"
            )
        if not isinstance(approval, OperatorApproval):
            self._calls[call_id] = _CallRecord(fingerprint, "PENDING_APPROVAL")
            return self._finish(
                call_id, name, "APPROVAL_REQUIRED", "APPROVAL_NOT_BOUND_TO_CALL"
            )
        if approval.call_id != call_id or type(approval.actor) is not str or not approval.actor.strip():
            self._calls[call_id] = _CallRecord(fingerprint, "PENDING_APPROVAL")
            return self._finish(
                call_id, name, "APPROVAL_REQUIRED", "APPROVAL_NOT_BOUND_TO_CALL"
            )
        if type(approval.approved) is not bool:
            self._calls[call_id] = _CallRecord(fingerprint, "PENDING_APPROVAL")
            return self._finish(
                call_id, name, "APPROVAL_REQUIRED", "INVALID_APPROVAL_DECISION"
            )
        if not approval.approved:
            self._calls[call_id] = _CallRecord(fingerprint, "FINAL")
            return self._finish(
                call_id,
                name,
                "OPERATOR_DENIED",
                "DENIED_BY_OPERATOR",
                actor=approval.actor,
            )

        self._indicator = color
        self._write_count += 1
        self._calls[call_id] = _CallRecord(fingerprint, "FINAL")
        return self._finish(
            call_id,
            name,
            "EXECUTED",
            "OK",
            {"indicator": self._indicator, "scope": "SIMULATED"},
            actor=approval.actor,
        )

    def _reject_and_remember(
        self, call_id: str, name: str | None, fingerprint: str, reason: str
    ) -> dict[str, Any]:
        self._calls[call_id] = _CallRecord(fingerprint, "FINAL")
        return self._finish(call_id, name, "REJECTED", reason)

    def _finish(
        self,
        call_id: str | None,
        name: str | None,
        status: str,
        reason: str,
        result: dict[str, Any] | None = None,
        actor: str | None = None,
    ) -> dict[str, Any]:
        entry = {
            "call_id": call_id,
            "tool": name,
            "actor": actor,
            "status": status,
            "reason": reason,
            "timestamp_utc": datetime.now(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
        }
        self._audit.append(entry.copy())
        return {**entry, "result": result}


def build_demo_report() -> dict[str, Any]:
    """Run fixed proposals through the local simulator, with no external I/O."""
    guard = ToolCallGuard()
    read_call = {
        "call_id": "demo-read-001",
        "name": "read_virtual_status",
        "arguments": {},
    }
    write_call = {
        "call_id": "demo-write-001",
        "name": "set_virtual_indicator",
        "arguments": {"color": "green"},
    }

    steps = [guard.dispatch(read_call), guard.dispatch(write_call)]
    approval = OperatorApproval(
        call_id="demo-write-001", actor="operator-demo", approved=True
    )
    steps.append(guard.dispatch(write_call, approval=approval))
    steps.append(guard.dispatch(write_call, approval=approval))
    return {
        "scope": "SIMULATION_ONLY",
        "model_api_called": False,
        "network_accessed": False,
        "hardware_io": False,
        "steps": steps,
        "final_virtual_state": {
            "indicator": guard.indicator,
            "write_count": guard.write_count,
        },
        "audit": guard.audit_log,
    }


def main() -> int:
    print(json.dumps(build_demo_report(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
