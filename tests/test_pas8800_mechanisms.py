import sys
import types
from analysis.mechanisms import PAS_8800_MECHANISMS
from analysis.models import MechanismLibrary

def _stub_review_toolbox():
    """Provide a lightweight stub for gui.review_toolbox.

    The real module depends on Pillow which isn't available in the test
    environment.  The application only requires the names of several classes
    when importing, so simple placeholders are sufficient."""
    rt = types.ModuleType("gui.review_toolbox")
    placeholders = [
        "ReviewToolbox",
        "ReviewData",
        "ReviewParticipant",
        "ReviewComment",
        "ParticipantDialog",
        "EmailConfigDialog",
        "ReviewScopeDialog",
        "UserSelectDialog",
        "ReviewDocumentDialog",
        "VersionCompareDialog",
    ]
    for name in placeholders:
        setattr(rt, name, type(name, (), {}))
    sys.modules.setdefault("gui.review_toolbox", rt)


def test_pas8800_contains_fault_aware_training():
    names = [m.name for m in PAS_8800_MECHANISMS]
    assert "Fault-aware training" in names


def test_pas8800_library_non_empty():
    lib = MechanismLibrary("PAS 8800", PAS_8800_MECHANISMS.copy())
    assert len(lib.mechanisms) >= 30


def test_default_mechanisms_include_pas8800():
    _stub_review_toolbox()
    from AutoML import FaultTreeApp

    class Dummy:
        def __init__(self):
            self.mechanism_libraries = []
            self.selected_mechanism_libraries = []

    Dummy.load_default_mechanisms = FaultTreeApp.load_default_mechanisms
    obj = Dummy()
    obj.load_default_mechanisms()

    names = [lib.name for lib in obj.mechanism_libraries]
    selected = [lib.name for lib in obj.selected_mechanism_libraries]
    assert "PAS 8800" in names
    assert "PAS 8800" in selected
