import types

from gsn import GSNNode, GSNDiagram
from gui.gsn_config_window import GSNElementConfig
from gui.gsn_diagram_window import GSNDiagramWindow


class DummyVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value


class DummyText:
    def __init__(self, text=""):
        self.text = text

    def get(self, *_args, **_kwargs):
        return self.text


def test_solution_config_sets_evidence_link():
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    node = GSNNode("Sol", "Solution")
    diag.add_node(node)

    cfg = GSNElementConfig.__new__(GSNElementConfig)
    cfg.node = node
    cfg.diagram = diag
    cfg.name_var = DummyVar(node.user_name)
    cfg.desc_text = DummyText(node.description)
    cfg.work_var = DummyVar("WP1")
    cfg.link_var = DummyVar("http://example.com")
    cfg.spi_var = DummyVar("")
    cfg.destroy = lambda: None

    cfg._on_ok()

    assert node.evidence_link == "http://example.com"


def test_solution_config_sets_manager_notes():
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    node = GSNNode("Sol", "Solution")
    diag.add_node(node)

    cfg = GSNElementConfig.__new__(GSNElementConfig)
    cfg.node = node
    cfg.diagram = diag
    cfg.name_var = DummyVar(node.user_name)
    cfg.desc_text = DummyText(node.description)
    cfg.notes_text = DummyText("Review this later")
    cfg.work_var = DummyVar("")
    cfg.link_var = DummyVar("")
    cfg.spi_var = DummyVar("")
    cfg.destroy = lambda: None

    cfg._on_ok()

    assert node.manager_notes == "Review this later"


def test_double_click_opens_evidence_link(monkeypatch):
    opened = {}

    def fake_open(url):
        opened["url"] = url
        return True

    monkeypatch.setattr("webbrowser.open", fake_open)

    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    node = GSNNode("Sol", "Solution")
    node.evidence_link = "http://example.com"
    diag.add_node(node)

    wnd = GSNDiagramWindow.__new__(GSNDiagramWindow)
    wnd.diagram = diag
    wnd.refresh = lambda: None
    wnd._node_at = lambda x, y: node
    wnd.canvas = type(
        "CanvasStub",
        (),
        {
            "canvasx": staticmethod(lambda x: x),
            "canvasy": staticmethod(lambda y: y),
        },
    )()

    event = types.SimpleNamespace(x=0, y=0)
    GSNDiagramWindow._on_double_click(wnd, event)

    assert opened["url"] == "http://example.com"

