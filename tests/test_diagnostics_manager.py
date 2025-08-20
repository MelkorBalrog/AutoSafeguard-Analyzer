import asyncio
import time
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tools.diagnostics_manager import (
    AsyncDiagnosticsManager,
    DiagnosticError,
    EventDiagnosticsManager,
    PassiveDiagnosticsManager,
    PollingDiagnosticsManager,
)


def test_polling_manager_detects_failure() -> None:
    manager = PollingDiagnosticsManager(interval=0.01)
    manager.register_check("fail", lambda: False)
    manager.start()
    time.sleep(0.05)
    manager.stop()
    with pytest.raises(DiagnosticError):
        manager.raise_errors()


def test_event_manager_records_error() -> None:
    manager = EventDiagnosticsManager()
    manager.record_event("fail", False)
    manager.process_events()
    with pytest.raises(DiagnosticError):
        manager.raise_errors()


def test_passive_manager_runs_checks() -> None:
    manager = PassiveDiagnosticsManager()
    manager.run_check("fail", lambda: False)
    with pytest.raises(DiagnosticError):
        manager.raise_errors()


def test_async_manager_detects_failure() -> None:
    manager = AsyncDiagnosticsManager()

    async def bad() -> bool:
        return False

    manager.register_check("fail", bad)
    asyncio.run(manager.run_once())
    with pytest.raises(DiagnosticError):
        manager.raise_errors()
