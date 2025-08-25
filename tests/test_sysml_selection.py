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

from gui.architecture import SysMLDiagramWindow, SysMLObject


def test_sysml_find_object_strategies():
    win = object.__new__(SysMLDiagramWindow)
    obj = SysMLObject(
        obj_id=1,
        obj_type="Block",
        x=50,
        y=50,
        element_id=None,
        width=40,
        height=20,
        properties={},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )
    win.objects = [obj]
    win.zoom = 1.0

    assert win._find_object_strategy1(50, 50) is obj
    assert win._find_object_strategy2(50, 50) is obj
    assert win._find_object_strategy3(50, 50) is obj
    assert win._find_object_strategy4(50, 50) is obj
    assert win.find_object(50, 50) is obj

