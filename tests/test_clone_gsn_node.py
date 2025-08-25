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
import types
import os
import sys

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import AutoMLApp
from mainappsrc.models.gsn.nodes import GSNNode


class CloneGSNNodeTests(unittest.TestCase):
    def test_clone_preserves_gsn_node_attributes(self):
        app = AutoMLApp.__new__(AutoMLApp)
        original = GSNNode("goal", "Goal")
        clone = app.clone_node_preserving_id(original)
        self.assertIsInstance(clone, GSNNode)
        self.assertEqual(clone.user_name, original.user_name)
        self.assertIs(clone.original, original)
        self.assertEqual(clone.x, original.x + 100)
        self.assertEqual(clone.y, original.y + 100)
        self.assertNotEqual(clone.unique_id, original.unique_id)

    def test_clone_context_attaches_to_parent(self):
        app = AutoMLApp.__new__(AutoMLApp)
        parent = GSNNode("Parent", "Goal")
        ctx = GSNNode("Ctx", "Context")
        clone = app.clone_node_preserving_id(ctx, parent)
        self.assertIn(clone, parent.context_children)
        self.assertIn(parent, clone.parents)


if __name__ == "__main__":  # pragma: no cover - manual test execution
    unittest.main()
