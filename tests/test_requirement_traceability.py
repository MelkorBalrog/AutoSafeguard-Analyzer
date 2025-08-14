import unittest

from sysml.sysml_repository import SysMLRepository
from gui.architecture import SysMLObject
from gui.toolboxes import find_requirement_traces
from analysis.models import global_requirements


class RequirementTraceabilityTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        global_requirements.clear()
        self.repo = SysMLRepository.get_instance()

    def test_find_requirement_traces_returns_diagram_objects(self):
        global_requirements["R1"] = {"id": "R1", "text": "Req1"}
        elem = self.repo.create_element("Block", name="B1")
        diag = self.repo.create_diagram("Block Definition Diagram", name="BD")
        self.repo.add_element_to_diagram(diag.diag_id, elem.elem_id)
        obj = SysMLObject(
            1,
            "Block",
            0,
            0,
            element_id=elem.elem_id,
            properties={"name": "B1"},
            requirements=[global_requirements["R1"]],
        )
        diag.objects.append(obj.__dict__)
        traces = find_requirement_traces("R1")
        self.assertIn("BD:B1", traces)


if __name__ == "__main__":
    unittest.main()

