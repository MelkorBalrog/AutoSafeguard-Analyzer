from analysis.mechanisms import PAS_8800_MECHANISMS
from analysis.models import MechanismLibrary


def test_pas8800_contains_fault_aware_training():
    names = [m.name for m in PAS_8800_MECHANISMS]
    assert "Fault-aware training" in names


def test_pas8800_library_non_empty():
    lib = MechanismLibrary("PAS 8800", PAS_8800_MECHANISMS.copy())
    assert len(lib.mechanisms) >= 30
