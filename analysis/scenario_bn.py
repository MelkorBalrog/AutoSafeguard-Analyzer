"""Utilities to derive Bayesian Network diagrams from Scenario Libraries."""
from __future__ import annotations

import re
from typing import Dict, Tuple

from analysis.causal_bayesian_network import CausalBayesianNetwork, CausalBayesianNetworkDoc


def build_bn_from_scenario(scenario: dict) -> CausalBayesianNetworkDoc:
    """Return a Bayesian network diagram for *scenario*.

    The implementation interprets ``[[element]]`` markers within the scenario
    description as ODD element references.  A chain-structured causal Bayesian
    network is constructed where the scenario name acts as the root node and
    each referenced element depends on the previous item in textual order.
    """
    desc = scenario.get("description", "")
    elements = re.findall(r"\[\[(.+?)\]\]", desc)

    net = CausalBayesianNetwork()
    root_name = scenario.get("name", "Scenario")
    net.add_node(root_name, cpd=0.5)
    positions: Dict[str, Tuple[int, int]] = {root_name: (0, 100)}
    types = {root_name: "Variable"}

    prev = root_name
    for i, name in enumerate(elements, start=1):
        if name in net.nodes:
            continue
        net.add_node(name, parents=[prev], cpd={(True,): 0.5, (False,): 0.5})
        positions[name] = (i * 120, 100)
        types[name] = "Variable"
        prev = name

    name = f"{root_name} CBN"
    return CausalBayesianNetworkDoc(name, network=net, positions=positions, types=types)
