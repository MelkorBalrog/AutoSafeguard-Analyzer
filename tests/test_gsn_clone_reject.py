import pytest
from gsn.nodes import GSNNode


def test_clone_rejects_unsupported_types():
    strategy = GSNNode("S", "Strategy")
    with pytest.raises(ValueError):
        strategy.clone()
    module = GSNNode("M", "Module")
    with pytest.raises(ValueError):
        module.clone()
