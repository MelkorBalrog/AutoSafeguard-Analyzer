import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow


def test_switch_toolbox_handles_governance_elements():
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)

    class Frame:
        def __init__(self):
            self.packed = False
        def pack(self, *a, **k):
            self.packed = True
        def pack_forget(self, *a, **k):
            self.packed = False

    win.gov_tools_frame = Frame()
    win.gov_rel_frame = Frame()
    win.ai_tools_frame = Frame()
    win.gov_elements_frame = Frame()
    win.prop_frame = Frame()

    win.toolbox_var = types.SimpleNamespace(get=lambda: "Governance Elements")
    GovernanceDiagramWindow._switch_toolbox(win)
    assert win.gov_elements_frame.packed
    assert not win.gov_tools_frame.packed

    win.toolbox_var = types.SimpleNamespace(get=lambda: "Governance")
    GovernanceDiagramWindow._switch_toolbox(win)
    assert win.gov_tools_frame.packed
    assert not win.gov_elements_frame.packed
