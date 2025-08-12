"""Utilities for acceptance criteria and validation targets per ISO 21448.

This module provides helper functions to derive the rate of hazardous behaviour
(RHB) and the associated validation time from an acceptance criterion as
specified in ISO 21448:2022, Annex C. The formulas implemented here correspond
to equations (C.1) and (C.2) and assume rates are expressed per hour.
"""

from __future__ import annotations

import math


def hazardous_behavior_rate(
    acceptance_rate: float,
    p_exposure_given_hb: float,
    p_uncontrollable_given_exposure: float,
    p_severity_given_uncontrollable: float,
) -> float:
    """Derive the rate of hazardous behaviour.

    All rates are expressed in **events per hour**. The function implements
    ISO 21448 Formula (C.2)::

        RHB = AH / (P_E|HB * P_C|E * P_S|C)

    Parameters
    ----------
    acceptance_rate:
        The acceptance criterion :math:`A_H` (e.g. ``1e-8`` events per hour).
    p_exposure_given_hb:
        Probability :math:`P_{E|HB}` that the hazardous behaviour occurs in a
        scenario leading to harm.
    p_uncontrollable_given_exposure:
        Probability :math:`P_{C|E}` that the hazardous behaviour cannot be
        controlled once exposed.
    p_severity_given_uncontrollable:
        Probability :math:`P_{S|C}` that the resulting harm reaches the
        considered severity.

    Returns
    -------
    float
        Rate of hazardous behaviour :math:`R_{HB}` in events per hour.

    Examples
    --------
    >>> hazardous_behavior_rate(1e-8, 0.05, 0.1, 0.01)
    0.0002
    """

    denominator = (
        p_exposure_given_hb * p_uncontrollable_given_exposure * p_severity_given_uncontrollable
    )
    if denominator <= 0:
        raise ValueError("Probabilities must be > 0")
    return acceptance_rate / denominator


def acceptance_rate(
    hazardous_behavior_rate: float,
    p_exposure_given_hb: float,
    p_uncontrollable_given_exposure: float,
    p_severity_given_uncontrollable: float,
) -> float:
    """Compute the acceptance rate from the hazardous behaviour rate.

    All rates are expressed in **events per hour**. Implements ISO 21448
    Formula (C.1)::

        AH = RHB * P_E|HB * P_C|E * P_S|C

    Parameters
    ----------
    hazardous_behavior_rate:
        Rate of hazardous behaviour :math:`R_{HB}` in events per hour.

    Returns
    -------
    float
        Acceptance criterion :math:`A_H` in events per hour.

    Examples
    --------
    >>> acceptance_rate(0.0002, 0.05, 0.1, 0.01)
    1e-08
    """

    return (
        hazardous_behavior_rate
        * p_exposure_given_hb
        * p_uncontrollable_given_exposure
        * p_severity_given_uncontrollable
    )


def validation_time(hazardous_behavior_rate: float, confidence: float) -> float:
    """Calculate required test time to demonstrate the acceptance criterion.

    Assumes no hazardous behaviour occurs during testing and uses a Poisson
    distribution to derive the required duration. The formula is::

        T = -ln(1 - C) / RHB

    where ``C`` is the desired confidence level (e.g. ``0.63`` for 63 %).
    """

    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if hazardous_behavior_rate <= 0:
        raise ValueError("hazardous_behavior_rate must be > 0")
    return -math.log(1 - confidence) / hazardous_behavior_rate
