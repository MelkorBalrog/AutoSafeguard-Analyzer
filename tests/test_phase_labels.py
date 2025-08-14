import unittest

from gui import format_name_with_phase
from gui.architecture import SysMLDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository


class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)

    def metrics(self, name: str) -> int:
        return 1


class DummyWindow:
    _object_label_lines = SysMLDiagramWindow._object_label_lines

    def __init__(self, diag_id):
        self.repo = SysMLRepository.get_instance()
        self.zoom = 1.0
        self.font = DummyFont()
        self.diagram_id = diag_id


class PhaseLabelTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None

    def test_format_helper(self):
        self.assertEqual(format_name_with_phase("Name", "P1"), "Name (P1)")
        self.assertEqual(format_name_with_phase("Name", None), "Name")

    def test_object_label_omits_phase(self):
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Block Diagram")
        elem = repo.create_element("Use Case", name="Do")
        elem.phase = "PhaseX"
        obj = SysMLObject(1, "Use Case", 0.0, 0.0, element_id=elem.elem_id, phase="PhaseX")
        win = DummyWindow(diag.diag_id)
        lines = win._object_label_lines(obj)
        text = " ".join(lines)
        self.assertIn("Do", text)
        self.assertNotIn("PhaseX", text)

    def test_governance_label_omits_phase(self):
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Governance Diagram")
        elem = repo.create_element("Use Case", name="Check")
        elem.phase = "PhaseZ"
        obj = SysMLObject(
            2,
            "Work Product",
            0.0,
            0.0,
            element_id=elem.elem_id,
            phase="PhaseZ",
            properties={"name": "Check"},
        )
        win = DummyWindow(diag.diag_id)
        lines = win._object_label_lines(obj)
        self.assertIn("Check", " ".join(lines))
        self.assertNotIn("PhaseZ", " ".join(lines))

    def test_safety_management_explorer_omits_phase(self):
        from gui.safety_management_explorer import SafetyManagementExplorer
        from analysis.safety_management import SafetyManagementToolbox

        repo = SysMLRepository.get_instance()
        toolbox = SafetyManagementToolbox()
        diag_id = toolbox.create_diagram("GovDiag")
        repo.diagrams[diag_id].phase = "Phase1"

        explorer = SafetyManagementExplorer.__new__(SafetyManagementExplorer)

        class DummyTree:
            def __init__(self):
                self.items = {}
                self.counter = 0

            def delete(self, *items):
                self.items = {}

            def get_children(self, item=""):
                return [iid for iid, meta in self.items.items() if meta["parent"] == item]

            def insert(self, parent, index, text="", image=None, **_kwargs):
                iid = f"i{self.counter}"
                self.counter += 1
                self.items[iid] = {"parent": parent, "text": text}
                return iid

        explorer.tree = DummyTree()
        explorer.toolbox = toolbox
        explorer.item_map = {}
        explorer.folder_icon = None
        explorer.diagram_icon = None

        SafetyManagementExplorer.populate(explorer)

        texts = [meta["text"] for meta in explorer.tree.items.values()]
        self.assertIn("GovDiag", texts)
        self.assertTrue(all("Phase1" not in t for t in texts))

if __name__ == "__main__":
    unittest.main()

