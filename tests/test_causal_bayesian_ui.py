import sys
from pathlib import Path
import types
from itertools import product

from analysis import CausalBayesianNetwork
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from gui.drawing_helper import FTADrawingHelper
from analysis import CausalBayesianNetwork
from unittest import mock


class DummyCanvas:
    """Canvas stub capturing gradient moves and item configures."""

    def __init__(self):
        self.next_id = 1
        self.items = {}
        self.moves = []
        self.last_configure = {}

    def create_line(self, x1, y1, x2, y2, **kw):
        i = self.next_id
        self.next_id += 1
        self.items[i] = {"type": "line", "coords": [x1, y1, x2, y2]}
        self.items[i].update(kw)
        return i

    def create_oval(self, x1, y1, x2, y2, **kw):
        i = self.next_id
        self.next_id += 1
        self.items[i] = {"type": "oval", "coords": [x1, y1, x2, y2]}
        self.items[i].update(kw)
        return i

    def create_text(self, x, y, **kw):
        i = self.next_id
        self.next_id += 1
        self.items[i] = {"type": "text", "coords": [x, y]}
        self.items[i].update(kw)
        return i

    def create_rectangle(self, x1, y1, x2, y2, **kw):
        i = self.next_id
        self.next_id += 1
        self.items[i] = {"type": "rectangle", "coords": [x1, y1, x2, y2]}
        self.items[i].update(kw)
        return i

    def delete(self, item):
        if item == "all":
            self.items.clear()
        else:
            self.items.pop(item, None)

    def coords(self, item, x1, y1, x2=None, y2=None):
        if item in self.items:
            if x2 is None and y2 is None:
                self.items[item]["coords"] = [x1, y1]
            else:
                self.items[item]["coords"] = [x1, y1, x2, y2]

    def move(self, tag, dx, dy):
        self.moves.append((tag, dx, dy))

    def itemconfigure(self, item, **kw):
        self.items.setdefault(item, {}).update(kw)
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
    win.after = lambda *a, **k: None
    win.after_cancel = lambda *a, **k: None
    win.selected_node = None
    win.selection_rect = None
    win.temp_edge_line = None
    win.temp_edge_anim = None
    win.temp_edge_offset = 0
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
                return [((), prob, 1.0, prob)]
            cpds = self.cpds.get(name, {})
            rows = []
            for combo in product([False, True], repeat=len(parents)):
                prob = float(cpds.get(combo, 0.0))
                rows.append((combo, prob, 0.0, 0.0))
            return rows

    doc = types.SimpleNamespace(network=Net(), positions={}, types={})
    app.active_cbn = doc
    win.app = app
    win._find_node = lambda x, y: next(
        (n for n, (nx, ny) in doc.positions.items() if abs(nx - x) <= win.NODE_RADIUS and abs(ny - y) <= win.NODE_RADIUS),
        None,
    )
    return win, doc


def _setup_window_real():
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
    win.after = lambda *a, **k: None
    win.after_cancel = lambda *a, **k: None
    win.selected_node = None
    win.selection_rect = None
    win.temp_edge_line = None
    win.temp_edge_anim = None
    win.temp_edge_offset = 0
    app = DummyApp()
    doc = types.SimpleNamespace(network=CausalBayesianNetwork(), positions={})
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
    # two parent columns plus a single probability column
    assert all(len(row) == 3 for row in tree.rows)


def test_node_colors_by_type():
    win, _ = _setup_window()
    colors = []

    def capture(canvas, x, y, r, color, tag=None):
        colors.append(color)

    win.drawing_helper._fill_gradient_circle = capture
    win._draw_node("T", 0, 0, "trigger")
    win._draw_node("I", 0, 0, "insufficiency")
    win._draw_node("M", 0, 0, "malfunction")
    assert colors[0] == "lightblue"
    assert colors[1] == "lightyellow"
    assert colors[2] == "lightgreen"

def test_click_adds_existing_malfunction_nodes():
    win, doc = _setup_window()
    win.current_tool = "Existing Malfunction"
    with mock.patch.object(win, "_select_malfunctions", return_value=["M1", "M2"]):
        win.on_click(types.SimpleNamespace(x=0, y=0))
    assert "M1" in doc.network.nodes and "M2" in doc.network.nodes
    assert doc.types["M1"] == doc.types["M2"] == "malfunction"
    # Second node should be offset horizontally
    expected_x = (2 * win.NODE_RADIUS + 10)
    assert doc.positions["M2"][0] == expected_x


def test_update_all_tables_refreshes_dependencies():
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
    net = CausalBayesianNetwork()
    net.add_node("Rain", cpd=0.3)
    net.add_node("WetGround", parents=["Rain"], cpd={(True,): 0.9, (False,): 0.1})
    doc = types.SimpleNamespace(network=net, positions={"Rain": (0, 0), "WetGround": (0, 0)})
    app.active_cbn = doc
    win.app = app

def test_drag_relationship_creates_edge():
    win, doc = _setup_window()
    doc.network.nodes.update({"A", "B"})
    doc.positions["A"] = (0, 0)
    doc.positions["B"] = (100, 0)
    win._draw_node("A", 0, 0)
    win._draw_node("B", 100, 0)
    win.current_tool = "Relationship"
    win.on_click(types.SimpleNamespace(x=0, y=0))
    win.on_drag(types.SimpleNamespace(x=100, y=0))
    win.on_release(types.SimpleNamespace(x=100, y=0))
    assert len(win.edges) == 1
    assert "A" in doc.network.parents.get("B", [])
    assert win.current_tool == "Select"


def test_add_node_returns_to_select():
    from gui import causal_bayesian_network_window as cbn_mod

    win, doc = _setup_window()
    win.current_tool = "Triggering Condition"
    orig = cbn_mod.simpledialog.askstring
    cbn_mod.simpledialog.askstring = lambda *a, **k: "N1"
    try:
        win.on_click(types.SimpleNamespace(x=10, y=20))
    finally:
        cbn_mod.simpledialog.askstring = orig
    assert "N1" in doc.network.nodes
    assert win.current_tool == "Select"


def test_joint_probabilities_refresh_on_parent_change():
    win, doc = _setup_window_real()
    cbn = doc.network
    cbn.add_node("A", cpd=0.2)
    cbn.add_node("B", parents=["A"], cpd={(True,): 0.5, (False,): 0.1})
    tree_a = DummyTree(); frame_a = DummyFrame(tree_a); win.tables["A"] = (1, frame_a, tree_a)
    tree_b = DummyTree(); frame_b = DummyFrame(tree_b); win.tables["B"] = (2, frame_b, tree_b)
    doc.positions["A"] = (0, 0)
    doc.positions["B"] = (0, 0)

    win._update_all_tables()
    assert tree_b.rows[0][-1] == f"{0.8 * 0.1:.3f}"
    assert tree_b.rows[1][-1] == f"{0.2 * 0.5:.3f}"

    cbn.cpds["A"] = 0.7
    win._update_all_tables()
    assert tree_b.rows[0][-1] == f"{0.3 * 0.1:.3f}"
    assert tree_b.rows[1][-1] == f"{0.7 * 0.5:.3f}"
