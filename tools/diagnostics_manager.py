from __future__ import annotations

"""Background diagnostics utilities for monitoring tool integrity.

This module provides several experimental diagnostics manager
implementations.  Each variant offers a different strategy for detecting
integrity issues in running operations.  The intent is to evaluate which
approach best fits the tool before wider integration.

The following managers are available:

* :class:`PollingDiagnosticsManager` -- periodically executes registered
  check callables on a background thread.
* :class:`EventDiagnosticsManager` -- collects explicit success/failure
  events from the application.
* :class:`PassiveDiagnosticsManager` -- exposes a simple ``run_check``
  method for ad-hoc validation.
* :class:`AsyncDiagnosticsManager` -- awaits registered asynchronous
  check coroutines.

Each manager raises :class:`DiagnosticError` when one or more checks
fail, allowing callers to decide how to handle integrity issues.
"""

from dataclasses import dataclass, field
import asyncio
import queue
import threading
import time
from typing import Awaitable, Callable, Dict, List, Optional


class DiagnosticError(RuntimeError):
    """Raised when a diagnostics check reports failure."""


@dataclass
class DiagnosticsManagerBase:
    """Common interface for diagnostics managers."""

    errors: List[str] = field(default_factory=list)

    def raise_errors(self) -> None:
        """Raise :class:`DiagnosticError` if any errors were collected."""
        if self.errors:
            raise DiagnosticError("; ".join(self.errors))


class PollingDiagnosticsManager(DiagnosticsManagerBase):
    """Polls registered checks on a background thread."""

    def __init__(self, interval: float = 0.1) -> None:
        super().__init__()
        self.interval = interval
        self._checks: Dict[str, Callable[[], bool]] = {}
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def register_check(self, name: str, func: Callable[[], bool]) -> None:
        self._checks[name] = func

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            for name, func in list(self._checks.items()):
                try:
                    if not func():
                        self.errors.append(name)
                except Exception as exc:  # pragma: no cover - rare
                    self.errors.append(f"{name}: {exc}")
            time.sleep(self.interval)

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join()


class EventDiagnosticsManager(DiagnosticsManagerBase):
    """Collects explicit success/failure events from the application."""

    def __init__(self) -> None:
        super().__init__()
        self._queue: "queue.Queue[tuple[str, bool]]" = queue.Queue()

    def record_event(self, name: str, ok: bool) -> None:
        self._queue.put((name, ok))

    def process_events(self) -> None:
        while True:
            try:
                name, ok = self._queue.get_nowait()
            except queue.Empty:
                break
            if not ok:
                self.errors.append(name)


class PassiveDiagnosticsManager(DiagnosticsManagerBase):
    """Runs checks on demand without background activity."""

    def run_check(self, name: str, func: Callable[[], bool]) -> None:
        try:
            if not func():
                self.errors.append(name)
        except Exception as exc:  # pragma: no cover - rare
            self.errors.append(f"{name}: {exc}")


class AsyncDiagnosticsManager(DiagnosticsManagerBase):
    """Await registered asynchronous checks."""

    def __init__(self) -> None:
        super().__init__()
        self._checks: Dict[str, Callable[[], Awaitable[bool]]] = {}

    def register_check(self, name: str, coro: Callable[[], Awaitable[bool]]) -> None:
        self._checks[name] = coro

    async def run_once(self) -> None:
        for name, coro in list(self._checks.items()):
            try:
                if not await coro():
                    self.errors.append(name)
            except Exception as exc:  # pragma: no cover - rare
                self.errors.append(f"{name}: {exc}")


__all__ = [
    "DiagnosticError",
    "DiagnosticsManagerBase",
    "PollingDiagnosticsManager",
    "EventDiagnosticsManager",
    "PassiveDiagnosticsManager",
    "AsyncDiagnosticsManager",
]
