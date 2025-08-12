# Author: Miguel Marina <karel.capek.robotics@gmail.com>
"""Utility helpers for analysis package."""

from typing import List


# Mapping tables from risk assessment ratings to probabilities.
#
# The values provide a simple heuristic for converting ISO 26262 / ISO 21448
# levels into conditional probabilities used in the validation target
# calculation. They can be refined as better field data becomes available.
EXPOSURE_PROBABILITIES = {1: 1e-4, 2: 1e-3, 3: 1e-2, 4: 5e-2}
CONTROLLABILITY_PROBABILITIES = {1: 1e-3, 2: 1e-2, 3: 1e-1}
SEVERITY_PROBABILITIES = {1: 1e-3, 2: 1e-2, 3: 1e-1}


def exposure_to_probability(level: int) -> float:
    """Return ``P(E|HB)`` for the given exposure rating."""
    return EXPOSURE_PROBABILITIES.get(int(level), 1.0)


def controllability_to_probability(level: int) -> float:
    """Return ``P(C|E)`` for the given controllability rating."""
    return CONTROLLABILITY_PROBABILITIES.get(int(level), 1.0)


def severity_to_probability(level: int) -> float:
    """Return ``P(S|C)`` for the given severity rating."""
    return SEVERITY_PROBABILITIES.get(int(level), 1.0)


def append_unique_insensitive(items: List[str], name: str) -> None:
    """Append ``name`` to ``items`` if not already present (case-insensitive)."""
    if not name:
        return
    name = name.strip()
    if not name:
        return
    lower = name.lower()
    for existing in items:
        if existing.lower() == lower:
            return
    items.append(name)


def derive_validation_target(acceptance_rate: float,
                             exposure_given_hb: float,
                             uncontrollable_given_exposure: float,
                             severity_given_uncontrollable: float) -> float:
    """Derive a validation target from an acceptance criterion.

    This implements the ISO 21448 relationship for the rate of hazardous
    behaviour :math:`R_{HB}`. All rates are expressed in **events per hour**.

    The acceptance criterion :math:`A_H` is decomposed into conditional
    probabilities for exposure (``exposure_given_hb``), lack of
    controllability (``uncontrollable_given_exposure``) and severity
    (``severity_given_uncontrollable``). The resulting validation target is
    calculated using:

    ``R_HB = A_H / (P_E|HB * P_C|E * P_S|C)``

    For example, ``A_H = 1e-8/h`` with ``P_E|HB = 0.05``, ``P_C|E = 0.1``
    and ``P_S|C = 0.01`` yields ``R_HB = 2e-4/h``.

    Parameters
    ----------
    acceptance_rate:
        Acceptance criterion for the harm :math:`A_H` in events per hour.
    exposure_given_hb:
        Conditional probability of being exposed to the scenario given the
        hazardous behaviour, :math:`P_{E|HB}`.
    uncontrollable_given_exposure:
        Probability that the hazardous behaviour is not controllable once
        exposure occurs, :math:`P_{C|E}`.
    severity_given_uncontrollable:
        Probability of the relevant severity assuming the control action
        fails, :math:`P_{S|C}`.

    Returns
    -------
    float
        The acceptable rate of the hazardous behaviour ``R_HB`` (events per
        hour) that can be used as a validation target.

    Raises
    ------
    ValueError
        If any of the probability terms is less than or equal to zero.
    """

    denominator = (
        exposure_given_hb *
        uncontrollable_given_exposure *
        severity_given_uncontrollable
    )

    if denominator <= 0:
        raise ValueError(
            "Probability factors must be positive to derive a validation target"
        )

    return acceptance_rate / denominator
