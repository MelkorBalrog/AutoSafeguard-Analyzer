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

import types
from AutoML import AutoMLApp


def test_enable_stpa_without_pillow():
    app = AutoMLApp.__new__(AutoMLApp)
    app.tool_listboxes = {}
    app.tool_actions = {}
    app.tool_categories = {}
    app.work_product_menus = {}
    app.enabled_work_products = set()
    app.update_views = lambda: None
    app.enable_process_area = lambda area: None
    app.manage_architecture = lambda: None
    app.show_requirements_editor = lambda: None
    AutoMLApp.enable_work_product(app, "STPA")
    assert "STPA" in app.enabled_work_products
