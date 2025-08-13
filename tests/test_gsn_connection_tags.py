from gsn import GSNNode, GSNDiagram


class StubCanvas:
    def __init__(self):
        self.lines = []
        self.polys = []

    def create_line(self, *args, **kwargs):
        self.lines.append(kwargs.get("tags"))

    def create_polygon(self, *args, **kwargs):
        self.polys.append(kwargs.get("tags"))

    def create_text(self, *args, **kwargs):
        pass

    def create_rectangle(self, *args, **kwargs):
        pass

    def bbox(self, tag):
        return None

    def tag_lower(self, *args, **kwargs):
        pass

    def tag_raise(self, *args, **kwargs):
        pass


class DummyHelper:
    def draw_solved_by_connection(self, canvas, parent_pt, child_pt, obj_id=""):
        canvas.create_line(0, 0, 0, 0, tags=(obj_id,))
        canvas.create_polygon([], tags=(obj_id,))

    def draw_in_context_connection(self, *args, **kwargs):
        pass


def test_connection_tags_present():
    parent = GSNNode("P", "Goal")
    child = GSNNode("C", "Goal")
    parent.add_child(child, relation="solved")
    diag = GSNDiagram(parent, drawing_helper=DummyHelper())
    diag.add_node(child)
    diag._draw_node = lambda *a, **k: None  # avoid tkinter font
    canvas = StubCanvas()
    diag.draw(canvas)
    tag = f"{parent.unique_id}->{child.unique_id}"
    assert canvas.lines[0] == (tag,)
    assert canvas.polys[0] == (tag,)
