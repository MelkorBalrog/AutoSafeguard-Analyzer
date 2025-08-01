# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
from sysml.sysml_repository import SysMLRepository
from gui.architecture import (
    extend_block_parts_with_parents,
    inherit_father_parts,
    inherit_block_properties,
    remove_inherited_block_properties,
    _sync_ibd_partproperty_parts,
    _sync_ibd_aggregation_parts,
    _sync_ibd_composite_parts,
)

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
        da.objects.append(
            {
                "obj_id": 1,
                "obj_type": "Part",
                "x": 0,
                "y": 0,
                "element_id": pb.elem_id,
                "properties": {"definition": b.elem_id},
            }
        )
        pc = repo.create_element("Part", name="PC")
        db.objects.append(
            {
                "obj_id": 2,
                "obj_type": "Part",
                "x": 0,
                "y": 0,
                "element_id": pc.elem_id,
                "properties": {"definition": c.elem_id},
            }
        )
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
        df.objects.append(
            {
                "obj_id": 1,
                "obj_type": "Part",
                "x": 0,
                "y": 0,
                "element_id": pf.elem_id,
                "properties": {"definition": father.elem_id},
            }
        )
        dc = repo.create_diagram("Internal Block Diagram", name="Child")
        repo.link_diagram(child.elem_id, dc.diag_id)
        dc.father = father.elem_id
        added = inherit_father_parts(repo, dc)
        self.assertTrue(any(o.get("element_id") == pf.elem_id for o in dc.objects))
        self.assertTrue(any(o["element_id"] == pf.elem_id for o in added))
        self.assertIn("p1", repo.elements[child.elem_id].properties.get("partProperties", ""))

    def test_inherit_father_parts_copies_ports(self):
        repo = self.repo
        father = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        p1 = repo.create_element("Part", name="P1")
        p2 = repo.create_element("Part", name="P2")
        df = repo.create_diagram("Internal Block Diagram", name="Father")
        repo.link_diagram(father.elem_id, df.diag_id)
        df.objects.extend(
            [
                {
                    "obj_id": 1,
                    "obj_type": "Part",
                    "x": 0,
                    "y": 0,
                    "element_id": p1.elem_id,
                    "properties": {"definition": father.elem_id, "ports": "a"},
                },
                {
                    "obj_id": 2,
                    "obj_type": "Port",
                    "x": 10,
                    "y": 0,
                    "properties": {"parent": "1", "name": "a", "direction": "in"},
                },
                {
                    "obj_id": 3,
                    "obj_type": "Part",
                    "x": 40,
                    "y": 0,
                    "element_id": p2.elem_id,
                    "properties": {"definition": father.elem_id, "ports": "b"},
                },
                {
                    "obj_id": 4,
                    "obj_type": "Port",
                    "x": 50,
                    "y": 0,
                    "properties": {"parent": "3", "name": "b", "direction": "out"},
                },
            ]
        )
        dc = repo.create_diagram("Internal Block Diagram", name="Child")
        repo.link_diagram(child.elem_id, dc.diag_id)
        dc.father = father.elem_id
        added = inherit_father_parts(repo, dc)
        ports = [o for o in dc.objects if o.get("obj_type") == "Port"]
        self.assertEqual(len(ports), 2)
        dir_map = {p["properties"]["name"]: p["properties"].get("direction") for p in ports}
        self.assertEqual(dir_map["a"], "in")
        self.assertEqual(dir_map["b"], "out")
        port_added = [o for o in added if o.get("obj_type") == "Port"]
        self.assertEqual(len(port_added), 2)

    def test_inherit_father_parts_skips_existing(self):
        repo = self.repo
        father = repo.create_element("Block", name="Parent", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        child = repo.create_element("Block", name="Child")
        df = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(father.elem_id, df.diag_id)
        p_f = repo.create_element("Part", name="B[1]", properties={"definition": part_blk.elem_id})
        df.objects.append({
            "obj_id": 1,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": p_f.elem_id,
            "properties": {"definition": part_blk.elem_id},
        })
        dc = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, dc.diag_id)
        dc.father = father.elem_id
        p_c = repo.create_element("Part", name="B", properties={"definition": part_blk.elem_id})
        repo.add_element_to_diagram(dc.diag_id, p_c.elem_id)
        dc.objects.append({
            "obj_id": 2,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": p_c.elem_id,
            "properties": {"definition": part_blk.elem_id},
        })
        added = inherit_father_parts(repo, dc)
        parts = [o for o in dc.objects if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part_blk.elem_id]
        self.assertEqual(len(parts), 1)
        self.assertFalse(any(o.get("obj_type") == "Part" for o in added))
        
    def test_generalization_inherits_properties(self):
        repo = self.repo
        parent = repo.create_element(
            "Block",
            name="Parent",
            properties={"partProperties": "p1"},
        )
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        inherit_block_properties(repo, child.elem_id)
        props = repo.elements[child.elem_id].properties
        self.assertIn("p1", props.get("partProperties", ""))

    def test_remove_generalization_clears_properties(self):
        repo = self.repo
        parent = repo.create_element(
            "Block",
            name="Parent",
            properties={"partProperties": "p1"},
        )
        child = repo.create_element("Block", name="Child")
        rel = repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        inherit_block_properties(repo, child.elem_id)
        remove_inherited_block_properties(repo, child.elem_id, parent.elem_id)
        repo.relationships.remove(rel)
        inherit_block_properties(repo, child.elem_id)
        props = repo.elements[child.elem_id].properties
        self.assertNotIn("p1", props.get("partProperties", ""))

    def test_reroute_generalization_updates_properties(self):
        repo = self.repo
        parent1 = repo.create_element(
            "Block",
            name="Parent1",
            properties={"partProperties": "p1"},
        )
        parent2 = repo.create_element(
            "Block",
            name="Parent2",
            properties={"partProperties": "p2"},
        )
        child = repo.create_element("Block", name="Child")
        rel = repo.create_relationship("Generalization", child.elem_id, parent1.elem_id)
        inherit_block_properties(repo, child.elem_id)
        remove_inherited_block_properties(repo, child.elem_id, parent1.elem_id)
        rel.target = parent2.elem_id
        inherit_block_properties(repo, child.elem_id)
        props = repo.elements[child.elem_id].properties
        self.assertIn("p2", props.get("partProperties", ""))
        self.assertNotIn("p1", props.get("partProperties", ""))

    def test_sync_partproperty_parts(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        added = _sync_ibd_partproperty_parts(repo, blk.elem_id)
        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part_blk.elem_id
                for o in ibd.objects
            )
        )
        self.assertTrue(
            any(d.get("properties", {}).get("definition") == part_blk.elem_id for d in added)
        )

    def test_sync_partproperty_parts_with_multiplicity(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B[1..2]"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        added = _sync_ibd_partproperty_parts(repo, blk.elem_id, names=["B[1..2]"])
        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part_blk.elem_id
                for o in ibd.objects
            )
        )
        self.assertTrue(
            any(d.get("properties", {}).get("definition") == part_blk.elem_id for d in added)
        )


    def test_sync_aggregation_parts_with_parent(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        repo.create_relationship("Aggregation", parent.elem_id, part.elem_id)
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, ibd.diag_id)
        added = _sync_ibd_aggregation_parts(repo, child.elem_id)
        self.assertTrue(
            any(o.get("properties", {}).get("definition") == part.elem_id for o in ibd.objects)
        )
        self.assertTrue(any(d.get("properties", {}).get("definition") == part.elem_id for d in added))

    def test_sync_composite_parts_with_parent(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        repo.create_relationship("Composite Aggregation", parent.elem_id, part.elem_id)
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, ibd.diag_id)
        added = _sync_ibd_composite_parts(repo, child.elem_id)
        self.assertTrue(
            any(o.get("properties", {}).get("definition") == part.elem_id for o in ibd.objects)
        )
        self.assertTrue(any(d.get("properties", {}).get("definition") == part.elem_id for d in added))

    def test_partproperty_names_with_brackets(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B[2]"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        added = _sync_ibd_partproperty_parts(repo, blk.elem_id, names=["B[2]"])
        self.assertTrue(
            any(
                o.get("obj_type") == "Part"
                and repo.elements[o.get("element_id")].name.startswith("B")
                and o.get("properties", {}).get("definition") == part_blk.elem_id
                for o in ibd.objects
            )
        )

    def test_partproperty_name_with_colon(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "p:B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        added = _sync_ibd_partproperty_parts(repo, blk.elem_id)
        self.assertTrue(
            any(
                o.get("obj_type") == "Part"
                and repo.elements[o.get("element_id")].name == "p"
                and o.get("properties", {}).get("definition") == part_blk.elem_id
                for o in ibd.objects
            )
        )

if __name__ == "__main__":
    unittest.main()
