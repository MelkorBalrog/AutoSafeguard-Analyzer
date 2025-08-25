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

import os
import sys
import tkinter as tk

import pytest

# Ensure repository root in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui import logger  # noqa: E402
from gui.controls import messagebox  # noqa: E402
from AutoML import AutoMLApp  # noqa: E402


def test_log_window_uses_default_height_for_messages():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    logger.init_log_window(root)
    long_message = "This is a long message " * 50
    short_message = "short"
    default_height = logger._default_height
    messagebox.showinfo("Title", long_message)
    root.update_idletasks()
    assert logger.log_frame.winfo_height() == default_height
    messagebox.showinfo("Title", short_message)
    root.update_idletasks()
    assert logger.log_frame.winfo_height() == default_height
    root.destroy()


def test_log_window_default_height_with_pinned_explorer():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    app = AutoMLApp(root)
    app.toggle_explorer_pin()
    default_height = logger._default_height
    messagebox.showinfo("Title", "Pinned panel message" * 40)
    root.update_idletasks()
    assert logger.log_frame.winfo_height() == default_height
    root.destroy()

