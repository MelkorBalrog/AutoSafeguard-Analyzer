import types
import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject, format_control_flow_label
from sysml.sysml_repository import SysMLRepository


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y

    def configure(self, **kwargs):
        pass


class ControlFlowStereotypeTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()
        from gui import architecture
        self._orig_conn_dialog = architecture.ConnectionDialog

    def tearDown(self):
        from gui import architecture
        architecture.ConnectionDialog = self._orig_conn_dialog

    def _create_window(self, tool, src, dst, diag):
        win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
        win.repo = self.repo
        win.diagram_id = diag.diag_id
        win.zoom = 1
        win.canvas = DummyCanvas()
        win.find_object = lambda x, y, prefer_port=False: src if win.start is None else dst
        win.validate_connection = SysMLDiagramWindow.validate_connection.__get__(win, SysMLDiagramWindow)
        win.update_property_view = lambda: None
        win.redraw = lambda: None
        win.current_tool = tool
        win.start = None
        win.temp_line_end = None
        win.selected_obj = None
        win.connections = []
        win._sync_to_repository = lambda: None
        from gui import architecture
        architecture.ConnectionDialog = lambda *args, **kwargs: None
        return win

    def test_control_action_relationship_stereotype(self):
        repo = self.repo
        e1 = repo.create_element("Block", name="A")
        e2 = repo.create_element("Block", name="B")
        diag = repo.create_diagram("Control Flow Diagram", name="CF")
        repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
        repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
        o1 = SysMLObject(1, "Existing Element", 0, 0, element_id=e1.elem_id)
        o2 = SysMLObject(2, "Existing Element", 0, 100, element_id=e2.elem_id)
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Control Action", o1, o2, diag)
        event = types.SimpleNamespace(x=0, y=0, state=0)
        SysMLDiagramWindow.on_left_press(win, event)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        SysMLDiagramWindow.on_left_press(win, event2)
        self.assertEqual(repo.relationships[0].stereotype, "control action")
        self.assertEqual(win.connections[0].stereotype, "control action")
        self.assertEqual(
            format_control_flow_label(win.connections[0], repo, diag.diag_type),
            "<<control action>>",
        )

    def test_feedback_relationship_stereotype(self):
        repo = self.repo
        e1 = repo.create_element("Block", name="A")
        e2 = repo.create_element("Block", name="B")
        diag = repo.create_diagram("Control Flow Diagram", name="CF")
        repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
        repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
        o1 = SysMLObject(1, "Existing Element", 0, 0, element_id=e1.elem_id)
        o2 = SysMLObject(2, "Existing Element", 0, 100, element_id=e2.elem_id)
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Feedback", o1, o2, diag)
        event = types.SimpleNamespace(x=0, y=0, state=0)
        SysMLDiagramWindow.on_left_press(win, event)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        SysMLDiagramWindow.on_left_press(win, event2)
        self.assertEqual(repo.relationships[0].stereotype, "feedback")
        self.assertEqual(win.connections[0].stereotype, "feedback")
        self.assertEqual(
            format_control_flow_label(win.connections[0], repo, diag.diag_type),
            "<<feedback>>",
        )


if __name__ == "__main__":
    unittest.main()
