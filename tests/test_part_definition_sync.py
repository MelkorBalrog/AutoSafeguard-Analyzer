import unittest
from gui.architecture import rename_block
from sysml.sysml_repository import SysMLRepository

class PartDefinitionSyncTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_rename_block_updates_name_based_definition(self):
        repo = self.repo
        blk = repo.create_element("Block", name="B")
        part = repo.create_element("Part", name="B", properties={"definition": "B"})
        rename_block(repo, blk.elem_id, "B2")
        self.assertEqual(part.name, "B2")
        self.assertEqual(part.properties["definition"], blk.elem_id)

    def test_from_dict_converts_definition_names(self):
        repo = self.repo
        blk = repo.create_element("Block", name="B")
        part = repo.create_element("Part", name="B", properties={"definition": "B"})
        data = repo.to_dict()
        SysMLRepository._instance = None
        repo2 = SysMLRepository.get_instance()
        repo2.from_dict(data)
        p2 = repo2.elements[part.elem_id]
        self.assertEqual(p2.properties["definition"], blk.elem_id)

