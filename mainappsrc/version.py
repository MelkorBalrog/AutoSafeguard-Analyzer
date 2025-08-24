from __future__ import annotations

"""Central version management for AutoML.

This module exposes a :data:`VERSION` constant derived from the first line of
``README.md``.  Having a dedicated module allows both the GUI wrapper and
command line launcher to share the same version information without importing
large GUI dependencies.
"""

from pathlib import Path


def get_version() -> str:
    """Read the tool version from the repository README.

    The README is located one directory above this module.
    """

    try:
        readme = Path(__file__).resolve().parents[1] / "README.md"
        with readme.open("r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line.lower().startswith("version:"):
                return first_line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "Unknown"


VERSION = get_version()

__all__ = ["VERSION", "get_version"]
