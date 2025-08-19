import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.safety_management import SafetyManagementToolbox
from sysml.sysml_repository import SysMLRepository


def test_set_all_diagrams_frozen():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    tb = SafetyManagementToolbox()
    d1 = tb.create_diagram("Gov1")
    d2 = tb.create_diagram("Gov2")
    tb.set_all_diagrams_frozen(True)
    assert repo.diagram_read_only(d1)
    assert repo.diagram_read_only(d2)
    tb.set_all_diagrams_frozen(False)
    assert not repo.diagram_read_only(d1)
    assert not repo.diagram_read_only(d2)
