from gsn import GSNNode, GSNDiagram
from gsn import GSNNode, GSNDiagram
from gui.gsn_config_window import GSNElementConfig, _collect_work_products
import types


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


def test_collect_work_products_includes_toolbox():
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)

    class DummyWP:
        def __init__(self, diagram, analysis):
            self.diagram = diagram
            self.analysis = analysis

    class DummyToolbox:
        def get_work_products(self):
            return [DummyWP("D1", "A1"), DummyWP("D2", "A2")]

    app = types.SimpleNamespace(safety_mgmt_toolbox=DummyToolbox())
    assert _collect_work_products(diag, app) == ["D1 - A1", "D2 - A2"]


def test_config_dialog_populates_comboboxes(monkeypatch):
    """Work product and SPI combos should list existing entries."""

    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    existing = GSNNode("Orig", "Solution")
    existing.work_product = "WP1"
    existing.spi_target = "SPI1"
    diag.add_node(existing)

    node = GSNNode("New", "Solution")
    diag.add_node(node)

    # ------------------------------------------------------------------
    # Stub tkinter widgets so the dialog can be created headlessly
    # ------------------------------------------------------------------
    class DummyWidget:
        def __init__(self, *a, **k):
            self.configured = {}

        def grid(self, *a, **k):
            pass

        def pack(self, *a, **k):
            pass

        def insert(self, *a, **k):
            pass

        def configure(self, **k):
            self.configured.update(k)

    class DummyText(DummyWidget):
        def get(self, *a, **k):
            return ""

    class DummyCombobox(DummyWidget):
        def __init__(self, *a, textvariable=None, values=None, state=None, **k):
            super().__init__(*a, **k)
            self.textvariable = textvariable
            self.state = state
            self.init_values = values

    combo_holder = []

    def combo_stub(*a, **k):
        cb = DummyCombobox(*a, **k)
        combo_holder.append(cb)
        return cb

    class DummyVar:
        def __init__(self, value=""):
            self._value = value

        def get(self):
            return self._value

        def set(self, v):
            self._value = v

    # Patch tkinter components used by the dialog
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.__init__", lambda self, master=None: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.title", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.geometry", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.columnconfigure", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.rowconfigure", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.transient", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.grab_set", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.wait_window", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Label", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.gsn_config_window.tk.Entry", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.gsn_config_window.tk.Text", lambda *a, **k: DummyText())
    monkeypatch.setattr("gui.gsn_config_window.ttk.Button", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.gsn_config_window.ttk.Frame", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.gsn_config_window.ttk.Combobox", combo_stub)
    monkeypatch.setattr("gui.gsn_config_window.tk.StringVar", lambda value="": DummyVar(value))

    cfg = GSNElementConfig(None, node, diag)

    wp_cb, spi_cb = combo_holder
    assert wp_cb.init_values is None
    assert spi_cb.init_values is None
    assert wp_cb.configured["values"] == ["WP1"]
    assert spi_cb.configured["values"] == ["SPI1"]
    # first existing entries should be preselected when the node has none
    assert cfg.work_var.get() == "WP1"
    assert cfg.spi_var.get() == "SPI1"


def test_config_dialog_lists_toolbox_work_products(monkeypatch):
    root = GSNNode("Root", "Goal")
    diag = GSNDiagram(root)
    node = GSNNode("New", "Solution")
    diag.add_node(node)

    class DummyToolbox:
        def get_work_products(self):
            return [types.SimpleNamespace(diagram="Diag", analysis="An")]

    app = types.SimpleNamespace(safety_mgmt_toolbox=DummyToolbox())

    class DummyWidget:
        def __init__(self, *a, **k):
            self.configured = {}

        def grid(self, *a, **k):
            pass

        def pack(self, *a, **k):
            pass

        def insert(self, *a, **k):
            pass

        def configure(self, **k):
            self.configured.update(k)

    class DummyText(DummyWidget):
        def get(self, *a, **k):
            return ""

    class DummyCombobox(DummyWidget):
        def __init__(self, *a, textvariable=None, values=None, state=None, **k):
            super().__init__(*a, **k)
            self.textvariable = textvariable
            self.state = state
            self.init_values = values

    combo_holder = []

    def combo_stub(*a, **k):
        cb = DummyCombobox(*a, **k)
        combo_holder.append(cb)
        return cb

    class DummyVar:
        def __init__(self, value=""):
            self._value = value

        def get(self):
            return self._value

        def set(self, v):
            self._value = v

    master = types.SimpleNamespace(app=app)

    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.__init__", lambda self, master=None: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.title", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.geometry", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.columnconfigure", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.rowconfigure", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.transient", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.grab_set", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Toplevel.wait_window", lambda self, *a, **k: None)
    monkeypatch.setattr("gui.gsn_config_window.tk.Label", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.gsn_config_window.tk.Entry", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.gsn_config_window.tk.Text", lambda *a, **k: DummyText())
    monkeypatch.setattr("gui.gsn_config_window.ttk.Button", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.gsn_config_window.ttk.Frame", lambda *a, **k: DummyWidget())
    monkeypatch.setattr("gui.gsn_config_window.ttk.Combobox", combo_stub)
    monkeypatch.setattr("gui.gsn_config_window.tk.StringVar", lambda value="": DummyVar(value))

    cfg = GSNElementConfig(master, node, diag)
    wp_cb, spi_cb = combo_holder
    assert wp_cb.configured["values"] == ["Diag - An"]
    assert cfg.work_var.get() == "Diag - An"

