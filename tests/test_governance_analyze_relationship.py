import types
import unittest

from gui.architecture import GovernanceDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y

    def configure(self, **kwargs):
        pass


class GovernanceAnalyzeRelationshipTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()
        from gui import architecture
        self._orig_conn_dialog = architecture.ConnectionDialog

    def tearDown(self):
        from gui import architecture
        architecture.ConnectionDialog = self._orig_conn_dialog

    def _create_window(self, tool, src, dst, diag):
        win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
        win.repo = self.repo
        win.diagram_id = diag.diag_id
        win.zoom = 1
        win.canvas = DummyCanvas()
        win.find_object = lambda x, y, prefer_port=False: src if win.start is None else dst
        win.validate_connection = GovernanceDiagramWindow.validate_connection.__get__(win, GovernanceDiagramWindow)
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

    def test_analyze_relationship_stereotype(self):
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
            properties={"name": "Architecture Diagram"},
        )
        o2 = SysMLObject(
            2,
            "Work Product",
            0,
            100,
            element_id=e2.elem_id,
            properties={"name": "FMEA"},
        )
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Analyze", o1, o2, diag)
        event1 = types.SimpleNamespace(x=0, y=0, state=0)
        GovernanceDiagramWindow.on_left_press(win, event1)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        GovernanceDiagramWindow.on_left_press(win, event2)
        self.assertEqual(self.repo.relationships[0].stereotype, "analyze")

    def test_toolbox_can_analyze(self):
        repo = self.repo
        toolbox = SafetyManagementToolbox()
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        toolbox.diagrams["Gov"] = diag.diag_id
        o1 = {"obj_id": 1, "obj_type": "Work Product", "x": 0, "y": 0, "properties": {"name": "Architecture Diagram"}}
        o2 = {"obj_id": 2, "obj_type": "Work Product", "x": 0, "y": 100, "properties": {"name": "FMEA"}}
        diag.objects = [o1, o2]
        diag.connections = [{"src": 1, "dst": 2, "conn_type": "Analyze"}]
        toolbox.add_work_product("Gov", "Architecture Diagram", "")
        toolbox.add_work_product("Gov", "FMEA", "")
        self.assertTrue(toolbox.can_analyze("Architecture Diagram", "FMEA"))
        self.assertIn("Architecture Diagram", toolbox.analysis_inputs("FMEA"))


if __name__ == "__main__":
    unittest.main()
