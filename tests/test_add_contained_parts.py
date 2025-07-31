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
            if diag.diag_type == "Internal Block Diagram":
                block_id = (
                    getattr(diag, "father", None)
                    or next(
                        (
                            eid
                            for eid, did in self.repo.element_diagrams.items()
                            if did == self.diagram_id
                        ),
                        None,
                    )
                )
                if block_id:
                    architecture._enforce_ibd_multiplicity(self.repo, block_id)

    def redraw(self):
        pass

class AddContainedPartsRenderTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_new_parts_become_visible(self):
        repo = self.repo
        block = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(block.elem_id, ibd.diag_id)
        win = DummyWindow(ibd)

        captured_visible = []

        class DummyDialog:
            def __init__(self, parent, names, visible, hidden):
                captured_visible.extend(visible)
                self.result = names

        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', DummyDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)

        diag = repo.diagrams[ibd.diag_id]
        self.assertEqual(len(diag.objects), 1)
        self.assertFalse(diag.objects[0].get('hidden', False))
        self.assertNotIn("B", captured_visible)

    def test_new_parts_render_with_app(self):
        repo = self.repo
        block = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(block.elem_id, ibd.diag_id)
        win = DummyWindow(ibd)

        class DummyApp:
            def __init__(self, win):
                self.ibd_windows = [win]

            def update_views(self):
                pass

        win.app = DummyApp(win)

        class DummyDialog:
            def __init__(self, parent, names, visible, hidden):
                self.result = names

        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', DummyDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)

        # Only one part should exist and it must be visible
        self.assertEqual(len(win.objects), 1)
        self.assertFalse(win.objects[0].hidden)

    def test_deleted_parts_remain_listed(self):
        repo = self.repo
        block = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(block.elem_id, ibd.diag_id)
        win = DummyWindow(ibd)

        class AddDialog:
            def __init__(self, parent, names, visible, hidden):
                self.result = ["B"]

        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', AddDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)

        # remove the part from the diagram
        obj = win.objects[0]
        InternalBlockDiagramWindow.remove_object(win, obj)

        captured = []

        class CaptureDialog:
            def __init__(self, parent, names, visible, hidden):
                captured.extend(names)
                self.result = []

        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', CaptureDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)

        self.assertIn("B", captured)

    def test_unhide_existing_part(self):
        repo = self.repo
        block = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(block.elem_id, ibd.diag_id)
        added = architecture._sync_ibd_partproperty_parts(repo, block.elem_id)
        win = DummyWindow(ibd)
        for obj_dict in ibd.objects:
            win.objects.append(SysMLObject(**obj_dict))
        class DummyDialog:
            def __init__(self, parent, names, visible, hidden):
                self.result = ["B"]
        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', DummyDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)
        self.assertFalse(win.objects[0].hidden)

    def test_unhide_part_with_app(self):
        repo = self.repo
        block = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(block.elem_id, ibd.diag_id)
        architecture._sync_ibd_partproperty_parts(repo, block.elem_id)
        win = DummyWindow(ibd)
        class DummyApp:
            def __init__(self, win):
                self.ibd_windows = [win]
            def update_views(self):
                pass
        win.app = DummyApp(win)
        for obj_dict in ibd.objects:
            win.objects.append(SysMLObject(**obj_dict))
        class DummyDialog:
            def __init__(self, parent, names, visible, hidden):
                self.result = ["B"]
        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', DummyDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)
        self.assertFalse(win.objects[0].hidden)

    def test_multiplicity_limit_enforced(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship(
            "Composite Aggregation",
            whole.elem_id,
            part.elem_id,
            properties={"multiplicity": "2"},
        )
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        win = DummyWindow(ibd)
        architecture._sync_ibd_composite_parts(repo, whole.elem_id)
        for obj in ibd.objects:
            win.objects.append(SysMLObject(**obj))

        class DummyDialog:
            def __init__(self, parent, names, visible, hidden):
                self.result = ["Part"]

        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', DummyDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)

        parts = [
            o
            for o in repo.diagrams[ibd.diag_id].objects
            if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(parts), 2)
        names = {repo.elements[o["element_id"]].name for o in parts}
        self.assertIn("Part[1]", names)
        self.assertIn("Part[2]", names)

    def test_rename_part_does_not_duplicate(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship(
            "Composite Aggregation",
            whole.elem_id,
            part.elem_id,
            properties={"multiplicity": "2"},
        )
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        architecture.add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "2")
        obj = next(o for o in ibd.objects if o.get("obj_type") == "Part")
        repo.elements[obj["element_id"]].name = "Renamed"
        architecture.update_block_parts_from_ibd(repo, ibd)
        architecture._sync_block_parts_from_ibd(repo, ibd.diag_id)
        props = repo.elements[whole.elem_id].properties.get("partProperties", "")
        self.assertEqual(props, "Part[2]")

    def test_rename_part_helper_updates_properties(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship(
            "Composite Aggregation",
            whole.elem_id,
            part.elem_id,
            properties={"multiplicity": "2"},
        )
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        architecture.add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "2")
        obj = next(o for o in ibd.objects if o.get("obj_type") == "Part")
        architecture.rename_part(repo, obj["element_id"], "New")
        props = repo.elements[whole.elem_id].properties.get("partProperties", "")
        self.assertEqual(props, "Part[2]")

    def test_definition_change_enforces_multiplicity(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship(
            "Composite Aggregation",
            whole.elem_id,
            part.elem_id,
            properties={"multiplicity": "2"},
        )
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        win = DummyWindow(ibd)
        elem = repo.create_element("Part", name="P")
        repo.add_element_to_diagram(ibd.diag_id, elem.elem_id)
        obj = SysMLObject(1, "Part", 0, 0, element_id=elem.elem_id, properties={})
        ibd.objects.append(obj.__dict__)
        win.objects.append(obj)
        obj.properties["definition"] = part.elem_id
        repo.elements[elem.elem_id].properties["definition"] = part.elem_id
        win._sync_to_repository()
        parts = [
            o
            for o in repo.diagrams[ibd.diag_id].objects
            if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(parts), 2)
        names = {repo.elements[o["element_id"]].name for o in parts}
        self.assertIn("Part[1]", names)
        self.assertIn("Part[2]", names)

if __name__ == '__main__':
    unittest.main()
