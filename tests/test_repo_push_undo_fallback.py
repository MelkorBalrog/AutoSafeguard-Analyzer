import pytest
from sysml.sysml_repository import SysMLRepository


def test_push_undo_state_falls_back_when_strategy_missing():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()
    base_len = len(repo._undo_stack)

    original = SysMLRepository._push_undo_state_v4
    del SysMLRepository._push_undo_state_v4
    try:
        repo.push_undo_state("v4")
        assert len(repo._undo_stack) == base_len + 1
    finally:
        SysMLRepository._push_undo_state_v4 = original
