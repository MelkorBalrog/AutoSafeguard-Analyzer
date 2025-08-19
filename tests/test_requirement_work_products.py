import types

from analysis.models import REQUIREMENT_TYPE_OPTIONS
from gui.architecture import GovernanceDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository
from AutoML import AutoMLApp


def _fmt(req: str) -> str:
    return " ".join(
        word.upper() if word.isupper() else word.capitalize() for word in req.split()
    )


def test_work_product_created_for_each_requirement_type():
    for req in REQUIREMENT_TYPE_OPTIONS:
        name = f"{_fmt(req)} Requirement Specification"
        assert name in AutoMLApp.WORK_PRODUCT_INFO


def test_add_requirement_work_product(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Gov")
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    win.repo = repo
    win.diagram_id = diag.diag_id
    win.objects = [
        SysMLObject(
            1,
            "System Boundary",
            0.0,
            0.0,
            width=200.0,
            height=150.0,
            properties={"name": "System Design (Item Definition)"},
        )
    ]
    win.sort_objects = lambda: None
    win._sync_to_repository = lambda: None
    win.redraw = lambda: None
    added = []
    win.app = types.SimpleNamespace(enable_work_product=lambda name, *, refresh=True: added.append(name))

    name = f"{_fmt(REQUIREMENT_TYPE_OPTIONS[2])} Requirement Specification"

    class FakeDialog:
        def __init__(self, *args, **kwargs):
            self.selection = name

    monkeypatch.setattr(GovernanceDiagramWindow, "_SelectDialog", FakeDialog)

    win.add_work_product()

    assert added == [name]
    assert any(o.properties.get("name") == name for o in win.objects)

