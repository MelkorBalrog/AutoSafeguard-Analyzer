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

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import AutoMLApp


def test_log_toggle_button_visible_with_pinned_explorer():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    app = AutoMLApp(root)
    # Pin the explorer pane which previously caused the toggle button to be hidden
    app.toggle_explorer_pin()
    app.toggle_logs()  # show logs
    root.update_idletasks()
    button_bottom = app.toggle_log_button.winfo_y() + app.toggle_log_button.winfo_height()
    assert button_bottom <= root.winfo_height()
    root.destroy()
