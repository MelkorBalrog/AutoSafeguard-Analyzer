# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Minimal styling utilities for report generation tests.

This module provides a very small subset of the real ReportLab styling API
that is sufficient for the unit tests in this repository.  The previous
implementation returned an empty dictionary which resulted in ``KeyError``
exceptions whenever a style such as ``"Title"`` or ``"Heading1"`` was
requested.  The real ReportLab library ships with a sample style sheet that
contains a number of basic styles; here we emulate only the pieces that are
required by :mod:`AutoML` when building PDF reports.

The goal of this module is not to be feature complete, but rather to provide
just enough behaviour so that code relying on ``getSampleStyleSheet`` can run
without raising exceptions.
"""


class StyleSheet(dict):
    """Dictionary-like container for paragraph styles."""

    def add(self, style):
        """Store *style* in the sheet using its name as the key."""
        self[style.name] = style


def getSampleStyleSheet():
    """Return a very small sample style sheet.

    The sheet mimics the real ReportLab ``getSampleStyleSheet`` function by
    providing a handful of commonly used styles (``Normal``, ``Title``,
    ``Heading1``–``Heading3``).  Additional styles can be added by client code
    via :meth:`StyleSheet.add`.
    """

    sheet = StyleSheet()

    normal = ParagraphStyle(name="Normal", fontName="Helvetica", fontSize=12, leading=14)
    sheet.add(normal)
    sheet.add(ParagraphStyle(name="Title", parent=normal, fontSize=24, leading=28))
    sheet.add(ParagraphStyle(name="Heading1", parent=normal, fontSize=18, leading=22))
    sheet.add(ParagraphStyle(name="Heading2", parent=normal, fontSize=14, leading=18))
    sheet.add(ParagraphStyle(name="Heading3", parent=normal, fontSize=12, leading=16))

    return sheet


class ParagraphStyle:
    """Minimal stand-in for ReportLab's :class:`ParagraphStyle`.

    The class simply stores the attributes that are used throughout the tests
    (``name``, ``parent``, ``fontName``, ``fontSize``, ``leading`` and
    ``alignment``).  No validation or advanced behaviour is provided.
    """

    def __init__(
        self,
        name,
        parent=None,
        fontName="Helvetica",
        fontSize=12,
        leading=None,
        alignment=0,
        **kwargs,
    ):
        self.name = name
        self.parent = parent
        self.fontName = fontName
        self.fontSize = fontSize
        self.leading = leading if leading is not None else fontSize * 1.2
        self.alignment = alignment

        # Store any additional keyword arguments for completeness.
        for key, value in kwargs.items():
            setattr(self, key, value)

