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

    def test_repeated_name_does_not_duplicate(self):
        repo = self.repo
        repo.create_diagram("Block Definition Diagram", name="Main")
        repo.create_diagram("Internal Block Diagram", name="Main")
        third = repo.create_diagram("Internal Block Diagram", name="Main")
        fourth = repo.create_diagram("Block Definition Diagram", name="Main")
        names = [d.name for d in repo.diagrams.values()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(third.name, "Main Internal Block Diagram_1")
        self.assertEqual(fourth.name, "Main Block Definition Diagram_1")


if __name__ == "__main__":
    unittest.main()
