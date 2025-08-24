from AutoML import PageDiagram

class DummyApp:
    def __init__(self):
        self.modes = []
        self.project_properties = {}
        self.occurrence_counts = {}

    def get_node_fill_color(self, node, mode=None):
        self.modes.append(mode)
        return "#000000"


class DummyCanvas:
    diagram_mode = "CTA"

    def bind(self, *args, **kwargs):
        pass


class DummyNode:
    is_primary_instance = True
    original = None
    display_label = ""
    input_subtype = None
    description = ""
    rationale = ""
    equation = ""
    detailed_equation = ""
    name = "n"
    x = 0
    y = 0
    unique_id = 1
    node_type = "Basic Event"
    children = []
    parents = []
    is_page = False
    gate_type = "AND"


class StubDrawingHelper:
    def draw_circle_event_shape(self, *args, **kwargs):
        pass


class DummyFont:
    def config(self, *args, **kwargs):
        pass


def test_page_diagram_uses_own_mode(monkeypatch):
    import AutoML as auto_module

    monkeypatch.setattr(auto_module.tkFont, "Font", lambda *a, **k: DummyFont())
    monkeypatch.setattr(auto_module, "fta_drawing_helper", StubDrawingHelper())

    app = DummyApp()
    canvas = DummyCanvas()
    pd = PageDiagram(app, DummyNode(), canvas)
    pd.draw_node(DummyNode())

    assert app.modes == ["CTA"]
