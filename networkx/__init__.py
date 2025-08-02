class DiGraph:
    def __init__(self, *args, **kwargs):
        self.nodes = []
        self.edges = []

    def add_node(self, node, **kwargs):
        self.nodes.append(node)

    def add_edge(self, u, v, **kwargs):
        self.edges.append((u, v))


def draw_networkx_edges(*args, **kwargs):
    pass


def draw_networkx_nodes(*args, **kwargs):
    pass


def draw(*args, **kwargs):
    pass


def draw_networkx_edge_labels(*args, **kwargs):
    pass
