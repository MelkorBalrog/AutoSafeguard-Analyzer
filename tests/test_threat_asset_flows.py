from sysml.sysml_repository import SysMLRepository, SysMLDiagram
from gui.threat_dialog import ThreatDialog


def test_get_assets_includes_flows():
    repo = SysMLRepository.reset_instance()
    flow_elem = repo.create_element("Flow", name="F1")
    diag = SysMLDiagram(diag_id="d1", diag_type="Internal Block Diagram")
    diag.connections.append({"element_id": flow_elem.elem_id})
    repo.diagrams[diag.diag_id] = diag

    dlg = ThreatDialog.__new__(ThreatDialog)
    assets = dlg._get_assets(diag.diag_id)
    assert "F1" in assets
