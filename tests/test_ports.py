# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
from gui.architecture import (
    SysMLObject,
    remove_orphan_ports,
    update_ports_for_part,
    SysMLDiagramWindow,
    rename_port,
    set_ibd_father,
)
from sysml.sysml_repository import SysMLRepository, SysMLDiagram

class PortParentTests(unittest.TestCase):
    def test_remove_orphan_ports(self):
        part = SysMLObject(1, "Part", 0, 0)
        good_port = SysMLObject(2, "Port", 0, 0, properties={"parent": "1"})
        orphan_port = SysMLObject(3, "Port", 0, 0)
        bad_port = SysMLObject(4, "Port", 0, 0, properties={"parent": "99"})
        objs = [part, good_port, orphan_port, bad_port]
        remove_orphan_ports(objs)
        self.assertIn(part, objs)
        self.assertIn(good_port, objs)
        self.assertNotIn(orphan_port, objs)
        self.assertNotIn(bad_port, objs)

    def test_ports_follow_part_resize(self):
        part = SysMLObject(1, "Part", 0, 0, width=80, height=40)
        port = SysMLObject(
            2,
            "Port",
            part.x + part.width / 2,
            0,
            properties={"parent": "1"},
        )
        objs = [part, port]
        update_ports_for_part(part, objs)
        self.assertEqual(port.properties.get("side"), "E")
        part.width = 100
        update_ports_for_part(part, objs)
        self.assertEqual(port.x, part.x + part.width / 2)


class DirectionValidationTests(unittest.TestCase):
    class DummyWindow:
        def __init__(self):
            self.repo = SysMLRepository.get_instance()
            diag = SysMLDiagram(diag_id="d", diag_type="Internal Block Diagram")
            self.repo.diagrams[diag.diag_id] = diag
            self.diagram_id = diag.diag_id

    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_incompatible_directions(self):
        win = self.DummyWindow()
        src = SysMLObject(1, "Port", 0, 0, properties={"direction": "out"})
        dst = SysMLObject(2, "Port", 0, 0, properties={"direction": "in"})
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Connector")
        self.assertFalse(valid)


class PortUpdateTests(unittest.TestCase):
    class DummyCanvas:
        def delete(self, *args, **kwargs):
            pass

        def configure(self, **kw):
            pass

    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def _create_window_with_port(self):
        repo = self.repo
        block = repo.create_element("Block", name="B", properties={"ports": "p"})
        diag = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, diag, block.elem_id)
        win = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
        win.repo = repo
        win.diagram_id = diag.diag_id
        win.objects = [SysMLObject(**o) for o in diag.objects]
        win.connections = []
        win.zoom = 1.0
        win.canvas = self.DummyCanvas()
        win.sort_objects = SysMLDiagramWindow.sort_objects.__get__(win)
        win.sync_ports = SysMLDiagramWindow.sync_ports.__get__(win)
        win.sync_boundary_ports = SysMLDiagramWindow.sync_boundary_ports.__get__(win)
        def sync():
            d = repo.diagrams[win.diagram_id]
            d.objects = [obj.__dict__ for obj in win.objects]
        win._sync_to_repository = sync
        win.redraw = SysMLDiagramWindow.redraw.__get__(win)
        win.update_property_view = lambda: None
        return win, block.elem_id

    def test_rename_port_updates_parent(self):
        win, block_id = self._create_window_with_port()
        port = next(o for o in win.objects if o.obj_type == "Port")
        rename_port(win.repo, port, win.objects, "q")
        win._sync_to_repository()
        boundary = next(o for o in win.objects if o.obj_type == "Block Boundary")
        self.assertIn("q", boundary.properties.get("ports"))
        self.assertNotIn("p", boundary.properties.get("ports"))
        self.assertIn("q", win.repo.elements[block_id].properties.get("ports"))

    def test_delete_port_updates_parent(self):
        win, block_id = self._create_window_with_port()
        port = next(o for o in win.objects if o.obj_type == "Port")
        win.remove_object(port)
        win._sync_to_repository()
        boundary = next(o for o in win.objects if o.obj_type == "Block Boundary")
        self.assertNotIn("p", boundary.properties.get("ports", ""))
        self.assertNotIn("p", win.repo.elements[block_id].properties.get("ports", ""))


if __name__ == '__main__':
    unittest.main()
