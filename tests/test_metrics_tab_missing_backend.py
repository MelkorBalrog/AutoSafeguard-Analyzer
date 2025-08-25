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

import unittest
import tkinter as tk
from unittest import mock
from AutoML import AutoMLApp


class MetricsTabWithoutMatplotlibTests(unittest.TestCase):
    def test_open_metrics_tab_without_matplotlib(self):
        try:
            root = tk.Tk()
            root.withdraw()
        except tk.TclError:
            self.skipTest("Tk not available")
        app = AutoMLApp(root)
        app.open_metrics_tab()
        tabs = [app.doc_nb.tab(tid, "text") for tid in app.doc_nb.tabs()]
        self.assertIn("Metrics", tabs)
        root.destroy()


if __name__ == "__main__":
    unittest.main()
