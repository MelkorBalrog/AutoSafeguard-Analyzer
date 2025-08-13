from gsn import GSNNode, GSNDiagram
from gui.gsn_config_window import GSNElementConfig, _collect_work_products


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
    original.work_product = "WP1"
    diag.add_node(original)
    node = GSNNode("New", "Solution")
    diag.add_node(node)

    cfg = GSNElementConfig.__new__(GSNElementConfig)
    cfg.node = node
    cfg.diagram = diag
    cfg.name_var = DummyVar(node.user_name)
    cfg.desc_text = DummyText(node.description)
    cfg.work_var = DummyVar("WP1")
    cfg.link_var = DummyVar("")
    cfg.spi_var = DummyVar("")
    cfg.destroy = lambda: None

    cfg._on_ok()

    assert node.original is original
    assert not node.is_primary_instance
    assert node.user_name == original.user_name
    assert node.unique_id == original.unique_id


def test_solution_requires_matching_spi_for_clone():
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    original = GSNNode("Orig", "Solution")
    original.work_product = "WP1"
    original.spi_target = "Brake Time"
    diag.add_node(original)

    node = GSNNode("New", "Solution")
    diag.add_node(node)
    cfg = GSNElementConfig.__new__(GSNElementConfig)
    cfg.node = node
    cfg.diagram = diag
    cfg.name_var = DummyVar(node.user_name)
    cfg.desc_text = DummyText(node.description)
    cfg.work_var = DummyVar("WP1")
    cfg.link_var = DummyVar("")
    cfg.spi_var = DummyVar("Other SPI")
    cfg.destroy = lambda: None
    cfg._on_ok()

    assert node.original is node

    node2 = GSNNode("New2", "Solution")
    diag.add_node(node2)
    cfg2 = GSNElementConfig.__new__(GSNElementConfig)
    cfg2.node = node2
    cfg2.diagram = diag
    cfg2.name_var = DummyVar(node2.user_name)
    cfg2.desc_text = DummyText(node2.description)
    cfg2.work_var = DummyVar("WP1")
    cfg2.link_var = DummyVar("")
    cfg2.spi_var = DummyVar("Brake Time")
    cfg2.destroy = lambda: None
    cfg2._on_ok()

    assert node2.original is original


def test_format_text_shows_spi_target():
    root = GSNNode("Root", "Goal")
    sol = GSNNode("Sol", "Solution")
    sol.spi_target = "Brake Time"
    diag = GSNDiagram(root)
    diag.add_node(sol)
    text = diag._format_text(sol)
    assert "SPI: Brake Time" in text


def test_collect_work_products_returns_unique_sorted():
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    n1 = GSNNode("S1", "Solution")
    n1.work_product = "B"
    diag.add_node(n1)
    n2 = GSNNode("S2", "Solution")
    n2.work_product = "A"
    diag.add_node(n2)
    n3 = GSNNode("S3", "Solution")
    n3.work_product = "A"  # duplicate
    diag.add_node(n3)

    assert _collect_work_products(diag) == ["A", "B"]

