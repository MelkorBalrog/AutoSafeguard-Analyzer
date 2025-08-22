
from gui.gsn_diagram_window import GSNDiagramWindow
from gui.gsn_config_window import GSNElementConfig
from gsn import GSNDiagram, GSNNode

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


def _configure(node, diagram, name="", desc="", notes=""):
    cfg = GSNElementConfig.__new__(GSNElementConfig)
    cfg.node = node
    cfg.diagram = diagram
    cfg.name_var = DummyVar(name or node.user_name)
    cfg.desc_text = DummyText(desc or node.description)
    cfg.notes_text = DummyText(notes or node.manager_notes)
    cfg.destroy = lambda: None
    cfg._on_ok()


def test_clone_sync_on_tab_focus():
    original = GSNNode("Orig", "Goal")
    diag1 = GSNDiagram(original)
    clone = original.clone()
    diag2 = GSNDiagram(clone)
    diag2.add_node(clone)

    _configure(original, diag1, name="NewName", desc="NewDesc", notes="NewNote")
    assert clone.user_name != "NewName"

    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    win.diagram = diag2
    win.refresh = lambda: None
    GSNDiagramWindow.refresh_from_repository(win)

    assert clone.user_name == "NewName"
    assert clone.description == "NewDesc"
    assert clone.manager_notes == "NewNote"
