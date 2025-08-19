import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui import messagebox
from gui.architecture import GovernanceDiagramWindow
from analysis import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository


def test_delete_process_area_removes_children(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    diag.tags.append("safety-management")

    toolbox = SafetyManagementToolbox()
    disabled: list[str] = []

    class DummyApp:
        def can_remove_work_product(self, name):
            return True

        def disable_work_product(self, name):
            disabled.append(name)

        def enable_process_area(self, name):
            pass

        def enable_work_product(self, name):
            pass

        def refresh_tool_enablement(self):
            pass

        safety_mgmt_toolbox = toolbox

    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = []
    win.connections = []
    win.selected_conn = None
    win.zoom = 1.0
    win.remove_object = GovernanceDiagramWindow.remove_object.__get__(win, GovernanceDiagramWindow)
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    win.update_property_view = lambda: None
    win.remove_part_model = GovernanceDiagramWindow.remove_part_model.__get__(win, GovernanceDiagramWindow)
    win.remove_element_model = GovernanceDiagramWindow.remove_element_model.__get__(win, GovernanceDiagramWindow)
    win.sort_objects = lambda: None
    win.app = DummyApp()

    area = win._place_process_area("Risk Assessment", 0.0, 0.0)
    win._place_work_product("Risk Assessment", 10.0, 10.0, area=area)

    win.selected_objs = [area]
    win.selected_obj = area

    monkeypatch.setattr(messagebox, "askyesno", lambda *args, **kwargs: True)
    monkeypatch.setattr(messagebox, "showerror", lambda *args, **kwargs: None)

    win.delete_selected()

    assert disabled == ["Risk Assessment"]
    assert toolbox.work_products == []
    assert not any(o.obj_type == "Work Product" for o in win.objects)
    assert not any(o.obj_type == "System Boundary" for o in win.objects)
