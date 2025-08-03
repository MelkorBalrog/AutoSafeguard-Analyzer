"""Minimal color definitions for the ReportLab stub.

The real :mod:`reportlab.lib.colors` module exposes a fairly extensive
collection of color objects.  The application only needs a tiny subset of
these names when constructing table styles for PDF export.  To keep the
lightweight ReportLab replacement functional, we provide a minimal
``Color`` type and a handful of commonly used named colors.

The numerical values are RGB triples expressed in the range ``0-1`` to
mirror ReportLab's behaviour.  They are not interpreted anywhere in the
tests, but storing something sensible makes debugging easier and keeps the
API reasonably faithful.
"""

from __future__ import annotations

from typing import Tuple


class Color(tuple):
    """Simple immutable RGB color representation.

    ReportLab represents colours as small objects with ``red``, ``green`` and
    ``blue`` attributes.  For the purposes of the tests we only need the values
    to be carried around, so a bare tuple subclass is sufficient.
    """

    def __new__(cls, red: float, green: float, blue: float) -> "Color":
        return super().__new__(cls, (red, green, blue))

    # Expose ``red``, ``green`` and ``blue`` attributes for compatibility.
    @property
    def red(self) -> float:
        return self[0]

    @property
    def green(self) -> float:
        return self[1]

    @property
    def blue(self) -> float:
        return self[2]


# A small palette of named colours required by the application
black = Color(0, 0, 0)
white = Color(1, 1, 1)
grey = Color(0.5, 0.5, 0.5)
lightgrey = Color(0.83, 0.83, 0.83)
lightblue = Color(0.68, 0.85, 0.90)
orange = Color(1, 0.65, 0)


__all__ = [
    "Color",
    "black",
    "white",
    "grey",
    "lightgrey",
    "lightblue",
    "orange",
]

