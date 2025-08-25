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

import tkinter as tk
from unittest.mock import MagicMock

import pytest

from AutoML import AutoMLApp


def test_confirm_close_quits_and_destroys():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter GUI not available")
    root.withdraw()
    quit_spy = MagicMock(wraps=root.quit)
    destroy_spy = MagicMock(wraps=root.destroy)
    root.quit = quit_spy
    root.destroy = destroy_spy

    app = AutoMLApp.__new__(AutoMLApp)
    app.root = root
    app.has_unsaved_changes = lambda: False
    app._loaded_model_paths = []

    app.confirm_close()

    assert quit_spy.called
    assert destroy_spy.called
