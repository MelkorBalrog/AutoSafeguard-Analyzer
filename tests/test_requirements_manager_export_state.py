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

import ast
from pathlib import Path


def test_requirements_manager_defines_export_state():
    code = Path("mainappsrc/managers/requirements_manager.py").read_text()
    tree = ast.parse(code)
    class_node = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RequirementsManagerSubApp"
    )
    assert any(
        isinstance(node, ast.FunctionDef) and node.name == "export_state" for node in class_node.body
    ), "RequirementsManagerSubApp.export_state missing"
