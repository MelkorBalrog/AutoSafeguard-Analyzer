import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.safety_management import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository


def test_manual_freeze_persists_across_save():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    tb = SafetyManagementToolbox()
    diag_id = tb.create_diagram("Gov1")
    tb.set_diagram_frozen("Gov1", True)
    assert repo.diagram_read_only(diag_id)

    repo_data = repo.to_dict()
    tb_data = tb.to_dict()

    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    repo.from_dict(repo_data)
    tb2 = SafetyManagementToolbox.from_dict(tb_data)
    diag_id2 = tb2.diagrams["Gov1"]
    assert repo.diagram_read_only(diag_id2)

    tb2.set_diagram_frozen("Gov1", False)
    assert not repo.diagram_read_only(diag_id2)
