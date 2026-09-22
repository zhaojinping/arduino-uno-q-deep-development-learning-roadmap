"""Regression checks for the chapter's local simulations."""
from __future__ import annotations

import asyncio
from dataclasses import replace
import unittest

from connection_owner import ConnectionOwner, FakeConnector, Session
from recovery_policy import Delivery, Request, ResultRecord, decide_recovery


class ControlledConnector(FakeConnector):
    def __init__(self) -> None:
        super().__init__(failures=0)
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.block = True

    async def open_and_probe(self, generation: int) -> Session:
        self.attempts += 1
        self.started.set()
        if self.block:
            await self.release.wait()
        return Session(generation)


class ConnectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_callers_share_one_recovery(self) -> None:
        connector = FakeConnector(failures=2)
        owner = ConnectionOwner(connector)
        sessions = await asyncio.gather(*(owner.ready() for _ in range(12)))
        self.assertTrue(all(item is sessions[0] for item in sessions))
        self.assertEqual(connector.attempts, 3)
        self.assertEqual(len(owner.delays), 2)
        self.assertTrue(0 <= owner.delays[0] <= 0.01)
        self.assertTrue(0 <= owner.delays[1] <= 0.02)

    async def test_ready_session_reused_without_new_open(self) -> None:
        connector = FakeConnector(failures=0)
        owner = ConnectionOwner(connector)
        first = await owner.ready()
        self.assertIs(await owner.ready(), first)
        self.assertEqual(connector.attempts, 1)

    async def test_stale_failure_cannot_clear_new_generation(self) -> None:
        owner = ConnectionOwner(FakeConnector(failures=0))
        first = await owner.ready()
        self.assertTrue(owner.invalidate(first.generation))
        second = await owner.ready()
        self.assertEqual(second.generation, first.generation + 1)
        self.assertFalse(owner.invalidate(first.generation))
        self.assertIs(await owner.ready(), second)

    async def test_exhaustion_does_not_restart_for_each_waiter(self) -> None:
        connector = FakeConnector(failures=100)
        owner = ConnectionOwner(connector)
        results = await asyncio.gather(
            *(owner.ready() for _ in range(8)), return_exceptions=True
        )
        self.assertTrue(all(isinstance(item, ConnectionError) for item in results))
        self.assertEqual(connector.attempts, 3)

    async def test_contract_mismatch_is_not_retried(self) -> None:
        connector = FakeConnector(failures=0, contract="unsupported")
        owner = ConnectionOwner(connector)
        with self.assertRaises(ValueError):
            await owner.ready()
        with self.assertRaises(ConnectionError):
            await owner.ready()
        self.assertEqual(connector.attempts, 1)

    async def test_cancellation_pauses_shared_cycle_and_releases_lock(self) -> None:
        connector = ControlledConnector()
        owner = ConnectionOwner(connector)
        pending = asyncio.create_task(owner.ready())
        await connector.started.wait()
        waiters = [asyncio.create_task(owner.ready()) for _ in range(5)]
        pending.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await pending
        results = await asyncio.wait_for(
            asyncio.gather(*waiters, return_exceptions=True), timeout=1.0
        )
        self.assertTrue(all(isinstance(item, ConnectionError) for item in results))
        self.assertEqual(connector.attempts, 1)
        connector.block = False
        # Explicit creation of a new owner represents an approved new cycle.
        session = await ConnectionOwner(connector).ready()
        self.assertEqual(session.generation, 1)
        self.assertEqual(connector.attempts, 2)

    async def test_handshake_timeout_pauses_after_budget(self) -> None:
        connector = ControlledConnector()
        owner = ConnectionOwner(connector, max_attempts=1)
        with self.assertRaises(asyncio.TimeoutError):
            await owner.ready()
        with self.assertRaises(ConnectionError):
            await owner.ready()
        self.assertEqual(connector.attempts, 1)

    def test_invalid_attempt_budget_rejected(self) -> None:
        for limit in (0, -1, True, 1.5, 11):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                ConnectionOwner(FakeConnector(), max_attempts=limit)


class RecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = Request(
            "sim-device", "operation-A", "digest-A", Delivery.MAYBE_SENT, 20.0
        )
        self.record = ResultRecord("sim-device", "operation-A", "digest-A", "APPLIED")

    def decide(self, request=None, record=None, ready=True, now=10.0):
        return decide_recovery(
            request or self.request, record, ready=ready, now=now
        )

    def test_reconnected_request_with_lost_response_is_query_only(self) -> None:
        self.assertEqual(self.decide(), "QUERY_ONLY")

    def test_not_found_is_not_permission_to_replay(self) -> None:
        request = replace(self.request, replay_safe=True)
        self.assertEqual(
            self.decide(request, replace(self.record, state="NOT_FOUND")),
            "KEEP_UNKNOWN",
        )

    def test_late_authoritative_success_resolves_without_replay(self) -> None:
        self.assertEqual(
            self.decide(record=self.record, ready=False, now=30.0), "STOP_APPLIED"
        )

    def test_identity_mismatch_does_not_complete_request(self) -> None:
        for field in ("target", "operation_key", "payload_digest"):
            with self.subTest(field=field):
                record = replace(self.record, **{field: "mismatch"})
                self.assertEqual(self.decide(record=record), "KEEP_UNKNOWN")

    def test_final_not_applied_requires_replay_contract(self) -> None:
        record = replace(self.record, state="NOT_APPLIED_FINAL")
        self.assertEqual(self.decide(record=record), "MANUAL_REVIEW")
        self.assertEqual(
            self.decide(replace(self.request, replay_safe=True), record),
            "RESUBMIT_SAME_KEY",
        )

    def test_expired_request_never_resubmitted(self) -> None:
        record = replace(self.record, state="NOT_APPLIED_FINAL")
        request = replace(self.request, replay_safe=True)
        self.assertEqual(self.decide(request, record, now=20.0), "STOP_NOT_APPLIED")
        self.assertEqual(self.decide(request, now=20.0), "KEEP_UNKNOWN")
        unsent = replace(request, delivery=Delivery.NOT_SENT)
        self.assertEqual(self.decide(unsent, now=20.0), "STOP_EXPIRED")

    def test_unsent_waits_for_ready_then_gets_first_attempt(self) -> None:
        request = replace(self.request, delivery=Delivery.NOT_SENT)
        self.assertEqual(self.decide(request, ready=False), "WAIT_READY")
        self.assertEqual(self.decide(request), "SEND_FIRST_ATTEMPT")

    def test_in_progress_or_unsupported_record_never_replayed(self) -> None:
        self.assertEqual(
            self.decide(record=replace(self.record, state="IN_PROGRESS")),
            "WAIT_AND_QUERY",
        )
        self.assertEqual(
            self.decide(record=replace(self.record, state="unknown-v2")),
            "KEEP_UNKNOWN",
        )

    def test_invalid_time_and_delivery_fail_closed(self) -> None:
        for now in (float("nan"), float("inf")):
            with self.subTest(now=now), self.assertRaises(ValueError):
                self.decide(now=now)
        with self.assertRaises(ValueError):
            self.decide(replace(self.request, expires_at=float("nan")))
        with self.assertRaises(ValueError):
            self.decide(replace(self.request, delivery="MAYBE_SENT"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
