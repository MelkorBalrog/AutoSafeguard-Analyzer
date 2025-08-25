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

from __future__ import annotations

"""Utility functions for GUI dialogs."""

from tkinter import simpledialog


def askstring_fixed(sd_module: simpledialog.__class__, title: str, prompt: str, **kwargs):
    """Display an ``askstring`` dialog with a fixed-size window.

    This helper temporarily patches the dialog class used by
    :func:`tkinter.simpledialog.askstring` so the resulting window cannot be
    resized.  The *sd_module* parameter should be the ``simpledialog`` module
    used by the caller so that test patches on that module remain effective.
    """
    original = sd_module._QueryString

    class FixedQueryString(sd_module._QueryString):  # type: ignore[attr-defined]
        """Query dialog variant that disables window resizing."""

        def body(self, master):  # type: ignore[override]
            self.resizable(False, False)
            return super().body(master)

    sd_module._QueryString = FixedQueryString  # type: ignore[attr-defined]
    try:
        return sd_module.askstring(title, prompt, **kwargs)
    finally:
        sd_module._QueryString = original  # type: ignore[attr-defined]
