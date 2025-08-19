from analysis.safety_management import SafetyManagementToolbox
from analysis import safety_management

def test_add_module_enforces_unique_names():
    prev = safety_management.ACTIVE_TOOLBOX
    tb = SafetyManagementToolbox()
    tb.add_module("Phase")
    tb.add_module("Phase")
    parent = tb.add_module("Parent")
    child = tb.add_module("Phase", parent=parent)
    assert [m.name for m in tb.modules] == ["Phase", "Phase_1", "Parent"]
    assert child.name == "Phase_2"
    assert tb.list_modules() == ["Phase", "Phase_1", "Parent", "Phase_2", "GLOBAL"]
    assert len(set(tb.list_modules())) == 5
    safety_management.ACTIVE_TOOLBOX = prev
