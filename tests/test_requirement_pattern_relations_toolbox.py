import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import _all_connection_tools, REQ_PATTERN_RELATIONS, _toolbox_defs


def test_requirement_patterns_relations_present():
    tools = set(_all_connection_tools())
    missing = [r for r in REQ_PATTERN_RELATIONS if r not in tools]
    assert not missing, f"Missing relations: {missing}"


def test_assesses_relation_visible_in_toolbox_defs():
    defs = _toolbox_defs()
    found = [g for g, d in defs.items() if "Assesses" in d["relations"]]
    assert found, "Assesses relation missing from toolbox groups"
