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
from mainappsrc.models.sysml.sysml_repository import SysMLRepository, SysMLDiagram


class UndoMoveIgnoreModifiedTests(unittest.TestCase):
    def _prepare_repo(self):
        SysMLRepository.reset_instance()
        repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Use Case Diagram")
        repo.diagrams[diag.diag_id] = diag
        diag.objects.append({"obj_id": 1, "obj_type": "Block", "x": 0.0, "y": 0.0, "modified": "t0"})
        return repo, diag

    def test_modified_fields_do_not_create_extra_states(self):
        for strat in ("v1", "v2", "v3", "v4"):
            with self.subTest(strategy=strat):
                repo, diag = self._prepare_repo()
                base_len = len(repo._undo_stack)
                # initial state
                repo.push_undo_state(strategy=strat)
                for i in range(1, 5):
                    diag.objects[0]["x"] = float(i)
                    diag.objects[0]["y"] = float(i)
                    diag.objects[0]["modified"] = f"t{i}"
                    repo.push_undo_state(strategy=strat)
                self.assertEqual(len(repo._undo_stack), base_len + 2)


if __name__ == "__main__":
    unittest.main()
