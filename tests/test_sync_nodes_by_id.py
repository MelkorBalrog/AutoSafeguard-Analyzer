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
import os
import sys
import types
from unittest.mock import patch

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import AutoMLApp, FaultTreeNode


class SyncNodesTests(unittest.TestCase):
    def setUp(self):
        self.app = AutoMLApp.__new__(AutoMLApp)
        self.original = FaultTreeNode("Orig", "BASIC EVENT")
        self.clone1 = FaultTreeNode("Clone1", "BASIC EVENT")
        self.clone1.is_primary_instance = False
        self.clone1.original = self.original
        self.clone1.display_label = "Orig (clone)"
        self.clone2 = FaultTreeNode("Clone2", "BASIC EVENT")
        self.clone2.is_primary_instance = False
        self.clone2.original = self.original
        self.clone2.display_label = "Orig (clone)"
        self.app.get_all_nodes = lambda *_args, **_kwargs: [self.original, self.clone1, self.clone2]
        self.app.get_all_fmea_entries = lambda: []
        self.app.root_node = self.original

    def test_original_updates_clones(self):
        self.original.description = "new desc"
        self.app.sync_nodes_by_id(self.original)
        self.assertEqual(self.clone1.description, "new desc")
        self.assertEqual(self.clone2.description, "new desc")

    def test_clone_updates_all(self):
        self.clone1.description = "clone desc"
        self.clone1.display_label = "New Label (clone)"
        self.app.sync_nodes_by_id(self.clone1)
        self.assertEqual(self.original.description, "clone desc")
        self.assertEqual(self.clone2.description, "clone desc")
        self.assertEqual(self.original.display_label, "New Label")
        self.assertEqual(self.clone2.display_label, "New Label (clone)")
        self.assertEqual(self.clone1.display_label, "New Label (clone)")

    @patch("AutoML.simpledialog.askstring", return_value="patched desc")
    def test_edit_description_propagates(self, mock_ask):
        self.app.update_views = lambda: None
        self.app.selected_node = self.clone1
        self.app.edit_description()
        self.assertEqual(self.original.description, "patched desc")
        self.assertEqual(self.clone2.description, "patched desc")
        self.assertEqual(self.clone1.description, "patched desc")


if __name__ == "__main__":
    unittest.main()
