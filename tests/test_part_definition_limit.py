import unittest
from unittest.mock import patch
from gui import architecture
from gui.architecture import SysMLObject
from sysml.sysml_repository import SysMLRepository

class DummyWin:
    def __init__(self, diagram):
        self.repo = SysMLRepository.get_instance()
        self.diagram_id = diagram.diag_id
        self.objects = []
        self.connections = []
        self.app = None
    def redraw(self):
        pass
    def _sync_to_repository(self):
        diag = self.repo.diagrams[self.diagram_id]
        diag.objects = [o.__dict__ for o in self.objects]

class PartDefinitionLimitTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_limit_prevents_definition_change(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Composite Aggregation", a.elem_id, b.elem_id, properties={"multiplicity": "1"})
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id, "1")
        win = DummyWin(ibd)
        for o in ibd.objects:
            win.objects.append(SysMLObject(**o))
        new_elem = repo.create_element("Part", name="P")
        repo.add_element_to_diagram(ibd.diag_id, new_elem.elem_id)
        new_obj = SysMLObject(99, "Part", 0, 0, element_id=new_elem.elem_id, properties={})
        ibd.objects.append(new_obj.__dict__)
        win.objects.append(new_obj)
        with patch.object(architecture.messagebox, "showinfo") as info:
            exceeded = architecture._multiplicity_limit_exceeded(
                repo,
                a.elem_id,
                b.elem_id,
                win.objects,
                new_obj.element_id,
            )
            if exceeded:
                architecture.messagebox.showinfo(
                    "Add Part",
                    "Maximum number of parts of that type has been reached",
                )
            else:
                new_obj.properties["definition"] = b.elem_id
            self.assertTrue(info.called)
        self.assertNotEqual(new_obj.properties.get("definition"), b.elem_id)

if __name__ == "__main__":
    unittest.main()
