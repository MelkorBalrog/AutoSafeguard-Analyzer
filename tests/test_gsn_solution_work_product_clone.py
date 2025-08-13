from gsn import GSNNode, GSNDiagram
from gui.gsn_config_window import GSNElementConfig, WORK_PRODUCTS


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


def test_solution_clones_existing_work_product():
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    original = GSNNode("Orig", "Solution")
    original.work_product = WORK_PRODUCTS[0]
    diag.add_node(original)
    node = GSNNode("New", "Solution")
    diag.add_node(node)

    cfg = GSNElementConfig.__new__(GSNElementConfig)
    cfg.node = node
    cfg.diagram = diag
    cfg.name_var = DummyVar(node.user_name)
    cfg.desc_text = DummyText(node.description)
    cfg.work_var = DummyVar(WORK_PRODUCTS[0])
    cfg.destroy = lambda: None

    cfg._on_ok()

    assert node.original is original
    assert not node.is_primary_instance
    assert node.user_name == original.user_name
    assert node.unique_id == original.unique_id

