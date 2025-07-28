# Author: Miguel Marina <karel.capek.robotics@gmail.com>
"""Utility helpers for analysis package."""

from typing import List


def append_unique_insensitive(items: List[str], name: str) -> None:
    """Append ``name`` to ``items`` if not already present (case-insensitive)."""
    if not name:
        return
    name = name.strip()
    if not name:
        return
    lower = name.lower()
    for existing in items:
        if existing.lower() == lower:
            return
    items.append(name)
