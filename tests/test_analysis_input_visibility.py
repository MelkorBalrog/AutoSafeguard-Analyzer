import types
import pytest

from sysml.sysml_repository import SysMLRepository
from gui.architecture import GovernanceDiagramWindow, SysMLObject
from analysis.safety_management import (
    SafetyManagementToolbox,
    SafetyWorkProduct,
    GovernanceModule,
)

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


def _cfd_tools(app):
    import gui.architecture as architecture

    captured = {}

    def fake_init(self, master, title, tools, diagram_id=None, app=None, history=None, relation_tools=None):
        captured["tools"] = list(tools)
        self.toolbox = object()

    orig = architecture.SysMLDiagramWindow.__init__
    architecture.SysMLDiagramWindow.__init__ = fake_init
    try:
        win = architecture.ControlFlowDiagramWindow.__new__(architecture.ControlFlowDiagramWindow)
        win.__init__(None, app)
    finally:
        architecture.SysMLDiagramWindow.__init__ = orig
    return captured.get("tools", [])


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


@pytest.mark.parametrize("analysis", ["FI2TC", "TC2FI"])
def test_analysis_inputs_respect_phase(analysis):
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams = {"Gov": diag.diag_id}
    toolbox.modules = [GovernanceModule("P1", diagrams=["Gov"]), GovernanceModule("P2")]
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
    toolbox.set_active_module("P2")
    assert toolbox.analysis_inputs(analysis) == set()
    toolbox.set_active_module("P1")
    assert toolbox.analysis_inputs(analysis) == {"Architecture Diagram"}


def test_scenario_library_inputs_require_relationship():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    # Without any governance relationship the Scenario Library has no inputs
    toolbox.work_products = [
        SafetyWorkProduct("Gov", "ODD", ""),
        SafetyWorkProduct("Gov", "Scenario Library", ""),
    ]
    assert toolbox.analysis_inputs("Scenario Library") == set()

    # Create a Used By relationship from ODD to Scenario Library
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams = {"Gov": diag.diag_id}
    e1 = repo.create_element("Block", name="E1")
    e2 = repo.create_element("Block", name="E2")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Work Product", 0, 0, element_id=e1.elem_id, properties={"name": "ODD"})
    o2 = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": "Scenario Library"})
    diag.objects = [o1.__dict__, o2.__dict__]
    win = _create_window(repo, "Used By", o1, o2, diag)
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=0, state=0))
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=100, state=0))
    diag.connections = [c.__dict__ for c in win.connections]
    assert toolbox.analysis_inputs("Scenario Library") == {"ODD"}


def test_scenario_library_inputs_respect_phase():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams = {"Gov": diag.diag_id}
    toolbox.modules = [GovernanceModule("P1", diagrams=["Gov"]), GovernanceModule("P2")]
    e1 = repo.create_element("Block", name="E1")
    e2 = repo.create_element("Block", name="E2")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Work Product", 0, 0, element_id=e1.elem_id, properties={"name": "ODD"})
    o2 = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": "Scenario Library"})
    diag.objects = [o1.__dict__, o2.__dict__]
    win = _create_window(repo, "Used By", o1, o2, diag)
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=0, state=0))
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=100, state=0))
    diag.connections = [c.__dict__ for c in win.connections]
    toolbox.work_products = [
        SafetyWorkProduct("Gov", "ODD", ""),
        SafetyWorkProduct("Gov", "Scenario Library", ""),
    ]
    toolbox.set_active_module("P2")
    assert toolbox.analysis_inputs("Scenario Library") == set()
    toolbox.set_active_module("P1")
    assert toolbox.analysis_inputs("Scenario Library") == {"ODD"}

def test_stpa_button_requires_relationship():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    app = types.SimpleNamespace(
        safety_mgmt_toolbox=toolbox,
        current_review=types.SimpleNamespace(reviewed=False, approved=False),
    )

    toolbox.work_products = [
        SafetyWorkProduct("Gov", "Architecture Diagram", ""),
        SafetyWorkProduct("Gov", "STPA", ""),
    ]
    assert "STPA Analysis" not in _cfd_tools(app)

    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams = {"Gov": diag.diag_id}
    e1 = repo.create_element("Block", name="E1")
    e2 = repo.create_element("Block", name="E2")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Work Product", 0, 0, element_id=e1.elem_id, properties={"name": "Architecture Diagram"})
    o2 = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": "STPA"})
    diag.objects = [o1.__dict__, o2.__dict__]
    win = _create_window(repo, "Used By", o1, o2, diag)
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=0, state=0))
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=100, state=0))
    diag.connections = [c.__dict__ for c in win.connections]
    assert "STPA Analysis" in _cfd_tools(app)


def test_stpa_button_respects_review_and_approval():
    # Used after Review relationship
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
    o2 = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": "STPA"})
    diag.objects = [o1.__dict__, o2.__dict__]
    toolbox.work_products = [
        SafetyWorkProduct("Gov", "Architecture Diagram", ""),
        SafetyWorkProduct("Gov", "STPA", ""),
    ]
    win = _create_window(repo, "Used after Review", o1, o2, diag)
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=0, state=0))
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=100, state=0))
    diag.connections = [c.__dict__ for c in win.connections]
    app = types.SimpleNamespace(
        safety_mgmt_toolbox=toolbox,
        current_review=types.SimpleNamespace(reviewed=False, approved=False),
    )
    assert "STPA Analysis" not in _cfd_tools(app)
    app.current_review.reviewed = True
    assert "STPA Analysis" in _cfd_tools(app)

    # Used after Approval relationship
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
    o2 = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": "STPA"})
    diag.objects = [o1.__dict__, o2.__dict__]
    toolbox.work_products = [
        SafetyWorkProduct("Gov", "Architecture Diagram", ""),
        SafetyWorkProduct("Gov", "STPA", ""),
    ]
    win = _create_window(repo, "Used after Approval", o1, o2, diag)
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=0, state=0))
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=100, state=0))
    diag.connections = [c.__dict__ for c in win.connections]
    app = types.SimpleNamespace(
        safety_mgmt_toolbox=toolbox,
        current_review=types.SimpleNamespace(reviewed=False, approved=False),
    )
    assert "STPA Analysis" not in _cfd_tools(app)
    app.current_review.approved = True
    assert "STPA Analysis" in _cfd_tools(app)


def test_stpa_button_respects_phase():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    diag = repo.create_diagram("Governance Diagram", name="Gov")
    toolbox.diagrams = {"Gov": diag.diag_id}
    toolbox.modules = [GovernanceModule("P1", diagrams=["Gov"]), GovernanceModule("P2")]
    e1 = repo.create_element("Block", name="E1")
    e2 = repo.create_element("Block", name="E2")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    o1 = SysMLObject(1, "Work Product", 0, 0, element_id=e1.elem_id, properties={"name": "Architecture Diagram"})
    o2 = SysMLObject(2, "Work Product", 0, 100, element_id=e2.elem_id, properties={"name": "STPA"})
    diag.objects = [o1.__dict__, o2.__dict__]
    win = _create_window(repo, "Used By", o1, o2, diag)
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=0, state=0))
    GovernanceDiagramWindow.on_left_press(win, types.SimpleNamespace(x=0, y=100, state=0))
    diag.connections = [c.__dict__ for c in win.connections]

    toolbox.work_products = [
        SafetyWorkProduct("Gov", "Architecture Diagram", ""),
        SafetyWorkProduct("Gov", "STPA", ""),
    ]

    app = types.SimpleNamespace(
        safety_mgmt_toolbox=toolbox,
        current_review=types.SimpleNamespace(reviewed=False, approved=False),
    )
    toolbox.set_active_module("P2")
    assert "STPA Analysis" not in _cfd_tools(app)
    toolbox.set_active_module("P1")
    assert "STPA Analysis" in _cfd_tools(app)
