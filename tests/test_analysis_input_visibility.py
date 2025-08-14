import types
import pytest

from sysml.sysml_repository import SysMLRepository
from gui.architecture import GovernanceDiagramWindow, SysMLObject
from analysis.safety_management import SafetyManagementToolbox, SafetyWorkProduct

ANALYSES = [
    "FI2TC",
    "TC2FI",
    "STPA",
    "Risk Assessment",
    "Threat Analysis",
    "FMEA",
    "FMEDA",
]


class DummyCanvas:
    def canvasx(self, x):
        return x

    def canvasy(self, y):
        return y

    def configure(self, **kwargs):
        pass


def _create_window(repo, tool, src, dst, diag):
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
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
    import gui.architecture as architecture

    architecture.ConnectionDialog = lambda *args, **kwargs: None
    return win


@pytest.mark.parametrize("analysis", ANALYSES)
def test_used_by_input_visibility(analysis):
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams = {"Gov": diag.diag_id}
    e1 = repo.create_element("Block", name="E1")
    e2 = repo.create_element("Block", name="E2")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Work Product", 0, 0, element_id=e1.elem_id, properties={"name": "Architecture Diagram"})
    o2 = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": analysis})
    diag.objects = [o1.__dict__, o2.__dict__]
    win = _create_window(repo, "Used By", o1, o2, diag)
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=0, state=0))
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=100, state=0))
    diag.connections = [c.__dict__ for c in win.connections]
    toolbox.work_products = [
        SafetyWorkProduct("Gov", "Architecture Diagram", ""),
        SafetyWorkProduct("Gov", analysis, ""),
    ]
    assert toolbox.analysis_inputs(analysis) == {"Architecture Diagram"}


@pytest.mark.parametrize("analysis", ANALYSES)
def test_used_after_review_input_visibility(analysis):
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams = {"Gov": diag.diag_id}
    e1 = repo.create_element("Block", name="E1")
    e2 = repo.create_element("Block", name="E2")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Work Product", 0, 0, element_id=e1.elem_id, properties={"name": "Architecture Diagram"})
    o2 = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": analysis})
    diag.objects = [o1.__dict__, o2.__dict__]
    win = _create_window(repo, "Used after Review", o1, o2, diag)
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=0, state=0))
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=100, state=0))
    diag.connections = [c.__dict__ for c in win.connections]
    toolbox.work_products = [
        SafetyWorkProduct("Gov", "Architecture Diagram", ""),
        SafetyWorkProduct("Gov", analysis, ""),
    ]
    assert toolbox.analysis_inputs(analysis) == set()
    assert toolbox.analysis_inputs(analysis, reviewed=True) == {"Architecture Diagram"}
    assert toolbox.analysis_inputs(analysis, approved=True) == {"Architecture Diagram"}


@pytest.mark.parametrize("analysis", ANALYSES)
def test_used_after_approval_input_visibility(analysis):
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams = {"Gov": diag.diag_id}
    e1 = repo.create_element("Block", name="E1")
    e2 = repo.create_element("Block", name="E2")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Work Product", 0, 0, element_id=e1.elem_id, properties={"name": "Architecture Diagram"})
    o2 = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": analysis})
    diag.objects = [o1.__dict__, o2.__dict__]
    win = _create_window(repo, "Used after Approval", o1, o2, diag)
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=0, state=0))
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=100, state=0))
    diag.connections = [c.__dict__ for c in win.connections]
    toolbox.work_products = [
        SafetyWorkProduct("Gov", "Architecture Diagram", ""),
        SafetyWorkProduct("Gov", analysis, ""),
    ]
    assert toolbox.analysis_inputs(analysis) == set()
    assert toolbox.analysis_inputs(analysis, reviewed=True) == set()
    assert toolbox.analysis_inputs(analysis, approved=True) == {"Architecture Diagram"}
