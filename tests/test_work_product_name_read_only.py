from gui.architecture import SysMLObjectDialog, SysMLObject
from sysml.sysml_repository import SysMLRepository


class DummyVar:
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value


def test_work_product_name_read_only():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    obj = SysMLObject(1, "Work Product", 0.0, 0.0, properties={"name": "Risk Assessment"})
    dlg = SysMLObjectDialog.__new__(SysMLObjectDialog)
    dlg.obj = obj
    dlg.master = object()
    dlg.name_var = DummyVar("Renamed")
    dlg.width_var = DummyVar(str(obj.width))
    dlg.height_var = DummyVar(str(obj.height))
    dlg.entries = {}
    dlg.listboxes = {}
    dlg._operations = []
    dlg._behaviors = []
    dlg.apply()
    assert obj.properties["name"] == "Risk Assessment"


def _make_master(diag_id):
    class DummyMaster:
        pass

    m = DummyMaster()
    m.diagram_id = diag_id
    return m


def test_process_area_name_read_only():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    obj = SysMLObject(
        1,
        "System Boundary",
        0.0,
        0.0,
        properties={"name": "Hazard & Threat Analysis"},
    )
    dlg = SysMLObjectDialog.__new__(SysMLObjectDialog)
    dlg.obj = obj
    dlg.master = _make_master(diag.diag_id)
    dlg.name_var = DummyVar("Renamed")
    dlg.width_var = DummyVar(str(obj.width))
    dlg.height_var = DummyVar(str(obj.height))
    dlg.entries = {}
    dlg.listboxes = {}
    dlg._operations = []
    dlg._behaviors = []
    dlg.apply()
    assert obj.properties["name"] == "Hazard & Threat Analysis"


def test_lifecycle_phase_name_read_only():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance Diagram")
    obj = SysMLObject(1, "Lifecycle Phase", 0.0, 0.0, properties={"name": "Concept"})
    dlg = SysMLObjectDialog.__new__(SysMLObjectDialog)
    dlg.obj = obj
    dlg.master = _make_master(diag.diag_id)
    dlg.name_var = DummyVar("Renamed")
    dlg.width_var = DummyVar(str(obj.width))
    dlg.height_var = DummyVar(str(obj.height))
    dlg.entries = {}
    dlg.listboxes = {}
    dlg._operations = []
    dlg._behaviors = []
    dlg.apply()
    assert obj.properties["name"] == "Concept"
