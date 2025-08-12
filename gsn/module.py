from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

# forward import of GSNDiagram for type checking only
if True:  # pragma: no cover - forward references
    from .diagram import GSNDiagram


@dataclass
class GSNModule:
    """Container for GSN diagrams and submodules."""

    name: str
    modules: List["GSNModule"] = field(default_factory=list)
    diagrams: List["GSNDiagram"] = field(default_factory=list)
