# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
from sysml.sysml_repository import SysMLRepository
from gui.architecture import extend_block_parts_with_parents, inherit_father_parts

class InheritPartsTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_extend_block_parts_with_parents(self):
        repo = self.repo
        a = repo.create_element("Block", name="A", properties={"partProperties": "a1"})
        b = repo.create_element("Block", name="B", properties={"partProperties": "b1"})
        c = repo.create_element("Block", name="C", properties={"partProperties": "c1"})
        d = repo.create_element("Block", name="D", properties={"partProperties": "d1"})

        da = repo.create_diagram("Internal Block Diagram", name="A")
        repo.link_diagram(a.elem_id, da.diag_id)
        db = repo.create_diagram("Internal Block Diagram", name="B")
        repo.link_diagram(b.elem_id, db.diag_id)
        dc = repo.create_diagram("Internal Block Diagram", name="C")
        repo.link_diagram(c.elem_id, dc.diag_id)

        pb = repo.create_element("Part", name="PB")
        da.objects.append({
            "obj_id": 1,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": pb.elem_id,
            "properties": {"definition": b.elem_id},
        })
        pc = repo.create_element("Part", name="PC")
        db.objects.append({
            "obj_id": 2,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": pc.elem_id,
            "properties": {"definition": c.elem_id},
        })
        repo.create_relationship("Association", c.elem_id, d.elem_id)

        extend_block_parts_with_parents(repo, c.elem_id)
        props = repo.elements[c.elem_id].properties["partProperties"]
        self.assertIn("c1", props)
        self.assertIn("b1", props)
        self.assertIn("a1", props)
        self.assertIn("d1", props)

        extend_block_parts_with_parents(repo, b.elem_id)
        props_b = repo.elements[b.elem_id].properties["partProperties"]
        self.assertIn("b1", props_b)
        self.assertIn("a1", props_b)

    def test_inherit_father_parts(self):
        repo = self.repo
        father = repo.create_element("Block", name="Parent", properties={"partProperties": "p1"})
        child = repo.create_element("Block", name="Child")
        pf = repo.create_element("Part", name="P1")
        df = repo.create_diagram("Internal Block Diagram", name="Father")
        repo.link_diagram(father.elem_id, df.diag_id)
        df.objects.append({
            "obj_id": 1,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": pf.elem_id,
            "properties": {"definition": father.elem_id},
        })
        dc = repo.create_diagram("Internal Block Diagram", name="Child")
        repo.link_diagram(child.elem_id, dc.diag_id)
        dc.father = father.elem_id
        added = inherit_father_parts(repo, dc)
        self.assertTrue(any(o.get("element_id") == pf.elem_id for o in dc.objects))
        self.assertTrue(any(o["element_id"] == pf.elem_id for o in added))
        self.assertIn("p1", repo.elements[child.elem_id].properties.get("partProperties", ""))

if __name__ == "__main__":
    unittest.main()
