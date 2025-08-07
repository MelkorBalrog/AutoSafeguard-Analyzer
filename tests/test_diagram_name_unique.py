import unittest
from sysml.sysml_repository import SysMLRepository


class DiagramNameUniqueTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_names_include_type_when_conflict(self):
        repo = self.repo
        bdd = repo.create_diagram("Block Definition Diagram", name="Main")
        ibd = repo.create_diagram("Internal Block Diagram", name="Main")
        self.assertIn(bdd.diag_type, bdd.name)
        self.assertIn(ibd.diag_type, ibd.name)
        self.assertNotEqual(bdd.name, ibd.name)


if __name__ == "__main__":
    unittest.main()
