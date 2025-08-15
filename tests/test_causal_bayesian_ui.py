import sys
from pathlib import Path
import types
from itertools import product

sys.path.append(str(Path(__file__).resolve().parents[1]))

import gui.causal_bayesian_network_window as cbnw
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from gui.drawing_helper import FTADrawingHelper


class DummyCanvas:
    """Canvas stub capturing gradient moves and item configures."""

    def __init__(self):
        self.next_id = 1
        self.items = {}
        self.moves = []
        self.last_configure = {}

    def create_line(self, x1, y1, x2, y2, fill=None, tags=None):
        i = self.next_id
        self.next_id += 1
        self.items[i] = {"type": "line", "tags": set([tags]) if tags else set()}
        return i

    def create_oval(self, x1, y1, x2, y2, **kw):
        i = self.next_id
        self.next_id += 1
        self.items[i] = {"type": "oval"}
        return i

    def create_text(self, x, y, **kw):
        i = self.next_id
        self.next_id += 1
        self.items[i] = {"type": "text"}
        return i

    def coords(self, *args, **kwargs):
        pass

    def move(self, tag, dx, dy):
        self.moves.append((tag, dx, dy))

    def itemconfigure(self, item, **kw):
        self.last_configure.update(kw)

    def update_idletasks(self):
        pass

    def create_window(self, *args, **kwargs):
        i = self.next_id
        self.next_id += 1
        self.items[i] = {"type": "window"}
        return i

    def find_overlapping(self, *args, **kwargs):
        return list(self.items.keys())


class DummyTree:
    def __init__(self):
        self.height = 0
        self.rows = []

    def delete(self, *args):
        self.rows = []

    def get_children(self):
        return list(range(len(self.rows)))

    def configure(self, **kw):
        if "height" in kw:
            self.height = kw["height"]

    def insert(self, parent, index, values):
        self.rows.append(values)

    # Methods not used in tests but required by interface
    def heading(self, *a, **k):
        pass

    def column(self, *a, **k):
        pass

    def pack(self, *a, **k):
        pass

    def bind(self, *a, **k):
        pass


class DummyFrame:
    def __init__(self, tree):
        self.tree = tree
        self.update_idletasks_called = False

    def update_idletasks(self):
        self.update_idletasks_called = True

    def winfo_reqwidth(self):
        return 100

    def winfo_reqheight(self):
        return 30 + self.tree.height * 20

    def pack(self, *a, **k):
        pass


class DummyApp:
    pass


def _setup_window():
    win = object.__new__(CausalBayesianNetworkWindow)
    win.NODE_RADIUS = CausalBayesianNetworkWindow.NODE_RADIUS
    win.canvas = DummyCanvas()
    win.drawing_helper = FTADrawingHelper()
    win.nodes = {}
    win.tables = {}
    win.id_to_node = {}
    win.edges = []
    win.current_tool = "Select"
    win._place_table = lambda *a, **k: None
    win._position_table = lambda *a, **k: None
    app = DummyApp()
    class Net:
        def __init__(self):
            self.nodes = set()
            self.parents = {}
            self.cpds = {}

        def add_node(self, name, cpd=0.0):
            self.nodes.add(name)
            self.cpds[name] = cpd

        def cpd_rows(self, name):
            parents = self.parents.get(name, [])
            if not parents:
                prob = float(self.cpds.get(name, 0.0))
                return [((), prob)]
            cpds = self.cpds.get(name, {})
            rows = []
            for combo in product([False, True], repeat=len(parents)):
                rows.append((combo, float(cpds.get(combo, 0.0))))
            return rows

    doc = types.SimpleNamespace(network=Net(), positions={}, types={})
    app.active_cbn = doc
    win.app = app
    return win, doc


def test_fill_moves_with_node():
    win, doc = _setup_window()
    doc.network.nodes.add("A")
    doc.positions["A"] = (0, 0)
    win._draw_node("A", 0, 0)
    win.drag_node = "A"
    win.drag_offset = (0, 0)
    event = types.SimpleNamespace(x=10, y=15)
    win.on_drag(event)
    assert ("fill_A", 10, 15) in win.canvas.moves


def test_table_resizes_for_new_rows():
    win, doc = _setup_window()
    tree = DummyTree()
    frame = DummyFrame(tree)
    win.tables["A"] = (1, frame, tree)
    doc.network.nodes.add("A")
    doc.network.parents["A"] = ["P1"]
    doc.positions["A"] = (0, 0)

    win._update_table("A")
    first_height = win.canvas.last_configure.get("height")
    assert frame.update_idletasks_called

    # updating CPDs should keep the same table size because all rows are
    # present from the start
    frame.update_idletasks_called = False
    doc.network.cpds["A"] = {(True,): 0.1, (False,): 0.2}
    win._update_table("A")
    second_height = win.canvas.last_configure.get("height")
    assert frame.update_idletasks_called
    assert second_height == first_height


def test_table_auto_fills_missing_rows():
    win, doc = _setup_window()
    tree = DummyTree()
    frame = DummyFrame(tree)
    win.tables["A"] = (1, frame, tree)
    doc.network.nodes.add("A")
    doc.network.parents["A"] = ["P1", "P2"]
    doc.positions["A"] = (0, 0)
    # only one CPD entry; others should default to 0.0
    doc.network.cpds["A"] = {(True, False): 0.2}
    win._update_table("A")
    assert tree.height == 4
    assert len(tree.rows) == 4


def test_node_colors_by_type():
    win, _ = _setup_window()
    colors = []

    def capture(canvas, x, y, r, color, tag=None):
        colors.append(color)

    win.drawing_helper._fill_gradient_circle = capture
    win._draw_node("T", 0, 0, "trigger")
    win._draw_node("I", 0, 0, "insufficiency")
    assert colors[0] == "lightgreen"
    assert colors[1] == "lightyellow"


def test_new_triggering_condition_registers():
    win, doc = _setup_window()
    called = {}
    win.app.update_triggering_condition_list = lambda: called.setdefault("tc", True)
    win.current_tool = "Triggering Condition"
    orig = cbnw.simpledialog.askstring
    cbnw.simpledialog.askstring = lambda *a, **k: "TC1"
    event = types.SimpleNamespace(x=5, y=5)
    win.on_click(event)
    cbnw.simpledialog.askstring = orig
    assert "TC1" in doc.network.nodes
    assert called.get("tc")


def test_new_functional_insufficiency_registers():
    win, doc = _setup_window()
    called = {}
    win.app.update_functional_insufficiency_list = lambda: called.setdefault("fi", True)
    win.current_tool = "Functional Insufficiency"
    orig = cbnw.simpledialog.askstring
    cbnw.simpledialog.askstring = lambda *a, **k: "FI1"
    event = types.SimpleNamespace(x=5, y=5)
    win.on_click(event)
    cbnw.simpledialog.askstring = orig
    assert "FI1" in doc.network.nodes
    assert called.get("fi")


def test_existing_triggering_condition_registers():
    win, doc = _setup_window()
    win.app.triggering_conditions = ["TC1"]
    called = {}
    win.app.update_triggering_condition_list = lambda: called.setdefault("tc", True)
    win._select_triggering_conditions = lambda: ["TC1"]
    win.current_tool = "Existing Triggering Condition"
    event = types.SimpleNamespace(x=5, y=5)
    win.on_click(event)
    assert "TC1" in doc.network.nodes
    assert doc.types["TC1"] == "trigger"
    assert called.get("tc")


def test_existing_functional_insufficiency_registers():
    win, doc = _setup_window()
    win.app.functional_insufficiencies = ["FI1"]
    called = {}
    win.app.update_functional_insufficiency_list = lambda: called.setdefault("fi", True)
    win._select_functional_insufficiencies = lambda: ["FI1"]
    win.current_tool = "Existing Functional Insufficiency"
    event = types.SimpleNamespace(x=5, y=5)
    win.on_click(event)
    assert "FI1" in doc.network.nodes
    assert doc.types["FI1"] == "insufficiency"
    assert called.get("fi")
