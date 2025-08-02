import unittest
from gui.architecture import (
    _aggregation_exists,
    SysMLDiagramWindow,
    SysMLObject,
    add_aggregation_part,
    extend_block_parts_with_parents,
)
from sysml.sysml_repository import SysMLRepository, SysMLDiagram

class AggregationExistsTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_direct_relationship(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Aggregation", whole.elem_id, part.elem_id)
        self.assertTrue(_aggregation_exists(repo, whole.elem_id, part.elem_id))

    def test_inherited_relationship(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        repo.create_relationship("Composite Aggregation", parent.elem_id, part.elem_id)
        self.assertTrue(_aggregation_exists(repo, child.elem_id, part.elem_id))

    def test_father_part_definition(self):
        repo = self.repo
        father = repo.create_element("Block", name="Father")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="Part")
        diag_f = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(father.elem_id, diag_f.diag_id)
        part_elem = repo.create_element("Part", name="P", properties={"definition": part.elem_id})
        diag_f.objects.append({
            "obj_id": 1,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": part_elem.elem_id,
            "properties": {"definition": part.elem_id},
        })
        diag_c = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, diag_c.diag_id)
        diag_c.father = father.elem_id
        self.assertTrue(_aggregation_exists(repo, child.elem_id, part.elem_id))

    def test_negative_case(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        self.assertFalse(_aggregation_exists(repo, a.elem_id, b.elem_id))


class ReciprocalAggregationTests(unittest.TestCase):
    class DummyWindow:
        def __init__(self):
            self.repo = SysMLRepository.get_instance()
            diag = SysMLDiagram(diag_id="d", diag_type="Block Diagram")
            self.repo.diagrams[diag.diag_id] = diag
            self.diagram_id = diag.diag_id

    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_reciprocal_aggregation_invalid(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Aggregation", a.elem_id, b.elem_id)
        win = self.DummyWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=b.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=a.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Aggregation")
        self.assertFalse(valid)

    def test_reciprocal_composite_aggregation_invalid(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Composite Aggregation", a.elem_id, b.elem_id)
        win = self.DummyWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=b.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=a.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Composite Aggregation")
        self.assertFalse(valid)


class AggregationSanityTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_parent_as_part_ignored(self):
        repo = self.repo
        parent = repo.create_element("Block", name="P")
        child = repo.create_element("Block", name="C")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        add_aggregation_part(repo, child.elem_id, parent.elem_id)
        props = repo.elements[child.elem_id].properties.get("partProperties", "")
        self.assertNotIn("P", props)
        self.assertFalse(
            any(
                r.rel_type in ("Aggregation", "Composite Aggregation")
                and r.source == child.elem_id
                and r.target == parent.elem_id
                for r in repo.relationships
            )
        )

    def test_self_part_ignored(self):
        repo = self.repo
        blk = repo.create_element("Block", name="Self")
        add_aggregation_part(repo, blk.elem_id, blk.elem_id)
        props = repo.elements[blk.elem_id].properties.get("partProperties", "")
        self.assertEqual(props, "")
        self.assertFalse(
            any(
                r.source == blk.elem_id and r.target == blk.elem_id for r in repo.relationships
            )
        )

if __name__ == "__main__":
    unittest.main()
