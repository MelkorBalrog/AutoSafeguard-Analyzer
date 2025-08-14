from gui import messagebox
from gui.architecture import ArchitectureManagerDialog
from sysml.sysml_repository import SysMLRepository


def test_drop_governance_diagram_creates_action(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    src = repo.create_diagram("Governance Diagram", name="Src")
    target = repo.create_diagram("Governance Diagram", name="Target")

    mgr = ArchitectureManagerDialog.__new__(ArchitectureManagerDialog)
    mgr.repo = repo

    errors = []
    monkeypatch.setattr(messagebox, "showerror", lambda *args: errors.append(args[1]))

    mgr._drop_on_diagram(f"diag_{src.diag_id}", target)

    assert not errors
    assert any(obj["obj_type"] == "Action" for obj in target.objects)
    elem_id = next(obj["element_id"] for obj in target.objects if obj["obj_type"] == "Action")
    assert repo.elements[elem_id].elem_type == "Action"
    assert repo.get_linked_diagram(elem_id) == src.diag_id


def test_drop_non_governance_diagram_on_governance_fails(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    src = repo.create_diagram("Activity Diagram", name="Act")
    target = repo.create_diagram("Governance Diagram", name="Target")

    mgr = ArchitectureManagerDialog.__new__(ArchitectureManagerDialog)
    mgr.repo = repo

    errors = []
    monkeypatch.setattr(messagebox, "showerror", lambda *args: errors.append(args[1]))

    mgr._drop_on_diagram(f"diag_{src.diag_id}", target)

    assert errors
    assert target.objects == []
