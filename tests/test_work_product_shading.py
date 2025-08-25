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
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import types
from gui.architecture import GovernanceDiagramWindow, SysMLObject

class DummyCanvas:
    def create_polygon(self, *a, **k):
        pass
    def create_line(self, *a, **k):
        pass
    def create_text(self, *a, **k):
        pass
    def create_arc(self, *a, **k):
        pass
    def create_image(self, *a, **k):
        pass


def test_work_product_shape_uses_gradient():
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.canvas = DummyCanvas()
    win.zoom = 1
    win.font = None
    win.selected_objs = []
    win.repo = types.SimpleNamespace(get_linked_diagram=lambda x: None, diagrams={})
    captured = []
    win._draw_gradient_rect = lambda *args, **kwargs: captured.append(args)
    obj = SysMLObject(obj_id=1, obj_type="Work Product", x=0, y=0, properties={})
    win.draw_object(obj)
    assert captured, "Work Product shape should use gradient fill"
