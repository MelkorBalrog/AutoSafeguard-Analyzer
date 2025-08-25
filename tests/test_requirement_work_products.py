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

import types

from analysis.models import REQUIREMENT_TYPE_OPTIONS
from gui.architecture import GovernanceDiagramWindow, SysMLObject
from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from AutoML import AutoMLApp


def _fmt(req: str) -> str:
    return " ".join(
        word.upper() if word.isupper() else word.capitalize() for word in req.split()
    )


def test_work_product_created_for_each_requirement_type():
    for req in REQUIREMENT_TYPE_OPTIONS:
        name = f"{_fmt(req)} Requirement Specification"
        assert name in AutoMLApp.WORK_PRODUCT_INFO


def test_add_requirement_work_product(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Gov")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = [
        SysMLObject(
            1,
            "System Boundary",
            0.0,
            0.0,
            width=200.0,
            height=150.0,
            properties={"name": "System Design (Item Definition)"},
        )
    ]
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    added = []
    win.app = types.SimpleNamespace(enable_work_product=lambda name, *, refresh=True: added.append(name))

    name = f"{_fmt(REQUIREMENT_TYPE_OPTIONS[3])} Requirement Specification"

    class FakeDialog:
        def __init__(self, *args, **kwargs):
            self.selection = name

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", FakeDialog)

    win.add_work_product()

    assert added == [name]
    assert any(o.properties.get("name") == name for o in win.objects)

