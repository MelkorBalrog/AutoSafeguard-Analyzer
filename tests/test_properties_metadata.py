from AutoML import FaultTreeApp
from sysml.sysml_repository import SysMLRepository


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
