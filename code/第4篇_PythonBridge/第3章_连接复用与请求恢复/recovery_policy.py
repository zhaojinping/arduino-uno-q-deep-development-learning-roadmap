"""Pure recovery decisions for validated application records; no I/O."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from math import isfinite


class Delivery(Enum):
    NOT_SENT = "NOT_SENT"
    MAYBE_SENT = "MAYBE_SENT"


@dataclass(frozen=True)
class Request:
    target: str
    operation_key: str
    payload_digest: str
    delivery: Delivery
    expires_at: float
    replay_safe: bool = False


@dataclass(frozen=True)
class ResultRecord:
    target: str
    operation_key: str
    payload_digest: str
    state: str


def decide_recovery(
    request: Request,
    record: ResultRecord | None,
    *,
    ready: bool,
    now: float,
) -> str:
    if not isfinite(now) or not isfinite(request.expires_at):
        raise ValueError("finite monotonic times required")
    if not isinstance(request.delivery, Delivery):
        raise ValueError("unsupported delivery evidence")
    if record is not None:
        expected = (request.target, request.operation_key, request.payload_digest)
        actual = (record.target, record.operation_key, record.payload_digest)
        if actual != expected:
            return "KEEP_UNKNOWN"
        if record.state == "APPLIED":
            return "STOP_APPLIED"
        if record.state == "REJECTED":
            return "STOP_REJECTED"
        if record.state not in {"NOT_FOUND", "IN_PROGRESS", "NOT_APPLIED_FINAL"}:
            return "KEEP_UNKNOWN"
    if now >= request.expires_at:
        if record is not None and record.state == "NOT_APPLIED_FINAL":
            return "STOP_NOT_APPLIED"
        return (
            "STOP_EXPIRED"
            if request.delivery is Delivery.NOT_SENT
            else "KEEP_UNKNOWN"
        )
    if not ready:
        return "WAIT_READY"
    if request.delivery is Delivery.NOT_SENT:
        # An unexpected remote record contradicts the local NOT_SENT evidence.
        return "SEND_FIRST_ATTEMPT" if record is None else "KEEP_UNKNOWN"
    if record is None:
        return "QUERY_ONLY"
    if record.state == "IN_PROGRESS":
        return "WAIT_AND_QUERY"
    if record.state == "NOT_APPLIED_FINAL" and request.replay_safe:
        return "RESUBMIT_SAME_KEY"
    if record.state == "NOT_APPLIED_FINAL":
        return "MANUAL_REVIEW"
    return "KEEP_UNKNOWN"


def main() -> None:
    request = Request(
        "sim-device", "op-007", "demo-payload-A", Delivery.MAYBE_SENT, 20.0
    )
    record = ResultRecord("sim-device", "op-007", "demo-payload-A", "NOT_FOUND")
    cases = [
        ("lost_response", request, None, 10.0),
        ("missing_record", request, record, 10.0),
        ("late_confirmation", request, replace(record, state="APPLIED"), 30.0),
        (
            "fenced_and_safe",
            replace(request, replay_safe=True),
            replace(record, state="NOT_APPLIED_FINAL"),
            10.0,
        ),
        ("wrong_payload", request, replace(record, payload_digest="other"), 10.0),
        ("expired_not_applied", request, replace(record, state="NOT_APPLIED_FINAL"), 30.0),
        (
            "expired_unsent",
            replace(request, delivery=Delivery.NOT_SENT),
            None,
            30.0,
        ),
    ]
    for label, req, result, now in cases:
        decision = decide_recovery(req, result, ready=True, now=now)
        print(f"SIMULATED {label}: {decision}")


if __name__ == "__main__":
    main()
