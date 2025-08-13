from gsn import GSNNode, GSNDiagram
from gui.gsn_config_window import GSNElementConfig


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


def _configure(node, diagram, name="", desc="", work="", link="", spi=""):
    cfg = GSNElementConfig.__new__(GSNElementConfig)
    cfg.node = node
    cfg.diagram = diagram
    cfg.name_var = DummyVar(name or node.user_name)
    cfg.desc_text = DummyText(desc or node.description)
    cfg.work_var = DummyVar(work or getattr(node, "work_product", ""))
    cfg.link_var = DummyVar(link or getattr(node, "evidence_link", ""))
    cfg.spi_var = DummyVar(spi or getattr(node, "spi_target", ""))
    cfg.destroy = lambda: None
    cfg._on_ok()


def test_updates_propagate_between_original_and_clones():
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    original = GSNNode("Orig", "Solution")
    original.work_product = "WP1"
    diag.add_node(original)

    clone = GSNNode("Clone", "Solution")
    diag.add_node(clone)

    _configure(clone, diag, work="WP1", link="L1")
    assert clone.original is original

    # modify the original and ensure the clone updates
    _configure(original, diag, name="Updated", desc="Desc", work="WP2", link="L2")
    assert clone.user_name == "Updated"
    assert clone.description == "Desc"
    assert clone.work_product == "WP2"
    assert clone.evidence_link == "L2"

    # modify the clone and ensure the original also updates
    _configure(clone, diag, name="Changed", desc="Changed Desc", link="L3")
    assert original.user_name == "Changed"
    assert original.description == "Changed Desc"
    assert original.evidence_link == "L3"
    assert clone.user_name == "Changed"
    assert clone.evidence_link == "L3"
