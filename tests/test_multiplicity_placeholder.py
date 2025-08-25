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
from unittest.mock import patch
from gui import architecture
from gui.architecture import InternalBlockDiagramWindow, SysMLObject
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class DummyWindow:
    _get_part_name = InternalBlockDiagramWindow._get_part_name
    def __init__(self, diagram):
        self.repo = SysMLRepository.get_instance()
        self.diagram_id = diagram.diag_id
        self.objects = []
        self.connections = []
        self.app = None
    def redraw(self):
        pass
    def _sync_to_repository(self):
        diag = self.repo.diagrams[self.diagram_id]
        diag.objects = [o.__dict__ for o in self.objects]

class MultiplicityPlaceholderTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_placeholder_listed_and_creates_part(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Composite Aggregation", a.elem_id, b.elem_id)
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id)
        obj = next(o for o in ibd.objects if o.get("obj_type") == "Part")
        repo.elements[obj["element_id"]].name = "X"
        rel = next(r for r in repo.relationships if r.rel_type == "Composite Aggregation")
        rel.properties["multiplicity"] = "2"
        win = DummyWindow(ibd)
        for data in ibd.objects:
            win.objects.append(SysMLObject(**data))
        captured = []
        class DummyDialog:
            def __init__(self, parent, names, visible, hidden):
                captured.extend(names)
                self.result = names
        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', DummyDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)
        parts = [o for o in repo.diagrams[ibd.diag_id].objects if o.get("obj_type") == "Part"]
        self.assertGreaterEqual(len(parts), 1)
        self.assertTrue(any(n.startswith(" : B [") for n in captured))

if __name__ == "__main__":
    unittest.main()
