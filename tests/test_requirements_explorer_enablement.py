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

import sys
import types
from pathlib import Path

import tkinter as tk

sys.path.append(str(Path(__file__).resolve().parents[1]))

from AutoML import AutoMLApp


class DummyMenu:
    def __init__(self):
        self.states = {}

    def entryconfig(self, idx, state=tk.DISABLED):
        self.states[idx] = state


def test_explorer_menu_enabled_with_work_product():
    menu = DummyMenu()
    app = types.SimpleNamespace(
        WORK_PRODUCT_INFO={
            "Requirement Specification": (
                "Area",
                "Tool",
                "show_requirements_editor",
            )
        },
        enable_process_area=lambda area: None,
        tool_actions={},
        tool_listboxes={},
        work_product_menus={"Requirement Specification": [(menu, 0), (menu, 1), (menu, 2)]},
        enabled_work_products=set(),
        WORK_PRODUCT_PARENTS={},
        tool_to_work_product={},
        update_views=lambda: None,
    )

    AutoMLApp.enable_work_product(app, "Requirement Specification", refresh=False)

    assert menu.states[2] == tk.NORMAL

