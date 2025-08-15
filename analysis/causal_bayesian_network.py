"""Simple Causal Bayesian Network utilities.

This module provides a minimal implementation of a causal Bayesian
network for binary variables.  Networks are specified by their directed
acyclic graph structure together with prior and conditional probability
values.  The implementation supports classic probability queries as well
as ``do``-style interventions.

Example
-------
>>> cbn = CausalBayesianNetwork()
>>> cbn.add_node('Rain', cpd=0.3)
>>> cbn.add_node('WetGround', parents=['Rain'],
...               cpd={(True,): 0.9, (False,): 0.1})
>>> cbn.add_node('SlipperyRoad', parents=['WetGround'],
...               cpd={(True,): 0.8, (False,): 0.05})
>>> round(cbn.query('SlipperyRoad'), 3)
0.305
>>> round(cbn.query('SlipperyRoad', evidence={'Rain': True}), 3)
0.725

The small network above mirrors the example discussed in the project
README and illustrates how priors, conditional probability tables and
queries map to the "circles and tables" intuition.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Tuple


@dataclass
class CausalBayesianNetwork:
    """Represent a causal Bayesian network with binary variables."""

    nodes: List[str] = field(default_factory=list)
    parents: Dict[str, List[str]] = field(default_factory=dict)
    cpds: Dict[str, object] = field(default_factory=dict)

    def add_node(
        self,
        name: str,
        *,
        parents: Iterable[str] | None = None,
        cpd: Mapping[Tuple[bool, ...], float] | float,
    ) -> None:
        """Add ``name`` with optional ``parents`` and probability ``cpd``.

        For root nodes (without parents) ``cpd`` is the prior probability
        of the node being ``True``.  Otherwise ``cpd`` must be a mapping
        from tuples of parent values to the probability of ``True``.
        """

        if name in self.nodes:
            raise ValueError(f"node '{name}' already exists")
        self.nodes.append(name)
        self.parents[name] = list(parents or [])
        if self.parents[name]:
            if not isinstance(cpd, Mapping):
                raise TypeError("cpd must be a mapping for non-root nodes")
            self.cpds[name] = dict(cpd)
        else:
            self.cpds[name] = float(cpd)

    # ------------------------------------------------------------------
    def query(
        self,
        var: str,
        evidence: Mapping[str, bool] | None = None,
    ) -> float:
        """Return ``P(var=True | evidence)`` using enumeration."""

        return self._query(var, evidence=evidence or {}, interventions={})

    # ------------------------------------------------------------------
    def intervention(
        self,
        var: str,
        interventions: Mapping[str, bool],
        evidence: Mapping[str, bool] | None = None,
    ) -> float:
        """Return ``P(var=True | do(interventions), evidence)``."""

        return self._query(var, evidence=evidence or {}, interventions=interventions)

    # ------------------------------------------------------------------
    # Internal helpers
    def _query(
        self,
        var: str,
        *,
        evidence: Mapping[str, bool],
        interventions: Mapping[str, bool],
    ) -> float:
        vars_order = self._topological()
        dist: Dict[bool, float] = {}
        for value in (False, True):
            extended = dict(evidence)
            extended[var] = value
            dist[value] = self._enumerate_all(vars_order, extended, interventions)
        total = dist[False] + dist[True]
        return dist[True] / total if total else 0.0

    def _enumerate_all(
        self,
        vars_order: List[str],
        evidence: Dict[str, bool],
        interventions: Mapping[str, bool],
    ) -> float:
        if not vars_order:
            return 1.0
        Y = vars_order[0]
        rest = vars_order[1:]
        if Y in evidence:
            prob = self._probability(Y, evidence[Y], evidence, interventions)
            return prob * self._enumerate_all(rest, evidence, interventions)
        else:
            total = 0.0
            evidence[Y] = True
            prob_true = self._probability(Y, True, evidence, interventions)
            total += prob_true * self._enumerate_all(rest, evidence, interventions)
            evidence[Y] = False
            prob_false = self._probability(Y, False, evidence, interventions)
            total += prob_false * self._enumerate_all(rest, evidence, interventions)
            del evidence[Y]
            return total

    def _probability(
        self,
        var: str,
        value: bool,
        evidence: Mapping[str, bool],
        interventions: Mapping[str, bool],
    ) -> float:
        if var in interventions:
            return 1.0 if value == interventions[var] else 0.0
        parents = self.parents.get(var, [])
        if not parents:
            p_true = float(self.cpds[var])
        else:
            key = tuple(evidence[p] for p in parents)
            p_true = float(self.cpds[var][key])
        return p_true if value else 1.0 - p_true

    # ------------------------------------------------------------------
    def _topological(self) -> List[str]:
        """Return nodes in topological order."""

        order: List[str] = []
        temp_mark: set = set()
        perm_mark: set = set()

        def visit(node: str) -> None:
            if node in perm_mark:
                return
            if node in temp_mark:
                raise ValueError("graph has cycles")
            temp_mark.add(node)
            for parent in self.parents.get(node, []):
                visit(parent)
            perm_mark.add(node)
            order.append(node)

        for node in self.nodes:
            visit(node)
        return order


@dataclass
class CausalBayesianNetworkDoc:
    """Container pairing a named network with node positions for diagrams."""

    name: str
    network: CausalBayesianNetwork = field(default_factory=CausalBayesianNetwork)
    positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)