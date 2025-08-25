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

import types
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Provide a minimal Pillow stub so importing AutoML does not fail.
pil = types.ModuleType("PIL")
pil.Image = types.ModuleType("Image")
pil.ImageTk = types.ModuleType("ImageTk")
pil.ImageDraw = types.ModuleType("ImageDraw")
pil.ImageFont = types.ModuleType("ImageFont")
sys.modules.setdefault("PIL", pil)
sys.modules.setdefault("PIL.Image", pil.Image)
sys.modules.setdefault("PIL.ImageTk", pil.ImageTk)
sys.modules.setdefault("PIL.ImageDraw", pil.ImageDraw)
sys.modules.setdefault("PIL.ImageFont", pil.ImageFont)

from analysis.models import HaraDoc, HaraEntry
from AutoML import AutoMLApp


def test_update_hazard_list_uses_entry_severity():
    """Hazard severities from HARA entries should populate the hazard list."""
    entry = HaraEntry(
        malfunction="m",
        hazard="HZ",
        scenario="scen",
        severity=3,
        sev_rationale="",
        controllability=1,
        cont_rationale="",
        exposure=1,
        exp_rationale="",
        asil="",
        safety_goal="",
    )
    hara = HaraDoc("RA", [], [entry])
    app = types.SimpleNamespace(
        hara_docs=[hara],
        hazop_docs=[],
        hazard_severity={},
        hazards=[],
    )

    AutoMLApp.update_hazard_list(app)

    assert app.hazard_severity["HZ"] == 3
    assert "HZ" in app.hazards
