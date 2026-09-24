"""Offline-only model for bounded IoT maintenance commands."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


SCOPE = "OFFLINE_IOT_REMOTE_COMMAND_SIMULATION"
COMMAND_FIELDS = {
    "schema_version",
    "command_id",
    "correlation_id",
    "device_id",
    "operation",
    "parameters",
    "issued_at_unix",
    "expires_at_unix",
}
SUPPORTED_OPERATIONS = {"read_status", "set_sampling_period"}
MAX_COMMAND_LIFETIME_SECONDS = 300
MAX_SAFE_UNIX_SECONDS = (1 << 53) - 1
MAX_COMMAND_LEDGER_ENTRIES = 64
MAX_COMMAND_BYTES = 4096
MAX_DEMO_COMMANDS = 8
MAX_DEMO_FILE_BYTES = MAX_COMMAND_BYTES * MAX_DEMO_COMMANDS
DEMO_NOW = 2_000
HERE = Path(__file__).resolve().parent


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for key, value in pairs:
        if key in parsed:
            raise ValueError(f"duplicate JSON member: {key}")
        parsed[key] = value
    return parsed


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def parse_command(raw: bytes) -> dict[str, Any]:
    """Parse one JSON object while rejecting duplicate members and constants."""
    if type(raw) is not bytes or not raw or len(raw) > MAX_COMMAND_BYTES:
        raise ValueError("command JSON must be non-empty bytes within the size limit")
    try:
        decoded = raw.decode("utf-8", errors="strict")
        value = json.loads(
            decoded,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("command JSON is not valid UTF-8 JSON") from error
    if type(value) is not dict:
        raise ValueError("command JSON root must be an object")
    return value


def _valid_identifier(value: object) -> bool:
    if type(value) is not str or not 1 <= len(value) <= 64:
        return False
    if not value[0].isascii() or not value[0].isalnum():
        return False
    return all(
        character.isascii() and (character.isalnum() or character in "-_.:")
        for character in value
    )


class CommandGate:
    def __init__(
        self,
        *,
        expected_device_id: str,
        principal_operations: dict[str, set[str]],
    ) -> None:
        if not _valid_identifier(expected_device_id):
            raise ValueError("expected_device_id must be a bounded ASCII identifier")
        self.expected_device_id = expected_device_id
        self.principal_operations = {
            principal: set(operations)
            for principal, operations in principal_operations.items()
        }
        self._sampling_period_seconds = 10
        self._commands: dict[str, dict[str, Any]] = {}

    def snapshot(self) -> dict[str, Any]:
        return {"sampling_period_seconds": self._sampling_period_seconds}

    def submit(
        self, command: dict[str, Any], *, principal: str, now: int
    ) -> dict[str, Any]:
        if type(command) is not dict or set(command) != COMMAND_FIELDS:
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id") if isinstance(command, dict) else None,
                "reason": "INVALID_COMMAND_SCHEMA",
            }
        if (
            type(command["schema_version"]) is not int
            or command["schema_version"] != 1
            or not _valid_identifier(command["command_id"])
            or not _valid_identifier(command["correlation_id"])
            or not _valid_identifier(command["device_id"])
            or type(command["operation"]) is not str
            or type(command["parameters"]) is not dict
        ):
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "INVALID_COMMAND_SCHEMA",
            }
        if command.get("device_id") != self.expected_device_id:
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "TARGET_MISMATCH",
            }
        if command.get("operation") not in SUPPORTED_OPERATIONS:
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "UNSUPPORTED_OPERATION",
            }
        parameters = command.get("parameters")
        operation = command["operation"]
        valid_parameters = isinstance(parameters, dict)
        if valid_parameters and operation == "read_status":
            valid_parameters = not parameters
        elif valid_parameters and operation == "set_sampling_period":
            seconds = parameters.get("seconds")
            valid_parameters = (
                set(parameters) == {"seconds"}
                and type(seconds) is int
                and 1 <= seconds <= 60
            )
        if not valid_parameters:
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "INVALID_PARAMETERS",
            }
        if not _valid_identifier(principal):
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "INVALID_PRINCIPAL_CONTEXT",
            }
        if command.get("operation") not in self.principal_operations.get(
            principal, set()
        ):
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "OPERATION_NOT_AUTHORIZED",
            }
        issued_at = command.get("issued_at_unix")
        expires_at = command.get("expires_at_unix")
        if (
            type(now) is not int
            or type(issued_at) is not int
            or type(expires_at) is not int
        ):
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "INVALID_TIME",
            }
        if any(
            timestamp < 0 or timestamp > MAX_SAFE_UNIX_SECONDS
            for timestamp in (now, issued_at, expires_at)
        ):
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "INVALID_TIME",
            }
        if issued_at > now:
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "COMMAND_NOT_YET_VALID",
            }
        if expires_at <= issued_at:
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "INVALID_TIME_WINDOW",
            }
        if expires_at - issued_at > MAX_COMMAND_LIFETIME_SECONDS:
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "COMMAND_LIFETIME_TOO_LONG",
            }
        command_id = command["command_id"]
        fingerprint = hashlib.sha256(
            json.dumps(
                command,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        previous = self._commands.get(command_id)
        if previous is not None:
            if previous["fingerprint"] != fingerprint:
                return {
                    "scope": SCOPE,
                    "status": "ID_CONFLICT",
                    "command_id": command_id,
                    "correlation_id": command.get("correlation_id"),
                    "device_id": command.get("device_id"),
                    "reason": "COMMAND_ID_REUSED_WITH_DIFFERENT_CONTENT",
                }
            if (
                previous["record"]["status"] == "ACCEPTED"
                and expires_at <= now
            ):
                previous["record"].update(
                    {
                        "status": "EXPIRED",
                        "reason": "COMMAND_EXPIRED_BEFORE_APPLY",
                    }
                )
            return deepcopy(
                {
                    **previous["record"],
                    "status": "DUPLICATE_RETURNED",
                    "stored_status": previous["record"]["status"],
                }
            )
        if expires_at <= now:
            return {
                "scope": SCOPE,
                "status": "EXPIRED",
                "command_id": command.get("command_id"),
                "correlation_id": command.get("correlation_id"),
                "device_id": command.get("device_id"),
                "reason": "COMMAND_EXPIRED",
            }
        if len(self._commands) >= MAX_COMMAND_LEDGER_ENTRIES:
            return {
                "scope": SCOPE,
                "status": "LEDGER_FULL",
                "command_id": command_id,
                "correlation_id": command["correlation_id"],
                "device_id": command["device_id"],
                "reason": "COMMAND_LEDGER_CAPACITY_REACHED",
            }
        record = {
            "scope": SCOPE,
            "status": "ACCEPTED",
            "command_id": command_id,
            "correlation_id": command["correlation_id"],
            "device_id": command["device_id"],
            "accepted_at_unix": now,
        }
        self._commands[command_id] = {
            "command": deepcopy(command),
            "principal": principal,
            "fingerprint": fingerprint,
            "record": record,
        }
        return deepcopy(record)

    def execute(self, command_id: str, *, now: int) -> dict[str, Any]:
        if (
            type(now) is not int
            or now < 0
            or now > MAX_SAFE_UNIX_SECONDS
        ):
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command_id,
                "reason": "INVALID_TIME",
            }
        entry = self._commands.get(command_id)
        if entry is None:
            return self.query(command_id)
        if entry["record"]["status"] != "ACCEPTED":
            return deepcopy(
                {
                    **entry["record"],
                    "status": "DUPLICATE_RETURNED",
                    "stored_status": entry["record"]["status"],
                }
            )
        if now < entry["command"]["issued_at_unix"]:
            return {
                "scope": SCOPE,
                "status": "REJECTED",
                "command_id": command_id,
                "reason": "COMMAND_NOT_YET_VALID",
            }
        if entry["command"]["expires_at_unix"] <= now:
            entry["record"].update(
                {
                    "status": "EXPIRED",
                    "reason": "COMMAND_EXPIRED_BEFORE_APPLY",
                }
            )
            return deepcopy(entry["record"])
        if entry["command"]["operation"] == "read_status":
            entry["record"].update(
                {
                    "status": "OBSERVED",
                    "observed_at_unix": now,
                    "result": self.snapshot(),
                }
            )
            return deepcopy(entry["record"])
        seconds = entry["command"]["parameters"]["seconds"]
        self._sampling_period_seconds = seconds
        entry["record"].update(
            {
                "status": "APPLIED",
                "applied_at_unix": now,
                "result": {"sampling_period_seconds": seconds},
            }
        )
        return deepcopy(entry["record"])

    def query(self, command_id: str) -> dict[str, Any]:
        entry = self._commands.get(command_id)
        if entry is None:
            return {
                "scope": SCOPE,
                "status": "UNKNOWN",
                "command_id": command_id,
                "reason": "RESULT_NOT_IN_LOCAL_LEDGER",
                "next_step": "RECONCILE_BEFORE_ANY_RETRY",
            }
        return deepcopy(entry["record"])


def _emit(result: dict[str, Any], *, phase: str) -> None:
    print(
        json.dumps(
            {"phase": phase, **result},
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False,
        )
    )


def run_demo() -> int:
    """Replay only the bounded, repository-local synthetic command fixture."""
    policy = {
        "maintenance-demo": {"read_status", "set_sampling_period"},
        "observer-demo": {"read_status"},
    }
    gate = CommandGate(
        expected_device_id="uno-q-demo-01",
        principal_operations=policy,
    )
    fixture = HERE / "commands.jsonl"
    try:
        with fixture.open("rb") as stream:
            raw_fixture = stream.read(MAX_DEMO_FILE_BYTES + 1)
    except OSError:
        print("offline command demo fixture is unavailable", file=sys.stderr)
        return 2
    if len(raw_fixture) > MAX_DEMO_FILE_BYTES:
        print("offline command demo fixture exceeds its byte limit", file=sys.stderr)
        return 2

    lines = raw_fixture.splitlines()
    if not lines or len(lines) > MAX_DEMO_COMMANDS or any(not line.strip() for line in lines):
        print("offline command demo fixture has an invalid line count", file=sys.stderr)
        return 2

    for line in lines:
        try:
            command = parse_command(line)
        except ValueError:
            print("offline command demo fixture contains invalid JSON", file=sys.stderr)
            return 2
        principal = (
            "observer-demo"
            if command.get("operation") == "read_status"
            else "maintenance-demo"
        )
        submitted = gate.submit(command, principal=principal, now=DEMO_NOW)
        _emit(submitted, phase="submit")
        if submitted["status"] == "ACCEPTED":
            execute_at = (
                DEMO_NOW + 1
                if command.get("command_id") == "cmd-expire-apply-001"
                else DEMO_NOW
            )
            _emit(
                gate.execute(command["command_id"], now=execute_at),
                phase="device_result_simulation",
            )

    _emit(gate.query("cmd-not-observed-001"), phase="reconcile")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run an offline-only IoT remote-command lifecycle simulation."
    )
    parser.parse_args(argv)
    return run_demo()


if __name__ == "__main__":
    raise SystemExit(main())
