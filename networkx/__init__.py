class DiGraph:
    """Very small subset of :class:`networkx.DiGraph`.

    The real NetworkX library exposes a rich API for storing directed graphs.
    For the needs of this project we only implement the handful of methods
    exercised by :func:`auto_generate_fta_diagram` in ``AutoML.py``.  The goal
    is merely to provide enough behaviour so the surrounding code can execute
    without pulling in the heavy NetworkX dependency.

    Nodes are stored in dictionaries mapping to sets of successors and
    predecessors which conveniently preserves insertion order in Python 3.7+
    while giving us efficient membership checks.
    """

    def __init__(self, *args, **kwargs):
        # Maps a node -> set of nodes with an incoming edge from ``node``
        self._succ = {}
        # Maps a node -> set of nodes with an outgoing edge to ``node``
        self._pred = {}

    # ------------------------------------------------------------------
    # Basic mutation helpers
    def add_node(self, node, **kwargs):
        """Add *node* to the graph if it isn't present."""
        self._succ.setdefault(node, set())
        self._pred.setdefault(node, set())

    def add_edge(self, u, v, **kwargs):
        """Insert a directed edge ``u -> v``."""
        self.add_node(u)
        self.add_node(v)
        self._succ[u].add(v)
        self._pred[v].add(u)

    # ------------------------------------------------------------------
    # Query helpers used by AutoML
    def has_node(self, node):
        return node in self._succ

    def successors(self, node):
        return list(self._succ.get(node, []))

    def predecessors(self, node):
        return list(self._pred.get(node, []))

    def nodes(self):
        return list(self._succ.keys())

    def edges(self):
        return [(u, v) for u, vs in self._succ.items() for v in vs]


def draw_networkx_edges(*args, **kwargs):
    pass


def draw_networkx_nodes(*args, **kwargs):
    pass


def draw(*args, **kwargs):
    pass


def draw_networkx_edge_labels(*args, **kwargs):
    pass
