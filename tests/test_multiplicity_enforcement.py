import unittest
from unittest.mock import patch

from gui import architecture
from gui.architecture import SysMLObject, InternalBlockDiagramWindow
from sysml.sysml_repository import SysMLRepository

class DummyWindow:
    _get_part_name = InternalBlockDiagramWindow._get_part_name
    def __init__(self, diagram):
        self.repo = SysMLRepository.get_instance()
        self.diagram_id = diagram.diag_id
        self.objects = []
        self.connections = []
        self.app = None
    def _sync_to_repository(self):
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag:
            diag.objects = [obj.__dict__ for obj in self.objects]
            diag.connections = [conn.__dict__ for conn in self.connections]
            architecture.update_block_parts_from_ibd(self.repo, diag)
            self.repo.touch_diagram(self.diagram_id)
            architecture._sync_block_parts_from_ibd(self.repo, self.diagram_id)
    def redraw(self):
        pass

class MultiplicityEnforcementTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_contained_parts_respects_multiplicity(self):
        repo = self.repo
        whole = repo.create_element("Block", name="W")
        part = repo.create_element("Block", name="P")
        architecture.add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "2")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        win = DummyWindow(ibd)
        class DummyDialog:
            def __init__(self, parent, names, visible, hidden):
                self.result = ["P"]
        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', DummyDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)
            InternalBlockDiagramWindow.add_contained_parts(win)
        objs = [
            o for o in repo.diagrams[ibd.diag_id].objects
            if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 2)
        names = {repo.elements[o["element_id"]].name for o in objs}
        self.assertIn("P[1]", names)
        self.assertIn("P[2]", names)

if __name__ == '__main__':
    unittest.main()
