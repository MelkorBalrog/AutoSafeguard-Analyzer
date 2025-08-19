import types
from sysml.sysml_repository import SysMLRepository
from analysis.safety_management import SafetyManagementToolbox, GovernanceModule
from AutoML import AutoMLApp


def test_global_phase_included_when_root_diagram_exists():
    repo = SysMLRepository.reset_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.modules = [GovernanceModule("P1")]
    toolbox.create_diagram("RootDiag")
    app = AutoMLApp.__new__(AutoMLApp)
    app.safety_mgmt_toolbox = toolbox
    captured = {}

    class DummyCB:
        def configure(self, **kwargs):
            captured.update(kwargs)

    app.lifecycle_cb = DummyCB()
    app.lifecycle_var = types.SimpleNamespace(set=lambda _v: None)
    app.update_lifecycle_cb()
    assert "GLOBAL" in captured.get("values", [])
