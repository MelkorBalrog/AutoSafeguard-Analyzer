import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis import SafetyManagementToolbox
from main.AutoML import AutoMLApp, FaultTreeNode
from sysml.sysml_repository import SysMLRepository


def test_paa_group_not_duplicated(monkeypatch):
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    toolbox = SafetyManagementToolbox()
    toolbox.create_diagram("Gov")
    repo.create_diagram("Block Definition Diagram", name="Arch")

    class DummyTree:
        def __init__(self):
            self.items = {}
            self.counter = 0

        def delete(self, *items):
            pass

        def get_children(self, item=""):
            return [iid for iid, meta in self.items.items() if meta["parent"] == item]

        def insert(self, parent, index, iid=None, text="", **kwargs):
            if iid is None:
                iid = f"i{self.counter}"
                self.counter += 1
            self.items[iid] = {"parent": parent, "text": text}
            return iid

    app = AutoMLApp.__new__(AutoMLApp)
    app.refresh_model = lambda: None
    app.compute_occurrence_counts = lambda: {}
    app.diagram_icons = {}
    app.hazop_docs = []
    app.stpa_docs = []
    app.threat_docs = []
    app.fi2tc_docs = []
    app.tc2fi_docs = []
    app.hara_docs = []
    app.fmeas = []
    app.fmedas = []
    app.analysis_tree = DummyTree()
    app.update_lifecycle_cb = lambda: None
    app.refresh_tool_enablement = lambda: None
    app.enabled_work_products = set()
    app.safety_mgmt_toolbox = toolbox
    toolbox.document_visible = lambda analysis, name: True
    toolbox.enabled_products = lambda: {"Prototype Assurance Analysis"}

    paa_event1 = FaultTreeNode("p1", "TOP EVENT")
    paa_event1.analysis_mode = "PAA"
    paa_event2 = FaultTreeNode("p2", "TOP EVENT")
    paa_event2.analysis_mode = "PAA"
    app.top_events = [paa_event1]
    app.paa_events = [paa_event2]

    app.update_views()
    names = [meta["text"] for meta in app.analysis_tree.items.values()]
    assert names.count("PAAs") == 1
