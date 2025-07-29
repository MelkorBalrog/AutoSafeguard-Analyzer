import unittest
from gui.architecture import (
    add_composite_aggregation_part,
    remove_aggregation_part,
    set_ibd_father,
    SysMLObject,
    SysMLDiagramWindow,
)
from sysml.sysml_repository import SysMLRepository


class CompositeAggregationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_composite_part_to_ibd(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        self.assertIn("Part", repo.elements[whole.elem_id].properties.get("partProperties", ""))
        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd.objects
            )
        )
        # ensure composite flag is set
        obj = next(o for o in ibd.objects if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id)
        self.assertEqual(obj.get("properties", {}).get("composite"), "true")

    def test_remove_composite_part_from_ibd(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        remove_aggregation_part(repo, whole.elem_id, part.elem_id, remove_object=True)
        self.assertNotIn("Part", repo.elements[whole.elem_id].properties.get("partProperties", ""))
        self.assertFalse(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd.objects
            )
        )

    def test_set_father_links_and_renders_existing_parts(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Composite Aggregation", whole.elem_id, part.elem_id)
        ibd = repo.create_diagram("Internal Block Diagram")
        added = set_ibd_father(repo, ibd, whole.elem_id)
        self.assertEqual(repo.get_linked_diagram(whole.elem_id), ibd.diag_id)
        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd.objects
            )
        )
        # ensure added list includes the new part
        self.assertTrue(any(d.get("properties", {}).get("definition") == part.elem_id for d in added))

    def test_composite_part_created_without_ibd(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        # no IBD linked yet - element should still exist with composite flag
        elem = next(
            e
            for e in repo.elements.values()
            if e.elem_type == "Part"
            and e.properties.get("definition") == part.elem_id
            and e.properties.get("whole") == whole.elem_id
        )
        self.assertEqual(elem.properties.get("composite"), "true")

    def test_cannot_delete_composite_part_object(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        obj_dict = next(o for o in ibd.objects if o.get("obj_type") == "Part")

        class DummyWin:
            def __init__(self):
                self.repo = repo
                self.diagram_id = ibd.diag_id
                self.objects = [SysMLObject(**obj_dict)]
                self.connections = []

            def _sync_to_repository(self):
                diag = self.repo.diagrams.get(self.diagram_id)
                diag.objects = [obj.__dict__ for obj in self.objects]
                diag.connections = []

        win = DummyWin()
        SysMLDiagramWindow.remove_object(win, win.objects[0])
        # object should still be present
        self.assertEqual(len(win.objects), 1)


if __name__ == "__main__":
    unittest.main()
