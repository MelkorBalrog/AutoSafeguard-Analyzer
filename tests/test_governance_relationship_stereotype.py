import types
import unittest

from gui.architecture import GovernanceDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox, SafetyWorkProduct


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y

    def configure(self, **kwargs):
        pass


class GovernanceRelationshipStereotypeTests(unittest.TestCase):
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
        win.validate_connection = GovernanceDiagramWindow.validate_connection.__get__(
            win, GovernanceDiagramWindow
        )
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

    def test_propagate_relationship_stereotype(self):
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
            properties={"name": "Risk Assessment"},
        )
        o2 = SysMLObject(
            2,
            "Work Product",
            0,
            100,
            element_id=e2.elem_id,
            properties={"name": "FTA"},
        )
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Propagate", o1, o2, diag)
        event1 = types.SimpleNamespace(x=0, y=0, state=0)
        GovernanceDiagramWindow.on_left_press(win, event1)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        GovernanceDiagramWindow.on_left_press(win, event2)
        self.assertEqual(repo.relationships[0].stereotype, "propagate")

    def test_used_by_relationship_stereotype(self):
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
            properties={"name": "FTA"},
        )
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Used By", o1, o2, diag)
        event1 = types.SimpleNamespace(x=0, y=0, state=0)
        GovernanceDiagramWindow.on_left_press(win, event1)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        GovernanceDiagramWindow.on_left_press(win, event2)
        self.assertEqual(repo.relationships[0].stereotype, "used by")

    def test_used_after_review_relationship_stereotype(self):
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
            properties={"name": "FTA"},
        )
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Used after Review", o1, o2, diag)
        event1 = types.SimpleNamespace(x=0, y=0, state=0)
        GovernanceDiagramWindow.on_left_press(win, event1)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        GovernanceDiagramWindow.on_left_press(win, event2)
        self.assertEqual(repo.relationships[0].stereotype, "used after review")

    def test_used_after_approval_relationship_stereotype(self):
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
            properties={"name": "FTA"},
        )
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Used after Approval", o1, o2, diag)
        event1 = types.SimpleNamespace(x=0, y=0, state=0)
        GovernanceDiagramWindow.on_left_press(win, event1)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        GovernanceDiagramWindow.on_left_press(win, event2)
        self.assertEqual(repo.relationships[0].stereotype, "used after approval")

    def test_used_relationship_validation(self):
        repo = self.repo
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
        win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
        win.repo = repo
        win.diagram_id = diag.diag_id
        rels = ["Used By", "Used after Review", "Used after Approval"]
        for rel in rels:
            o1 = SysMLObject(
                1,
                "Work Product",
                0,
                0,
                element_id=e1.elem_id,
                properties={"name": "Mission Profile"},
            )
            o2 = SysMLObject(
                2,
                "Work Product",
                0,
                100,
                element_id=e2.elem_id,
                properties={"name": "Architecture Diagram"},
            )
            valid, _ = GovernanceDiagramWindow.validate_connection(win, o1, o2, rel)
            self.assertFalse(valid)
            o2 = SysMLObject(
                2,
                "Work Product",
                0,
                100,
                element_id=e2.elem_id,
                properties={"name": "FTA"},
            )
            valid, _ = GovernanceDiagramWindow.validate_connection(win, o1, o2, rel)
            self.assertTrue(valid)

    def test_analysis_targets_mapping(self):
        repo = self.repo
        toolbox = SafetyManagementToolbox()
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        toolbox.diagrams = {"Gov": diag.diag_id}
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
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
            properties={"name": "FTA"},
        )
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Used By", o1, o2, diag)
        event1 = types.SimpleNamespace(x=0, y=0, state=0)
        GovernanceDiagramWindow.on_left_press(win, event1)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        GovernanceDiagramWindow.on_left_press(win, event2)
        diag.connections = [c.__dict__ for c in win.connections]
        toolbox.work_products = [
            SafetyWorkProduct("Gov", "Architecture Diagram", ""),
            SafetyWorkProduct("Gov", "FTA", ""),
        ]
        targets = toolbox.analysis_targets("Architecture Diagram")
        self.assertEqual(targets, {"FTA"})

    def test_analysis_targets_used_after_review_visibility(self):
        repo = self.repo
        toolbox = SafetyManagementToolbox()
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        toolbox.diagrams = {"Gov": diag.diag_id}
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
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
            properties={"name": "FTA"},
        )
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Used after Review", o1, o2, diag)
        event1 = types.SimpleNamespace(x=0, y=0, state=0)
        GovernanceDiagramWindow.on_left_press(win, event1)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        GovernanceDiagramWindow.on_left_press(win, event2)
        diag.connections = [c.__dict__ for c in win.connections]
        toolbox.work_products = [
            SafetyWorkProduct("Gov", "Architecture Diagram", ""),
            SafetyWorkProduct("Gov", "FTA", ""),
        ]
        self.assertEqual(toolbox.analysis_targets("Architecture Diagram"), set())
        self.assertEqual(
            toolbox.analysis_targets("Architecture Diagram", reviewed=True), {"FTA"}
        )
        self.assertEqual(
            toolbox.analysis_targets("Architecture Diagram", approved=True), {"FTA"}
        )

    def test_analysis_targets_used_after_approval_visibility(self):
        repo = self.repo
        toolbox = SafetyManagementToolbox()
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        toolbox.diagrams = {"Gov": diag.diag_id}
        e1 = repo.create_element("Block", name="E1")
        e2 = repo.create_element("Block", name="E2")
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
            properties={"name": "FTA"},
        )
        diag.objects = [o1.__dict__, o2.__dict__]
        win = self._create_window("Used after Approval", o1, o2, diag)
        event1 = types.SimpleNamespace(x=0, y=0, state=0)
        GovernanceDiagramWindow.on_left_press(win, event1)
        event2 = types.SimpleNamespace(x=0, y=100, state=0)
        GovernanceDiagramWindow.on_left_press(win, event2)
        diag.connections = [c.__dict__ for c in win.connections]
        toolbox.work_products = [
            SafetyWorkProduct("Gov", "Architecture Diagram", ""),
            SafetyWorkProduct("Gov", "FTA", ""),
        ]
        self.assertEqual(toolbox.analysis_targets("Architecture Diagram"), set())
        self.assertEqual(
            toolbox.analysis_targets("Architecture Diagram", reviewed=True), set()
        )
        self.assertEqual(
            toolbox.analysis_targets("Architecture Diagram", approved=True), {"FTA"}
        )


if __name__ == "__main__":
    unittest.main()

