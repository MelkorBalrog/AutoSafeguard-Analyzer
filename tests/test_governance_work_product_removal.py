from gui import messagebox
from gui.architecture import GovernanceDiagramWindow, SysMLObject
from analysis import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository


def test_delete_work_product_updates_toolbox(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram", name="Gov1")
    diag.tags.append("safety-management")

    toolbox = SafetyManagementToolbox()
    toolbox.add_work_product("Gov1", "FI2TC", "")

    disabled: list[str] = []

    class DummyApp:
        def can_remove_work_product(self, name):
            return True

        def disable_work_product(self, name):
            disabled.append(name)

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

    wp = SysMLObject(1, "Work Product", 0, 0, properties={"name": "FI2TC"})
    win.objects.append(wp)
    win.selected_objs = [wp]
    win.selected_obj = wp
    win.app = DummyApp()

    monkeypatch.setattr(messagebox, "askyesnocancel", lambda *args, **kwargs: False)
    monkeypatch.setattr(messagebox, "showerror", lambda *args, **kwargs: None)

    win.delete_selected()

    assert disabled == ["FI2TC"]
    assert toolbox.work_products == []
