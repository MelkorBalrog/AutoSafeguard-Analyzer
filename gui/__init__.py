# Shared GUI helpers

from __future__ import annotations


def format_name_with_phase(name: str, phase: str | None) -> str:
    """Return ``name`` with ``" (phase)"`` appended when ``phase`` is set."""

    if phase:
        return f"{name} ({phase})" if name else f"({phase})"
    return name
