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

import unittest
import types, sys
sys.modules.setdefault('PIL', types.ModuleType('PIL'))
sys.modules.setdefault('PIL.Image', types.ModuleType('PIL.Image'))
sys.modules.setdefault('PIL.ImageDraw', types.ModuleType('PIL.ImageDraw'))
sys.modules.setdefault('PIL.ImageFont', types.ModuleType('PIL.ImageFont'))
sys.modules.setdefault('PIL.ImageTk', types.ModuleType('PIL.ImageTk'))

from AutoML import AutoMLApp, FaultTreeNode


class FunctionalInsufficiencySubtypeTests(unittest.TestCase):
    def test_subtype_nodes_listed(self):
        app = AutoMLApp.__new__(AutoMLApp)
        top = FaultTreeNode("TE", "TOP EVENT")

        fi_type = FaultTreeNode("FI1", "Functional Insufficiency")
        fi_subtype = FaultTreeNode("FI2", "RIGOR LEVEL")
        fi_subtype.input_subtype = "Functional Insufficiency"

        fi_type.parents.append(top)
        fi_subtype.parents.append(top)
        top.children.extend([fi_type, fi_subtype])
        app.top_events = [top]

        fi_nodes = app.get_all_functional_insufficiencies()
        self.assertEqual({fi_type, fi_subtype}, set(fi_nodes))


if __name__ == "__main__":
    unittest.main()
