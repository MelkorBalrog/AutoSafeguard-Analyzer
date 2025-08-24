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

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Return a serialisable representation of this module."""
        return {
            "name": self.name,
            "modules": [m.to_dict() for m in self.modules],
            "diagrams": [d.to_dict() for d in self.diagrams],
        }

    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict) -> "GSNModule":
        mod = cls(data.get("name", ""))
        mod.modules = [cls.from_dict(m) for m in data.get("modules", [])]
        from .diagram import GSNDiagram  # local import to avoid cycle
        mod.diagrams = [GSNDiagram.from_dict(d) for d in data.get("diagrams", [])]
        return mod
