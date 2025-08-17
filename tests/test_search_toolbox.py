import unittest
from unittest.mock import patch
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui import search_toolbox, messagebox


class DummyVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


class DummyListbox:
    def delete(self, *_args):
        pass

    def insert(self, *_args):
        pass


class DummyApp:
    def get_all_nodes_in_model(self):
        return []

    def get_all_fmea_entries(self):
        return []


class SearchToolboxTests(unittest.TestCase):
    def test_notifies_on_no_results(self):
        tb = search_toolbox.SearchToolbox.__new__(search_toolbox.SearchToolbox)
        tb.app = DummyApp()
        tb.search_var = DummyVar("missing")
        tb.case_var = DummyVar(False)
        tb.regex_var = DummyVar(False)
        tb.results_box = DummyListbox()
        tb.results = []
        tb.current_index = -1

        infos = []
        with patch.object(messagebox, "showinfo", lambda *a: infos.append(a)):
            tb._run_search()
        self.assertTrue(infos, "User was not notified when no results found")
        self.assertIn("No matches found", infos[0][1])


if __name__ == "__main__":
    unittest.main()
