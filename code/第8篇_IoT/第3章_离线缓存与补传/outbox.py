"""Offline-only, bounded SQLite outbox for validated IoT telemetry."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
import time
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any, Iterator


SCOPE = "OFFLINE_PERSISTENT_OUTBOX_SIMULATION"
MAX_TTL_SECONDS = 30 * 24 * 60 * 60
MAX_SQLITE_INTEGER = (1 << 63) - 1
HERE = Path(__file__).resolve().parent
CHAPTER_ONE_CODE = HERE.parent / "第1章_IoT开发基础"
if str(CHAPTER_ONE_CODE) not in sys.path:
    sys.path.insert(0, str(CHAPTER_ONE_CODE))

from validate_telemetry import validate_payload  # noqa: E402


def _valid_integer(value: object, *, minimum: int, maximum: int) -> bool:
    return type(value) is int and minimum <= value <= maximum


def _report(
    outcome: str,
    event_key: str | None = None,
    *,
    reason: str | None = None,
    **details: Any,
) -> dict[str, Any]:
    return {
        "scope": SCOPE,
        "outcome": outcome,
        "event_key": event_key,
        "reason": reason,
        **details,
    }


class Outbox:
    """Persist telemetry until the next-hop outcome is known or TTL expires.

    This teaching implementation expects one publisher worker per database.
    Each operation opens its own SQLite connection so closing/reopening an
    ``Outbox`` models process restart without keeping an in-memory queue.
    """

    def __init__(
        self,
        database: str | Path,
        *,
        max_items: int = 1000,
        max_payload_bytes: int = 4096,
    ) -> None:
        if not _valid_integer(max_items, minimum=1, maximum=1_000_000):
            raise ValueError("max_items must be an integer from 1 to 1000000")
        if not _valid_integer(max_payload_bytes, minimum=1, maximum=4096):
            raise ValueError("max_payload_bytes must be an integer from 1 to 4096")

        self.database = Path(database)
        if not self.database.parent.is_dir():
            raise FileNotFoundError("database parent directory must already exist")
        self.max_items = max_items
        self.max_payload_bytes = max_payload_bytes
        self._closed = False
        self._initialize()

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("outbox is closed")

    def _initialize(self) -> None:
        connection = sqlite3.connect(str(self.database), timeout=5.0)
        try:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise RuntimeError(f"unsupported outbox schema version: {version}")
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """CREATE TABLE IF NOT EXISTS outbox (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_key TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL,
                    payload_bytes INTEGER NOT NULL,
                    created_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    next_attempt_at INTEGER NOT NULL,
                    last_outcome TEXT
                )"""
            )
            connection.execute("PRAGMA user_version = 1")
            connection.commit()
        except BaseException:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    @contextmanager
    def _write_transaction(self) -> Iterator[sqlite3.Connection]:
        self._ensure_open()
        connection = sqlite3.connect(str(self.database), timeout=5.0)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except BaseException:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def _expire_in_transaction(
        self, connection: sqlite3.Connection, *, now: int
    ) -> list[str]:
        rows = connection.execute(
            "SELECT event_key FROM outbox WHERE expires_at <= ? ORDER BY sequence",
            (now,),
        ).fetchall()
        if rows:
            connection.execute("DELETE FROM outbox WHERE expires_at <= ?", (now,))
        return [row["event_key"] for row in rows]

    def enqueue(
        self, raw_payload: bytes, *, now: int, ttl_seconds: int
    ) -> dict[str, Any]:
        """Validate and append one event, rejecting overflow instead of evicting."""
        if not _valid_integer(now, minimum=0, maximum=MAX_SQLITE_INTEGER - MAX_TTL_SECONDS):
            return _report("INVALID_TIME", reason="NOW_OUT_OF_RANGE")
        if not _valid_integer(ttl_seconds, minimum=1, maximum=MAX_TTL_SECONDS):
            return _report("INVALID_TTL", reason="TTL_OUT_OF_RANGE")

        validation = validate_payload(raw_payload)
        if validation["result"] != "VALID":
            return _report("INVALID_REJECTED", reason=validation["reason"])

        payload_object = json.loads(raw_payload.decode("utf-8"))
        canonical = json.dumps(
            payload_object,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        canonical_bytes = canonical.encode("utf-8")
        event_key = validation["event_key"]
        if len(canonical_bytes) > self.max_payload_bytes:
            return _report(
                "PAYLOAD_TOO_LARGE",
                event_key,
                reason="CANONICAL_PAYLOAD_EXCEEDS_CONFIGURED_LIMIT",
            )

        with self._write_transaction() as connection:
            expired = self._expire_in_transaction(connection, now=now)
            previous = connection.execute(
                "SELECT payload FROM outbox WHERE event_key = ?", (event_key,)
            ).fetchone()
            if previous is not None:
                outcome = (
                    "DUPLICATE_IGNORED"
                    if previous["payload"] == canonical
                    else "CONFLICT_REVIEW"
                )
                return _report(
                    outcome,
                    event_key,
                    reason=None if outcome == "DUPLICATE_IGNORED" else "SAME_KEY_DIFFERENT_PAYLOAD",
                    expired_before_enqueue=expired,
                )

            count = connection.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]
            if count >= self.max_items:
                return _report(
                    "QUEUE_FULL",
                    event_key,
                    reason="NEWEST_EVENT_REJECTED_NO_EVICTION",
                    expired_before_enqueue=expired,
                    pending_count=count,
                )

            connection.execute(
                """INSERT INTO outbox (
                    event_key, payload, payload_bytes, created_at, expires_at,
                    attempts, next_attempt_at, last_outcome
                ) VALUES (?, ?, ?, ?, ?, 0, ?, NULL)""",
                (
                    event_key,
                    canonical,
                    len(canonical_bytes),
                    now,
                    now + ttl_seconds,
                    now,
                ),
            )
        return _report("ENQUEUED", event_key, expired_before_enqueue=expired)

    def expire_due(self, *, now: int) -> list[str]:
        """Delete expired rows and return their keys so the caller can audit them."""
        if not _valid_integer(now, minimum=0, maximum=MAX_SQLITE_INTEGER):
            raise ValueError("now must be a non-negative SQLite integer timestamp")
        with self._write_transaction() as connection:
            return self._expire_in_transaction(connection, now=now)

    def next_ready(self, *, now: int) -> dict[str, Any] | None:
        """Return the oldest unexpired event only when its backoff has elapsed.

        Ordering is strict FIFO: a backing-off head row blocks newer rows. Call
        ``expire_due`` first to remove expired rows and capture their identities.
        """
        self._ensure_open()
        if not _valid_integer(now, minimum=0, maximum=MAX_SQLITE_INTEGER):
            raise ValueError("now must be a non-negative SQLite integer timestamp")
        with closing(sqlite3.connect(str(self.database), timeout=5.0)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                """SELECT event_key, payload, created_at, expires_at,
                          attempts, next_attempt_at, last_outcome
                   FROM outbox WHERE expires_at > ? ORDER BY sequence LIMIT 1""",
                (now,),
            ).fetchone()
        if row is None or row["next_attempt_at"] > now:
            return None
        return dict(row)

    def next_due_time(self, *, now: int) -> int | None:
        """Return the head event's next retry time, or ``None`` if no live row exists."""
        self._ensure_open()
        if not _valid_integer(now, minimum=0, maximum=MAX_SQLITE_INTEGER):
            raise ValueError("now must be a non-negative SQLite integer timestamp")
        with closing(sqlite3.connect(str(self.database), timeout=5.0)) as connection:
            row = connection.execute(
                """SELECT next_attempt_at FROM outbox
                   WHERE expires_at > ? ORDER BY sequence LIMIT 1""",
                (now,),
            ).fetchone()
        return None if row is None else row[0]

    def record_outcome(
        self,
        event_key: str,
        outcome: str,
        *,
        now: int,
        base_backoff_seconds: int = 2,
        max_backoff_seconds: int = 300,
    ) -> dict[str, Any]:
        """Record a scripted next-hop result; this does not perform network I/O."""
        if outcome not in {"ACKED", "RETRYABLE", "UNCERTAIN"}:
            raise ValueError("outcome must be ACKED, RETRYABLE, or UNCERTAIN")
        if not _valid_integer(now, minimum=0, maximum=MAX_SQLITE_INTEGER):
            raise ValueError("now must be a non-negative SQLite integer timestamp")
        if (
            not _valid_integer(base_backoff_seconds, minimum=1, maximum=MAX_TTL_SECONDS)
            or not _valid_integer(max_backoff_seconds, minimum=1, maximum=MAX_TTL_SECONDS)
            or max_backoff_seconds < base_backoff_seconds
        ):
            raise ValueError("backoff values must be positive, bounded, and max >= base")

        with self._write_transaction() as connection:
            row = connection.execute(
                "SELECT attempts FROM outbox WHERE event_key = ?", (event_key,)
            ).fetchone()
            if row is None:
                raise KeyError(event_key)
            if outcome == "ACKED":
                connection.execute("DELETE FROM outbox WHERE event_key = ?", (event_key,))
                return _report(
                    "ACKED_REMOVED",
                    event_key,
                    ack_scope="PUBLISHER_TO_NEXT_HOP_ONLY",
                )

            attempts = row["attempts"] + 1
            shift = min(attempts - 1, max_backoff_seconds.bit_length())
            delay = min(max_backoff_seconds, base_backoff_seconds * (1 << shift))
            next_attempt_at = now + delay
            if next_attempt_at > MAX_SQLITE_INTEGER:
                raise ValueError("next retry timestamp exceeds SQLite integer range")
            connection.execute(
                """UPDATE outbox SET attempts = ?, next_attempt_at = ?, last_outcome = ?
                   WHERE event_key = ?""",
                (attempts, next_attempt_at, outcome, event_key),
            )
        return _report(
            outcome,
            event_key,
            attempts=attempts,
            retry_delay_seconds=delay,
            next_attempt_at=next_attempt_at,
            event_key_preserved=True,
        )

    def size(self) -> int:
        self._ensure_open()
        with closing(sqlite3.connect(str(self.database), timeout=5.0)) as connection:
            return connection.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]

    def pending_keys(self) -> list[str]:
        self._ensure_open()
        with closing(sqlite3.connect(str(self.database), timeout=5.0)) as connection:
            rows = connection.execute(
                "SELECT event_key FROM outbox ORDER BY sequence"
            ).fetchall()
        return [row[0] for row in rows]

    def close(self) -> None:
        """Prevent further use; no database connection remains open between calls."""
        self._closed = True

    def __enter__(self) -> "Outbox":
        self._ensure_open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def run_demo(database: Path) -> int:
    """Run a deterministic scripted outage/recovery simulation on local files."""
    queue = Outbox(database, max_items=3, max_payload_bytes=4096)
    now = 1_790_000_000
    try:
        fixture = HERE / "offline_telemetry.jsonl"
        with fixture.open("rb") as stream:
            for line_number, line in enumerate(stream, start=1):
                if line_number > 3:
                    print(json.dumps(_report("INPUT_REJECTED", reason="TOO_MANY_LINES")))
                    return 2
                raw = line.rstrip(b"\r\n")
                result = queue.enqueue(raw, now=now, ttl_seconds=3600)
                print(json.dumps({"phase": "enqueue", **result}, ensure_ascii=False, sort_keys=True))

        scripted_attempts: dict[str, int] = {}
        while queue.size():
            expired = queue.expire_due(now=now)
            if expired:
                print(json.dumps(_report("EXPIRED", expired_keys=expired), sort_keys=True))
            event = queue.next_ready(now=now)
            if event is None:
                due = queue.next_due_time(now=now)
                if due is None:
                    break
                now = max(now, due)
                continue

            key = event["event_key"]
            attempt_index = scripted_attempts.get(key, 0)
            outcome = "RETRYABLE" if key.endswith("/42") and attempt_index == 0 else (
                "UNCERTAIN" if key.endswith("/42") and attempt_index == 1 else "ACKED"
            )
            scripted_attempts[key] = attempt_index + 1
            result = queue.record_outcome(key, outcome, now=now)
            print(json.dumps({"phase": "publish_simulation", **result}, ensure_ascii=False, sort_keys=True))
            if "next_attempt_at" in result:
                now = result["next_attempt_at"]

        return 0 if queue.size() == 0 else 2
    except (OSError, sqlite3.Error, ValueError, KeyError) as error:
        print(f"offline outbox error: {error}", file=sys.stderr)
        return 2
    finally:
        queue.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline-only SQLite outbox and scripted recovery demonstration."
    )
    parser.add_argument(
        "--database",
        type=Path,
        help="explicit local SQLite test file; the command creates or updates it",
    )
    args = parser.parse_args()
    if args.database is not None:
        return run_demo(args.database)
    with tempfile.TemporaryDirectory(prefix="uno-q-iot-outbox-") as directory:
        return run_demo(Path(directory) / "outbox.sqlite3")


if __name__ == "__main__":
    raise SystemExit(main())
