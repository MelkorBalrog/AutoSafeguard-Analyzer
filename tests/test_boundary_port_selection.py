import unittest
from gui.architecture import SysMLDiagramWindow, SysMLObject, set_ibd_father
from sysml.sysml_repository import SysMLRepository

class BoundaryPortSelectionTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_find_object_prefers_port_over_boundary(self):
        repo = self.repo
        block = repo.create_element("Block", name="B", properties={"ports": "p"})
        diag = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, diag, block.elem_id)
        win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
        win.repo = repo
        win.diagram_id = diag.diag_id
        win.objects = [SysMLObject(**o) for o in diag.objects]
        win.zoom = 1.0
        port_obj = next(o for o in win.objects if o.obj_type == "Port")
        obj = win.find_object(port_obj.x, port_obj.y, prefer_port=True)
        self.assertEqual(obj.obj_type, "Port")

if __name__ == '__main__':
    unittest.main()
