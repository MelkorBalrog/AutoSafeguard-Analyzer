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
from itertools import product
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
            # Normalize keys so they are always tuples of parent values.
            normalised: Dict[Tuple[bool, ...], float] = {}
            for key, prob in cpd.items():
                # ``key`` may be provided as a single bool, a list of bools or a
                # proper tuple.  Convert everything to a tuple of booleans so that
                # internal lookups are consistent.
                if isinstance(key, tuple):
                    combo = key
                elif isinstance(key, list):
                    combo = tuple(key)
                else:
                    combo = (key,)
                normalised[combo] = float(prob)
            self.cpds[name] = normalised
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
            p_true = float(self.cpds[var].get(key, 0.0))
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

    # ------------------------------------------------------------------
    def marginal_probabilities(self) -> Dict[str, float]:
        r"""Return ``P(node=True)`` for every node.

        This implementation follows the standard marginalisation formula

            P(X=True) = \sum_{pa} P(X=True \mid pa) P(pa)

        by delegating the computation of each term to the enumeration based
        :meth:`joint_probability` helper.  While potentially more expensive
        than simple propagation, it produces correct results even when parent
        nodes are themselves dependent.
        """

        return {node: self.joint_probability({node: True}) for node in self.nodes}

    # ------------------------------------------------------------------
    def _cpd_rows_only(self, var: str) -> List[Tuple[Tuple[bool, ...], float]]:
        """Return combinations of parent values with their ``P(var=True)``.

        This private helper simply enumerates the conditional probability
        table of ``var`` without computing any additional information.  It is
        used as the starting point for :meth:`cpd_rows`.
        """

        parents = self.parents.get(var, [])
        if not parents:
            prob = float(self.cpds.get(var, 0.0))
            return [((), prob)]
        cpds = self.cpds.get(var, {})
        rows: List[Tuple[Tuple[bool, ...], float]] = []
        for combo in product([False, True], repeat=len(parents)):
            rows.append((combo, float(cpds.get(combo, 0.0))))
        return rows

    def cpd_rows(self, var: str) -> List[Tuple[Tuple[bool, ...], float, float, float]]:
        """Return rows of the conditional probability table for ``var``.

        Each returned tuple has four elements:

        ``(parent_values, P(var=True | parents), P(parents), P(all))``

        where ``P(all)`` is the joint probability of the entire row, i.e. the
        probability that the parents take ``parent_values`` *and* ``var`` is
        ``True``.  Missing entries in the conditional probability table default
        to ``0.0`` so that the table is always complete.
        """

        rows = self._cpd_rows_only(var)
        parents = self.parents.get(var, [])
        if not parents:
            combo, prob = rows[0]
            return [(combo, prob, 1.0, prob)]

        result: List[Tuple[Tuple[bool, ...], float, float, float]] = []
        for combo, p_true in rows:
            assignment = {p: v for p, v in zip(parents, combo)}
            combo_prob = self.joint_probability(assignment)
            joint_prob = combo_prob * p_true
            result.append((combo, p_true, combo_prob, joint_prob))
        return result

    # ------------------------------------------------------------------
    def joint_probability(self, assignment: Mapping[str, bool]) -> float:
        r"""Return ``P(assignment)`` for the provided variable/value mapping.

        The computation mirrors the classic factorisation of a Bayesian
        network, ``\prod_i P(X_i \mid Parents(X_i))``, while summing out all
        unspecified variables.  It forms the basis for deriving marginal and
        conditional probabilities used throughout the UI.
        """

        order = self._topological()
        return self._enumerate_all(order, dict(assignment), {})


@dataclass
class CausalBayesianNetworkDoc:
    """Container pairing a named network with node positions for diagrams."""

    name: str
    network: CausalBayesianNetwork = field(default_factory=CausalBayesianNetwork)
    positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    types: Dict[str, str] = field(default_factory=dict)
