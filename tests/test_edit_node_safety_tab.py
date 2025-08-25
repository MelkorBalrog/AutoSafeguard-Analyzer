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

"""Tests for safety tab population in EditNodeDialog."""

import types
import tkinter as tk

from gui.dialogs.edit_node_dialog import EditNodeDialog
from mainappsrc.models.fta.fault_tree_node import FaultTreeNode


def test_safety_tab_not_empty_for_intermediate_event():
    root = tk.Tk()
    root.withdraw()
    try:
        node = FaultTreeNode("Test", "INTERMEDIATE EVENT")
        app = types.SimpleNamespace(malfunctions=[], safety_mgmt_toolbox=None)
        dlg = EditNodeDialog.__new__(EditNodeDialog)
        dlg.node = node
        dlg.app = app
        dlg.body(root)
        assert dlg.safety_frame.winfo_children()
    finally:
        root.destroy()
