import unittest
from types import SimpleNamespace
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gui.architecture import SysMLDiagramWindow, SysMLObject, set_ibd_father
from sysml.sysml_repository import SysMLRepository

class DummyCanvas:
    def canvasx(self, val):
        return val
    def canvasy(self, val):
        return val
    def configure(self, **kw):
        pass

class BoundaryPortButtonTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_port_to_boundary_via_button(self):
        repo = self.repo
        block = repo.create_element("Block", name="B")
        diag = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, diag, block.elem_id)
        boundary = next(o for o in diag.objects if o.get("obj_type") == "Block Boundary")

        win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
        win.repo = repo
        win.diagram_id = diag.diag_id
        win.objects = [SysMLObject(**o) for o in diag.objects]
        win.connections = []
        win.zoom = 1.0
        win.current_tool = "Port"
        win.canvas = DummyCanvas()
        win.sort_objects = SysMLDiagramWindow.sort_objects.__get__(win)
        win.find_object = SysMLDiagramWindow.find_object.__get__(win)
        win.snap_port_to_parent = SysMLDiagramWindow.snap_port_to_parent.__get__(win)
        win.ensure_text_fits = SysMLDiagramWindow.ensure_text_fits.__get__(win)
        def sync():
            d = repo.diagrams[win.diagram_id]
            d.objects = [obj.__dict__ for obj in win.objects]
            d.connections = [conn.__dict__ for conn in win.connections]
        win._sync_to_repository = sync
        win.redraw = lambda: None
        win.update_property_view = lambda: None

        evt_x = boundary["x"] + boundary["width"] / 2
        evt_y = boundary["y"]
        win.on_left_press(SimpleNamespace(x=evt_x, y=evt_y, state=0))

        diag = repo.diagrams[diag.diag_id]
        ports = [
            o for o in diag.objects
            if o.get("obj_type") == "Port" and o.get("properties", {}).get("parent") == str(boundary["obj_id"])
        ]
        self.assertEqual(len(ports), 1)
        self.assertIn(ports[0]["properties"]["name"], repo.elements[block.elem_id].properties.get("ports", ""))

if __name__ == "__main__":
    unittest.main()
