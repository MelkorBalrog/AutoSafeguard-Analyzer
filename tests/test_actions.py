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

# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

class ActionNameTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_activity_actions(self):
        diag = self.repo.create_diagram("Activity Diagram", name="MainFlow")
        act = self.repo.create_element("Action", name="DoThing")
        obj = {
            "obj_id": 1,
            "obj_type": "Action",
            "x": 10,
            "y": 10,
            "element_id": act.elem_id,
            "width": 20,
            "height": 20,
            "properties": {"name": "DoThing"},
        }
        diag.objects.append(obj)
        names = self.repo.get_activity_actions()
        self.assertIn("MainFlow", names)
        self.assertIn("DoThing", names)

    def test_activity_actions_from_elements(self):
        diag = self.repo.create_diagram("Activity Diagram", name="Flow")
        act = self.repo.create_element("Action", name="Act")
        self.repo.add_element_to_diagram(diag.diag_id, act.elem_id)
        names = self.repo.get_activity_actions()
        self.assertIn("Flow", names)
        self.assertIn("Act", names)

    def test_call_behavior_action_names(self):
        diag = self.repo.create_diagram("Activity Diagram", name="Top")
        cba = self.repo.create_element("CallBehaviorAction", name="Invoke")
        diag.objects.append({
            "obj_id": 2,
            "obj_type": "CallBehaviorAction",
            "x": 0,
            "y": 0,
            "element_id": cba.elem_id,
            "properties": {"name": "Invoke"},
        })
        names = self.repo.get_activity_actions()
        self.assertIn("Invoke", names)


if __name__ == '__main__':
    unittest.main()
