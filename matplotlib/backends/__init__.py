"""Minimal ``matplotlib.backends`` package for testing.

This stub package provides only the pieces required by the project.  It is
*not* a full-featured backend implementation.  Only the TkAgg canvas is
implemented to allow the metrics tab to create a drawing surface when the
real Matplotlib library is unavailable.
"""

from .backend_tkagg import FigureCanvasTkAgg  # noqa: F401

__all__ = ["FigureCanvasTkAgg"]

