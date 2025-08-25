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

"""Governance rules for Safety & Security Case visibility of GSN diagrams."""
from dataclasses import dataclass

@dataclass
class RelationshipStatus:
    """Status of relationships between GSN argumentation and Safety & Security Case.

    A diagram is visible only when all relationships are satisfied.
    """
    used_by: bool = False
    used_after_review: bool = False
    used_after_approval: bool = False


def can_view_gsn_argumentation(rel: RelationshipStatus) -> bool:
    """Return True if the Safety & Security Case may view GSN diagrams.

    The rule requires the GSN argumentation to be used by the case and
    to have passed both review and approval.
    """
    return rel.used_by and rel.used_after_review and rel.used_after_approval
