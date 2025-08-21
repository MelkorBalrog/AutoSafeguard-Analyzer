from AutoML import AutoMLApp
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


def test_app_undo_redo_without_app_state():
    repo = SysMLRepository.reset_instance()
    app = AutoMLApp.__new__(AutoMLApp)
    app._undo_stack = []
    app._redo_stack = []
    app.export_model_data = lambda include_versions=False: {}
    app.apply_model_data = lambda state: None
    app.refresh_all = lambda: None
    app.diagram_tabs = {}

    diag = SysMLDiagram(diag_id="d", diag_type="Use Case Diagram")
    repo.diagrams[diag.diag_id] = diag

    repo.push_undo_state()
    repo.diagrams[diag.diag_id].name = "Renamed"
    repo.touch_diagram(diag.diag_id)

    AutoMLApp.undo(app)
    assert repo.diagrams[diag.diag_id].name == ""

    AutoMLApp.redo(app)
    assert repo.diagrams[diag.diag_id].name == "Renamed"
