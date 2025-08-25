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

from gui.architecture import (
    GovernanceDiagramWindow,
    SysMLObjectDialog,
    SysMLObject,
)
from mainappsrc.models.sysml.sysml_repository import SysMLRepository
import types


class DummyVar:
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value


def test_work_product_name_read_only():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.create_diagram("Governance Diagram")
    obj = SysMLObject(
        1,
        "Work Product",
        0.0,
        0.0,
        properties={"name": "Risk Assessment", "name_locked": "1"},
    )
    dlg = SysMLObjectDialog.__new__(SysMLObjectDialog)
    dlg.obj = obj
    dlg.master = object()
    dlg.name_var = DummyVar("Renamed")
    dlg.width_var = DummyVar(str(obj.width))
    dlg.height_var = DummyVar(str(obj.height))
    dlg.entries = {}
    dlg.listboxes = {}
    dlg._operations = []
    dlg._behaviors = []
    dlg.apply()
    assert obj.properties["name"] == "Risk Assessment"


def test_work_product_name_editable_when_unlocked():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.create_diagram("Governance Diagram")
    obj = SysMLObject(1, "Work Product", 0.0, 0.0, properties={"name": "Custom"})
    dlg = SysMLObjectDialog.__new__(SysMLObjectDialog)
    dlg.obj = obj
    dlg.master = object()
    dlg.name_var = DummyVar("Renamed")
    dlg.width_var = DummyVar(str(obj.width))
    dlg.height_var = DummyVar(str(obj.height))
    dlg.entries = {}
    dlg.listboxes = {}
    dlg._operations = []
    dlg._behaviors = []
    dlg.apply()
    assert obj.properties["name"] == "Renamed"


def test_process_area_name_read_only():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.create_diagram("Governance Diagram")
    obj = SysMLObject(
        1,
        "System Boundary",
        0.0,
        0.0,
        properties={"name": "Hazard & Threat Analysis", "name_locked": "1"},
    )
    dlg = SysMLObjectDialog.__new__(SysMLObjectDialog)
    dlg.obj = obj
    dlg.master = object()
    dlg.name_var = DummyVar("Renamed")
    dlg.width_var = DummyVar(str(obj.width))
    dlg.height_var = DummyVar(str(obj.height))
    dlg.entries = {}
    dlg.listboxes = {}
    dlg._operations = []
    dlg._behaviors = []
    dlg.apply()
    assert obj.properties["name"] == "Hazard & Threat Analysis"


def test_lifecycle_phase_name_read_only():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    repo.create_diagram("Governance Diagram")
    obj = SysMLObject(
        1,
        "Lifecycle Phase",
        0.0,
        0.0,
        properties={"name": "P1", "name_locked": "1"},
    )
    dlg = SysMLObjectDialog.__new__(SysMLObjectDialog)
    dlg.obj = obj
    dlg.master = object()
    dlg.name_var = DummyVar("Renamed")
    dlg.width_var = DummyVar(str(obj.width))
    dlg.height_var = DummyVar(str(obj.height))
    dlg.entries = {}
    dlg.listboxes = {}
    dlg._operations = []
    dlg._behaviors = []
    dlg.apply()
    assert obj.properties["name"] == "P1"


def _create_win():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.zoom = 1.0
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.app = types.SimpleNamespace(
        enable_work_product=lambda *a, **k: None,
        refresh_tool_enablement=lambda *a, **k: None,
        enable_process_area=lambda *a, **k: None,
        safety_mgmt_toolbox=None,
    )
    return win


def test_place_work_product_sets_name_locked():
    win = _create_win()
    win._place_work_product("FMEA", 0.0, 0.0)
    assert win.objects[-1].properties.get("name_locked") == "1"


def test_place_generic_work_product_unlocked():
    win = _create_win()
    win._place_work_product("Generic", 0.0, 0.0, lock_name=False)
    assert win.objects[-1].properties.get("name_locked") != "1"


def test_place_process_area_sets_name_locked():
    win = _create_win()
    win._place_process_area("Hazard & Threat Analysis", 0.0, 0.0)
    assert win.objects[-1].properties.get("name_locked") == "1"


def test_add_lifecycle_phase_sets_name_locked(monkeypatch):
    win = _create_win()

    class Mod:
        def __init__(self, name, modules=None):
            self.name = name
            self.modules = modules or []

    toolbox = types.SimpleNamespace(modules=[Mod("Phase1")])
    win.app.safety_mgmt_toolbox = toolbox

    class DummyDialog:
        def __init__(self, parent, title, options):
            self.selection = "Phase1"

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", DummyDialog)

    win.add_lifecycle_phase()
    assert win.objects[-1].properties.get("name_locked") == "1"
