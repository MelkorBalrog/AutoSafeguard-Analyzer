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

Each manager attempts recovery and mitigation to correct detected
issues at runtime.  If neither strategy succeeds, a
:class:`DiagnosticError` is raised so callers can react to the
unhandled fault.
"""

from dataclasses import dataclass, field
import asyncio
import queue
import threading
import time
from typing import Awaitable, Callable, Dict, List, Optional, Tuple


class DiagnosticError(RuntimeError):
    """Raised when a diagnostics check reports failure."""


@dataclass
class DiagnosticsManagerBase:
    """Common interface for diagnostics managers."""

    errors: List[str] = field(default_factory=list)
    notifications: List[str] = field(default_factory=list)

    def _handle_failure(
        self,
        name: str,
        recoverable: bool,
        recover: Optional[Callable[[], bool]] = None,
        mitigate: Optional[Callable[[], Optional[str]]] = None,
    ) -> None:
        """Attempt recovery or mitigation for a failed check."""
        if self._attempt_recover(name, recoverable, recover):
            return
        if self._attempt_mitigate(name, mitigate):
            return
        self.errors.append(name)

    def _attempt_recover(
        self,
        name: str,
        recoverable: bool,
        recover: Optional[Callable[[], bool]],
    ) -> bool:
        if recoverable and recover:
            try:
                return bool(recover())
            except Exception as exc:  # pragma: no cover - rare
                self.errors.append(f"{name}: recovery error: {exc}")
        return False

    def _attempt_mitigate(
        self,
        name: str,
        mitigate: Optional[Callable[[], Optional[str]]],
    ) -> bool:
        if mitigate:
            try:
                msg = mitigate()
                if msg:
                    self.notifications.append(msg)
                return True
            except Exception as exc:  # pragma: no cover - rare
                self.errors.append(f"{name}: mitigation error: {exc}")
        return False

    def raise_errors(self) -> None:
        """Raise :class:`DiagnosticError` if any errors were collected."""
        if self.errors:
            raise DiagnosticError("; ".join(self.errors))


class PollingDiagnosticsManager(DiagnosticsManagerBase):
    """Polls registered checks on a background thread."""

    def __init__(self, interval: float = 0.1) -> None:
        super().__init__()
        self.interval = interval
        self._checks: Dict[str, Tuple[Callable[[], bool], bool, Optional[Callable[[], bool]], Optional[Callable[[], Optional[str]]]]] = {}
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def register_check(
        self,
        name: str,
        func: Callable[[], bool],
        *,
        recover: Optional[Callable[[], bool]] = None,
        mitigate: Optional[Callable[[], Optional[str]]] = None,
        recoverable: bool = True,
    ) -> None:
        self._checks[name] = (func, recoverable, recover, mitigate)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            for name, (func, recoverable, recover, mitigate) in list(self._checks.items()):
                try:
                    if not func():
                        self._handle_failure(name, recoverable, recover, mitigate)
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
        self._meta: Dict[str, Tuple[bool, Optional[Callable[[], bool]], Optional[Callable[[], Optional[str]]]]] = {}

    def register_check(
        self,
        name: str,
        *,
        recover: Optional[Callable[[], bool]] = None,
        mitigate: Optional[Callable[[], Optional[str]]] = None,
        recoverable: bool = True,
    ) -> None:
        self._meta[name] = (recoverable, recover, mitigate)

    def record_event(self, name: str, ok: bool) -> None:
        self._queue.put((name, ok))

    def process_events(self) -> None:
        while True:
            try:
                name, ok = self._queue.get_nowait()
            except queue.Empty:
                break
            if not ok:
                recoverable, recover, mitigate = self._meta.get(name, (True, None, None))
                self._handle_failure(name, recoverable, recover, mitigate)


class PassiveDiagnosticsManager(DiagnosticsManagerBase):
    """Runs checks on demand without background activity."""

    def run_check(
        self,
        name: str,
        func: Callable[[], bool],
        *,
        recover: Optional[Callable[[], bool]] = None,
        mitigate: Optional[Callable[[], Optional[str]]] = None,
        recoverable: bool = True,
    ) -> None:
        try:
            if not func():
                self._handle_failure(name, recoverable, recover, mitigate)
        except Exception as exc:  # pragma: no cover - rare
            self.errors.append(f"{name}: {exc}")


class AsyncDiagnosticsManager(DiagnosticsManagerBase):
    """Await registered asynchronous checks."""

    def __init__(self) -> None:
        super().__init__()
        self._checks: Dict[str, Tuple[Callable[[], Awaitable[bool]], bool, Optional[Callable[[], bool]], Optional[Callable[[], Optional[str]]]]] = {}

    def register_check(
        self,
        name: str,
        coro: Callable[[], Awaitable[bool]],
        *,
        recover: Optional[Callable[[], bool]] = None,
        mitigate: Optional[Callable[[], Optional[str]]] = None,
        recoverable: bool = True,
    ) -> None:
        self._checks[name] = (coro, recoverable, recover, mitigate)

    async def run_once(self) -> None:
        for name, (coro, recoverable, recover, mitigate) in list(self._checks.items()):
            try:
                if not await coro():
                    self._handle_failure(name, recoverable, recover, mitigate)
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
