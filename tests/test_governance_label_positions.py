import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import _BOTTOM_LABEL_TYPES


def test_governance_names_after_shape():
    for obj_type in ("Organization", "Model", "Business Unit"):
        assert obj_type in _BOTTOM_LABEL_TYPES
