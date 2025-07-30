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

        class DummyDialog:
            def __init__(self, parent, names, visible, hidden):
                self.result = names

        with patch.object(architecture.SysMLObjectDialog, 'ManagePartsDialog', DummyDialog):
            InternalBlockDiagramWindow.add_contained_parts(win)

        diag = repo.diagrams[ibd.diag_id]
        self.assertEqual(len(diag.objects), 1)
        self.assertFalse(diag.objects[0].get('hidden', False))

    def test_deleted_parts_removed_from_list(self):
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

        self.assertNotIn("B", captured)

if __name__ == '__main__':
    unittest.main()
