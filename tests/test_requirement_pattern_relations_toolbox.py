import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import _all_connection_tools, REQ_PATTERN_RELATIONS


def test_requirement_patterns_relations_present():
    tools = set(_all_connection_tools())
    missing = [r for r in REQ_PATTERN_RELATIONS if r not in tools]
    assert not missing, f"Missing relations: {missing}"
