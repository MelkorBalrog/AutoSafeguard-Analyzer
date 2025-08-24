import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import AutoMLApp
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


def test_undo_after_project_load_keeps_project():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    blk = repo.create_element("Block", name="A")
    data = {"sysml_repository": repo.to_dict()}

    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()

    app = AutoMLApp.__new__(AutoMLApp)
    app.export_model_data = lambda include_versions=False: data
    app.apply_model_data = lambda d: repo.from_dict(d["sysml_repository"])
    app.refresh_all = lambda: None
    app.diagram_tabs = {}
    app._undo_stack = [{}]
    app._redo_stack = [{}]
    app.undo = AutoMLApp.undo.__get__(app)
    app.clear_undo_history = AutoMLApp.clear_undo_history.__get__(app)

    app.apply_model_data(data)
    app.clear_undo_history()
    app.undo()
    assert blk.elem_id in repo.elements
