"""Local simulation of a shared connection owner; no network or hardware."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class Session:
    generation: int
    contract: str = "demo-v1"


class FakeConnector:
    def __init__(self, failures: int = 2, contract: str = "demo-v1") -> None:
        self.failures = failures
        self.contract = contract
        self.attempts = 0

    async def open_and_probe(self, generation: int) -> Session:
        self.attempts += 1
        await asyncio.sleep(0)
        if self.attempts <= self.failures:
            raise ConnectionError("simulated unavailable endpoint")
        return Session(generation, self.contract)


class ConnectionOwner:
    def __init__(self, connector: FakeConnector, max_attempts: int = 3) -> None:
        if type(max_attempts) is not int or not 1 <= max_attempts <= 10:
            raise ValueError("max_attempts must be an integer from 1 to 10")
        self.connector = connector
        self.max_attempts = max_attempts
        self._lock = asyncio.Lock()
        self._session: Session | None = None
        self._generation = 0
        self._paused = False
        self._attempts = 0
        self._random = Random(7)  # Fixed seed only for reproducible teaching.
        self.delays: list[float] = []

    async def ready(self) -> Session:
        async with self._lock:
            if self._paused:
                raise ConnectionError("recovery paused")
            if self._session is not None:
                return self._session
            try:
                while self._attempts < self.max_attempts:
                    self._attempts += 1
                    try:
                        candidate = await asyncio.wait_for(
                            self.connector.open_and_probe(self._generation + 1),
                            timeout=0.5,
                        )
                    except (ConnectionError, asyncio.TimeoutError):
                        if self._attempts == self.max_attempts:
                            raise
                        ceiling = min(0.04, 0.01 * (2 ** (self._attempts - 1)))
                        delay = self._random.uniform(0.0, ceiling)
                        self.delays.append(delay)
                        await asyncio.sleep(delay)
                        continue
                    if candidate.contract != "demo-v1":
                        raise ValueError("contract mismatch")
                    self._generation = candidate.generation
                    self._session = candidate
                    return candidate
            except asyncio.CancelledError:
                self._paused = True
                raise
            except Exception:
                self._paused = True
                raise
        raise RuntimeError("unreachable")

    def invalidate(self, observed_generation: int) -> bool:
        # Called on the same event loop; a stale failure cannot clear a new session.
        if self._session is None:
            return False
        if self._session.generation != observed_generation:
            return False
        self._session = None
        self._attempts = 0
        return True


async def main() -> None:
    connector = FakeConnector(failures=2)
    owner = ConnectionOwner(connector)
    sessions = await asyncio.gather(*(owner.ready() for _ in range(6)))
    assert all(session is sessions[0] for session in sessions)
    assert connector.attempts == 3
    print(f"SIMULATED shared=6 attempts={connector.attempts} generation=1")
    owner.invalidate(sessions[0].generation)
    current = await owner.ready()
    stale_cleared = owner.invalidate(sessions[0].generation)
    assert current.generation == 2 and not stale_cleared
    print(f"SIMULATED generation={current.generation} stale_cleared={stale_cleared}")


if __name__ == "__main__":
    asyncio.run(main())
