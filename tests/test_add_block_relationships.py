import unittest
from gui.architecture import BlockDiagramWindow, SysMLObject, _get_next_id
from sysml.sysml_repository import SysMLRepository

class DummyWindow:
    _add_block_relationships = BlockDiagramWindow._add_block_relationships
    def __init__(self, diagram):
        self.repo = SysMLRepository.get_instance()
        self.diagram_id = diagram.diag_id
        self.objects = []
        self.connections = []

    def redraw(self):
        pass

    def _sync_to_repository(self):
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag:
            diag.objects = [o.__dict__ for o in self.objects]
            diag.connections = [c.__dict__ for c in self.connections]

class AddBlockRelationshipsTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_relationships_added_when_blocks_imported(self):
        repo = self.repo
        d1 = repo.create_diagram("Block Diagram", name="D1")
        d2 = repo.create_diagram("Block Diagram", name="D2")
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        c = repo.create_element("Block", name="C")

        repo.add_element_to_diagram(d2.diag_id, a.elem_id)
        repo.add_element_to_diagram(d2.diag_id, b.elem_id)
        repo.add_element_to_diagram(d2.diag_id, c.elem_id)
        d2.objects = [
            {"obj_id": 1, "obj_type": "Block", "x": 0, "y": 0, "element_id": a.elem_id},
            {"obj_id": 2, "obj_type": "Block", "x": 0, "y": 0, "element_id": b.elem_id},
            {"obj_id": 3, "obj_type": "Block", "x": 0, "y": 0, "element_id": c.elem_id},
        ]

        rel_ab = repo.create_relationship("Association", a.elem_id, b.elem_id)
        repo.add_relationship_to_diagram(d2.diag_id, rel_ab.rel_id)
        rel_bc = repo.create_relationship("Association", b.elem_id, c.elem_id)
        repo.add_relationship_to_diagram(d2.diag_id, rel_bc.rel_id)

        win = DummyWindow(d1)

        # add A
        repo.add_element_to_diagram(d1.diag_id, a.elem_id)
        obj_a = SysMLObject(_get_next_id(), "Block", 0, 0, element_id=a.elem_id)
        d1.objects.append(obj_a.__dict__)
        win.objects.append(obj_a)
        win._add_block_relationships()
        self.assertEqual(len(win.connections), 0)

        # add B
        repo.add_element_to_diagram(d1.diag_id, b.elem_id)
        obj_b = SysMLObject(_get_next_id(), "Block", 0, 0, element_id=b.elem_id)
        d1.objects.append(obj_b.__dict__)
        win.objects.append(obj_b)
        win._add_block_relationships()
        self.assertEqual(len(win.connections), 1)
        self.assertIn(rel_ab.rel_id, repo.diagrams[d1.diag_id].relationships)

        # add C
        repo.add_element_to_diagram(d1.diag_id, c.elem_id)
        obj_c = SysMLObject(_get_next_id(), "Block", 0, 0, element_id=c.elem_id)
        d1.objects.append(obj_c.__dict__)
        win.objects.append(obj_c)
        win._add_block_relationships()
        self.assertEqual(len(win.connections), 2)
        self.assertIn(rel_bc.rel_id, repo.diagrams[d1.diag_id].relationships)

if __name__ == '__main__':
    unittest.main()
