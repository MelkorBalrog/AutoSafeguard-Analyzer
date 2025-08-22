import types

from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow


def test_fill_tag_strategies_unique_and_ordered():
    win = object.__new__(CausalBayesianNetworkWindow)
    win.canvas = types.SimpleNamespace()
    tags = [
        win._fill_tag_strategy1("A", 0),
        win._fill_tag_strategy2("A", 0),
        win._fill_tag_strategy3("A", 0),
        win._fill_tag_strategy4("A", 0),
    ]
    assert len(set(tags)) == 4
    assert win._generate_fill_tag("A", 0) == tags[0]
