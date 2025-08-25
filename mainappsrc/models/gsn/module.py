# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
