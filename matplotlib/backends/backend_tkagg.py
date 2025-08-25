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

"""TkAgg backend stub for the minimal Matplotlib substitute.

Only the small subset of functionality exercised by the tests is provided.
The real Matplotlib project offers a rich drawing API; this lightweight
implementation merely supplies the :class:`FigureCanvasTkAgg` class with the
methods used by the GUI metrics tab.
"""

try:  # pragma: no cover - best effort import
    import tkinter as tk
except Exception:  # pragma: no cover - fallback when Tk is unavailable
    tk = None  # type: ignore


class FigureCanvasTkAgg:
    """Very small stand-in for Matplotlib's canvas widget."""

    def __init__(self, figure, master=None):
        self.figure = figure
        if tk and master is not None:
            self._tk_widget = tk.Frame(master)
        else:  # pragma: no cover - Tk not available
            class _Dummy:
                def pack(self, *args, **kwargs):
                    pass

            self._tk_widget = _Dummy()

    def get_tk_widget(self):  # pragma: no cover - trivial
        return self._tk_widget

    def draw_idle(self):  # pragma: no cover - trivial
        pass


__all__ = ["FigureCanvasTkAgg"]

