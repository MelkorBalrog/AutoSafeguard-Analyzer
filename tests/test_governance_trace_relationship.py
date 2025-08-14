import types
import unittest

from gui.architecture import GovernanceDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y

    def configure(self, **kwargs):
        pass


class GovernanceTraceRelationshipTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()
        from gui import architecture

        self._orig_conn_dialog = architecture.ConnectionDialog

    def tearDown(self):
        from gui import architecture

        architecture.ConnectionDialog = self._orig_conn_dialog

    def _create_window(self, src, dst, diag):
        win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
        win.repo = self.repo
        win.diagram_id = diag.diag_id
        win.zoom = 1
        win.canvas = DummyCanvas()
        win.find_object = lambda x, y, prefer_port=False: src if win.start is None else dst
        win.validate_connection = GovernanceDiagramWindow.validate_connection.__get__(
            win, GovernanceDiagramWindow
        )
        win.update_property_view = lambda: None
        win.redraw = lambda: None
        win.current_tool = "Trace"
        win.start = None
        win.temp_line_end = None
        win.selected_obj = None
        win.connections = []
        win._sync_to_repository = lambda: None
        from gui import architecture

        architecture.ConnectionDialog = lambda *args, **kwargs: None
        return win

    def test_trace_relationship_creates_bidirectional_link(self):
        repo = self.repo
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
        repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
        o1 = SysMLObject(
            1,
            "Work Product",
            0,
            0,
            element_id=e1.elem_id,
            properties={"name": "WP1"},
        )
        o2 = SysMLObject(
            2,
            "Work Product",
            0,
            100,
            element_id=e2.elem_id,
            properties={"name": "WP2"},
        )
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window(o1, o2, diag)
        event1 = types.SimpleNamespace(x=0, y=0, state=0)
        GovernanceDiagramWindow.on_left_press(win, event1)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        GovernanceDiagramWindow.on_left_press(win, event2)
        conn = win.connections[0]
        self.assertEqual(conn.conn_type, "Trace")
        self.assertEqual(conn.arrow, "both")
        rel_types = {r.rel_type for r in repo.relationships}
        self.assertEqual(rel_types, {"Trace"})
        self.assertEqual(len(repo.relationships), 2)


if __name__ == "__main__":
    unittest.main()

