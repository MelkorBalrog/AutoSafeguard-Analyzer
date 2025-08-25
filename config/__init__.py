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

from .config_loader import (
    load_json_with_comments,
    load_diagram_rules,
    validate_diagram_rules,
    load_requirement_patterns,
    validate_requirement_patterns,
    load_report_template,
    validate_report_template,
)

__all__ = [
    "load_json_with_comments",
    "load_diagram_rules",
    "validate_diagram_rules",
    "load_requirement_patterns",
    "validate_requirement_patterns",
    "load_report_template",
    "validate_report_template",
]
