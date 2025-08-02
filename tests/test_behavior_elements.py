import unittest
from gui.architecture import (
    get_block_behavior_elements,
    BehaviorAssignment,
    behaviors_to_json,
)
from sysml.sysml_repository import SysMLRepository


class BehaviorElementsTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_behavior_element_filtering(self):
        repo = self.repo
        block = repo.create_element("Block", name="B")
        action = repo.create_element("Action", name="Act1")
        op_elem = repo.create_element("Operation", name="Op1")
        diag = repo.create_diagram("Activity Diagram", name="Diag1")
        diag.objects.append(
            {
                "obj_id": 1,
                "obj_type": "Action",
                "x": 0,
                "y": 0,
                "element_id": action.elem_id,
                "properties": {"name": "Act1"},
            }
        )
        block.properties["behaviors"] = behaviors_to_json(
            [BehaviorAssignment("Op1", diag.diag_id)]
        )
        repo.elements[block.elem_id] = block
        elems = get_block_behavior_elements(repo, block.elem_id)
        ids = [e.elem_id for e in elems]
        self.assertIn(action.elem_id, ids)
        self.assertIn(op_elem.elem_id, ids)

        other = repo.create_element("Action", name="Other")
        diag2 = repo.create_diagram("Activity Diagram", name="OtherDiag")
        diag2.objects.append(
            {
                "obj_id": 2,
                "obj_type": "Action",
                "x": 0,
                "y": 0,
                "element_id": other.elem_id,
                "properties": {"name": "Other"},
            }
        )
        ids = [e.elem_id for e in get_block_behavior_elements(repo, block.elem_id)]
        self.assertNotIn(other.elem_id, ids)


if __name__ == "__main__":
    unittest.main()

