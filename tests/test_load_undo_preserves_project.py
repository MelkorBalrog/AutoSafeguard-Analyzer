import unittest
import tempfile
from pathlib import Path
from sysml.sysml_repository import SysMLRepository

class LoadUndoPreservesProjectTests(unittest.TestCase):
    def _create_project(self, path: Path):
        repo = SysMLRepository.get_instance()
        blk = repo.create_element("Block", name="A")
        repo.save(path)
        return blk.elem_id

    def test_undo_after_load_keeps_elements(self):
        for strat in ("v1", "v2", "v3", "v4"):
            with self.subTest(strategy=strat):
                SysMLRepository.reset_instance()
                repo = SysMLRepository.get_instance()
                with tempfile.TemporaryDirectory() as td:
                    file = Path(td)/"model.json"
                    elem_id = self._create_project(file)
                    SysMLRepository.reset_instance()
                    repo = SysMLRepository.get_instance()
                    repo.load(str(file), strategy=strat)
                    self.assertIn(elem_id, repo.elements)
                    repo.undo()
                    self.assertIn(elem_id, repo.elements)

if __name__ == '__main__':
    unittest.main()
