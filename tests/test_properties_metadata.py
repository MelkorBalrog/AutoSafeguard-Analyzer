import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import FaultTreeApp
from sysml.sysml_repository import SysMLRepository
from gui.architecture import ArchitectureManagerDialog, SysMLObject
from types import SimpleNamespace


def test_analysis_tree_selection_shows_metadata():
    # reset repository
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Use Case Diagram", name="Diag")

    # setup minimal app instance without running __init__
    app = FaultTreeApp.__new__(FaultTreeApp)

    class DummyTree:
        def __init__(self):
            self._focus = "i1"
            self.items = {
                "i1": {"text": diag.name, "tags": ("arch", diag.diag_id)}
            }

        def focus(self):
            return self._focus

        def item(self, item, attr):
            return self.items[item][attr]

    class DummyPropView:
        def __init__(self):
            self.rows = []

        def delete(self, *items):
            self.rows = []

        def get_children(self):
            return list(range(len(self.rows)))

        def insert(self, _parent, _index, values):
            self.rows.append(values)

    app.analysis_tree = DummyTree()
    app.prop_view = DummyPropView()
    # bind methods
    app.show_properties = FaultTreeApp.show_properties.__get__(app)
    app.on_analysis_tree_select = FaultTreeApp.on_analysis_tree_select.__get__(app)

    app.on_analysis_tree_select(None)
    values = {k: v for k, v in app.prop_view.rows}
    assert values["Author"] == diag.author
    assert values["Created"] == diag.created


def test_architecture_tree_selection_shows_metadata():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Use Case Diagram", name="Diag")

    class DummyPropView:
        def __init__(self):
            self.rows = []

        def delete(self, *items):
            self.rows = []

        def get_children(self):
            return list(range(len(self.rows)))

        def insert(self, _parent, _index, values):
            self.rows.append(values)

    app = SimpleNamespace()
    app.prop_view = DummyPropView()
    app.show_properties = FaultTreeApp.show_properties.__get__(app)

    class DummyTree:
        def __init__(self):
            self._focus = f"diag_{diag.diag_id}"
            self.items = {
                self._focus: {"text": diag.name, "values": (diag.diag_type,)}
            }

        def focus(self):
            return self._focus

        def item(self, item, attr):
            return self.items[item][attr]

    dlg = ArchitectureManagerDialog.__new__(ArchitectureManagerDialog)
    dlg.tree = DummyTree()
    dlg.app = app
    dlg.repo = repo

    dlg.on_tree_select(None)
    values = {k: v for k, v in app.prop_view.rows}
    assert values["Author"] == diag.author
    assert values["Created"] == diag.created


def test_diagram_selection_clears_tree_and_shows_object_properties():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Use Case Diagram", name="Diag")

    obj = SysMLObject(1, "Actor", 0, 0, properties={"name": "Act"})

    app = FaultTreeApp.__new__(FaultTreeApp)

    class DummyTree:
        def __init__(self):
            self._focus = "i1"
            self._sel = ("i1",)
            self.items = {"i1": {"text": diag.name, "tags": ("arch", diag.diag_id)}}

        def focus(self, item=None):
            if item is None:
                return self._focus
            self._focus = item

        def item(self, item, attr):
            return self.items[item][attr]

        def selection(self):
            return self._sel

        def selection_set(self, sel):
            self._sel = tuple(sel)

    class DummyPropView:
        def __init__(self):
            self.rows = []

        def delete(self, *items):
            self.rows = []

        def get_children(self):
            return list(range(len(self.rows)))

        def insert(self, _parent, _index, values):
            self.rows.append(values)

    app.analysis_tree = DummyTree()
    app.prop_view = DummyPropView()
    app.show_properties = FaultTreeApp.show_properties.__get__(app)
    app.on_analysis_tree_select = FaultTreeApp.on_analysis_tree_select.__get__(app)

    app.on_analysis_tree_select(None)

    app.show_properties(obj=obj)
    values = {k: v for k, v in app.prop_view.rows}
    assert values["Name"] == "Act"
    assert values["Type"] == "Actor"
    assert app.analysis_tree.selection() == ()
