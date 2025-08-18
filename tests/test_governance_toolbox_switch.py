import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow


def test_switch_toolbox_combines_governance_elements():
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)

    class Frame:
        def __init__(self):
            self.packed = False

        def pack(self, *a, **k):
            self.packed = True

        def pack_forget(self, *a, **k):
            self.packed = False

    gov_frame = Frame()
    ai_frame = Frame()
    win._toolbox_frames = {
        "Governance": [gov_frame],
        "Safety & AI Lifecycle": [ai_frame],
    }

    win.toolbox_var = types.SimpleNamespace(get=lambda: "Governance")
    GovernanceDiagramWindow._switch_toolbox(win)
    assert gov_frame.packed
    assert not ai_frame.packed

    win.toolbox_var = types.SimpleNamespace(get=lambda: "Safety & AI Lifecycle")
    GovernanceDiagramWindow._switch_toolbox(win)
    assert ai_frame.packed
    assert not gov_frame.packed

