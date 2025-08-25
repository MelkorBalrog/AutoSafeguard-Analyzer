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
from gui.architecture import SysMLDiagramWindow, SysMLObject
from mainappsrc.models.sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Block Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        self.diagram_id = diag.diag_id


class GeneralizationValidationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_common_parent_invalid(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        c = repo.create_element("Block", name="C")
        repo.create_relationship("Generalization", a.elem_id, c.elem_id)
        repo.create_relationship("Generalization", b.elem_id, c.elem_id)
        win = DummyWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=a.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=b.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(
            win, src, dst, "Generalization"
        )
        self.assertFalse(valid)

    def test_reciprocal_generalization_invalid(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Generalization", a.elem_id, b.elem_id)
        win = DummyWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=b.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=a.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(
            win, src, dst, "Generalization"
        )
        self.assertFalse(valid)

    def test_cycle_generalization_invalid(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        c = repo.create_element("Block", name="C")
        repo.create_relationship("Generalization", b.elem_id, a.elem_id)
        repo.create_relationship("Generalization", c.elem_id, b.elem_id)
        win = DummyWindow()
        src = SysMLObject(3, "Block", 0, 0, element_id=a.elem_id)
        dst = SysMLObject(4, "Block", 0, 0, element_id=c.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(
            win, src, dst, "Generalization"
        )
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
