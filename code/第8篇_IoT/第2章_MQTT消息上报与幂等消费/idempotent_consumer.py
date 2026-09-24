"""Offline MQTT QoS 1 redelivery simulation with a SQLite idempotency ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path
from typing import Any


SCOPE = "OFFLINE_QOS1_REDELIVERY_SIMULATION"
MAX_DELIVERY_BYTES = 4096
MAX_DELIVERIES = 1000
HERE = Path(__file__).resolve().parent
CHAPTER_ONE_CODE = HERE.parent / "第1章_IoT开发基础"
if str(CHAPTER_ONE_CODE) not in sys.path:
    sys.path.insert(0, str(CHAPTER_ONE_CODE))

from validate_telemetry import validate_payload  # noqa: E402


def initialize_database(connection: sqlite3.Connection) -> None:
    """Create the small local ledger and simulated business-effect table."""
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS processed_events (
            event_key TEXT PRIMARY KEY,
            payload_sha256 TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS simulated_effects (
            event_key TEXT PRIMARY KEY
                REFERENCES processed_events(event_key),
            metric TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL
        );
        """
    )
    connection.commit()


def _report(outcome: str, event_key: str | None, reason: str | None = None) -> dict[str, Any]:
    return {
        "scope": SCOPE,
        "outcome": outcome,
        "event_key": event_key,
        "reason": reason,
    }


def consume_delivery(connection: sqlite3.Connection, raw: bytes) -> dict[str, Any]:
    """Validate one delivery, then atomically record its key and simulated effect.

    The caller must provide a connection outside an existing transaction.
    The MQTT packet and broker are deliberately not part of this simulation.
    """
    validation = validate_payload(raw)
    if validation["result"] != "VALID":
        return _report("INVALID_REJECTED", None, validation["reason"])

    payload = json.loads(raw.decode("utf-8"))
    event_key = validation["event_key"]
    canonical_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    payload_sha256 = hashlib.sha256(canonical_payload).hexdigest()

    connection.execute("BEGIN IMMEDIATE")
    try:
        previous = connection.execute(
            "SELECT payload_sha256 FROM processed_events WHERE event_key = ?",
            (event_key,),
        ).fetchone()
        if previous is not None:
            connection.rollback()
            if previous[0] == payload_sha256:
                return _report("DUPLICATE_IGNORED", event_key)
            return _report("CONFLICT_REVIEW", event_key, "EVENT_KEY_PAYLOAD_CONFLICT")

        connection.execute(
            "INSERT INTO processed_events(event_key, payload_sha256) VALUES (?, ?)",
            (event_key, payload_sha256),
        )
        connection.execute(
            """INSERT INTO simulated_effects(event_key, metric, value, unit)
               VALUES (?, ?, ?, ?)""",
            (event_key, payload["metric"], payload["value"], payload["unit"]),
        )
        connection.commit()
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise

    return _report("APPLIED", event_key)


def process_file(database: Path, deliveries: Path) -> int:
    """Process a bounded JSONL file and print one machine-readable result per line."""
    processed = 0
    exit_code = 0
    try:
        with closing(sqlite3.connect(str(database), timeout=5.0)) as connection:
            initialize_database(connection)
            with deliveries.open("rb") as stream:
                for line_number, line in enumerate(stream, start=1):
                    if line_number > MAX_DELIVERIES:
                        print(
                            json.dumps(
                                _report("INVALID_REJECTED", None, "TOO_MANY_DELIVERIES"),
                                sort_keys=True,
                            )
                        )
                        return 2
                    raw = line.rstrip(b"\r\n")
                    if not raw:
                        continue
                    if len(raw) > MAX_DELIVERY_BYTES:
                        result = _report("INVALID_REJECTED", None, "PAYLOAD_TOO_LARGE")
                    else:
                        result = consume_delivery(connection, raw)
                    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
                    processed += 1
                    if result["outcome"] in {"INVALID_REJECTED", "CONFLICT_REVIEW"}:
                        exit_code = 2
    except (OSError, sqlite3.Error) as error:
        print(f"local input/database error: {error}", file=sys.stderr)
        return 2

    if processed == 0:
        print("no non-empty delivery lines found", file=sys.stderr)
        return 2
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline-only duplicate-delivery and idempotency demonstration."
    )
    parser.add_argument("--database", type=Path, help="SQLite file for an explicit local run")
    parser.add_argument("--deliveries", type=Path, help="bounded JSONL file of synthetic events")
    args = parser.parse_args()
    if (args.database is None) != (args.deliveries is None):
        parser.error("--database and --deliveries must be supplied together")

    if args.database is not None and args.deliveries is not None:
        return process_file(args.database, args.deliveries)

    fixture = HERE / "qos1_redelivery.jsonl"
    with tempfile.TemporaryDirectory(prefix="uno-q-iot-demo-") as directory:
        database = Path(directory) / "demo.sqlite3"
        return process_file(database, fixture)


if __name__ == "__main__":
    raise SystemExit(main())
