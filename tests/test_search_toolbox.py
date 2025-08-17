import sys
import types
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.search_toolbox import search_repository
from sysml.sysml_repository import SysMLRepository


def test_search_repository_matches_names_and_descriptions():
    repo = SysMLRepository.reset_instance()
    e1 = repo.create_element("Block", name="Controller", properties={"description": "controls things"})
    e2 = repo.create_element("Block", name="sensor", properties={"description": "temperature sensor"})
    d1 = repo.create_diagram("UseCase", name="Main", description="main scenario")

    res = search_repository(repo, "controller")
    assert ("element", e1.elem_id, e1.display_name()) in res

    res = search_repository(repo, "scenario")
    assert ("diagram", d1.diag_id, d1.display_name()) in res

    res = search_repository(repo, "Sensor", case_sensitive=True)
    assert ("element", e2.elem_id, e2.display_name()) not in res

    res = search_repository(repo, "sens[oa]r", use_regex=True)
    assert ("element", e2.elem_id, e2.display_name()) in res
