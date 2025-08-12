import types
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analysis.models import HaraDoc
from gui.toolboxes import RiskAssessmentWindow


def test_edit_doc_updates_selections(monkeypatch):
    doc = HaraDoc("RA1", ["HZ1"], [], False, "draft", stpa="STPA1", threat="TA1")
    app = types.SimpleNamespace(
        active_hara=doc,
        hara_docs=[doc],
        update_views=lambda: None,
    )

    window = RiskAssessmentWindow.__new__(RiskAssessmentWindow)
    window.app = app
    window.refresh_docs = lambda: None
    window.refresh = lambda: None

    class DummyDialog:
        def __init__(self, *a, **k):
            self.result = ("HZ2", "STPA2", "TA2")

    monkeypatch.setattr(RiskAssessmentWindow, "EditAssessmentDialog", DummyDialog)

    window.edit_doc()

    assert doc.hazops == ["HZ2"]
    assert doc.stpa == "STPA2"
    assert doc.threat == "TA2"
