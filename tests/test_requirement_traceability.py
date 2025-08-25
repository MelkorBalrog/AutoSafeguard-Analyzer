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

from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from gui.architecture import SysMLObject
from gui.toolboxes import find_requirement_traces
from analysis.models import global_requirements


class RequirementTraceabilityTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        global_requirements.clear()
        self.repo = SysMLRepository.get_instance()

    def test_find_requirement_traces_returns_diagram_objects(self):
        global_requirements["R1"] = {"id": "R1", "text": "Req1"}
        elem = self.repo.create_element("Block", name="B1")
        diag = self.repo.create_diagram("Block Definition Diagram", name="BD")
        self.repo.add_element_to_diagram(diag.diag_id, elem.elem_id)
        obj = SysMLObject(
            1,
            "Block",
            0,
            0,
            element_id=elem.elem_id,
            properties={"name": "B1"},
            requirements=[global_requirements["R1"]],
        )
        diag.objects.append(obj.__dict__)
        traces = find_requirement_traces("R1")
        self.assertIn("BD:B1", traces)


if __name__ == "__main__":
    unittest.main()

