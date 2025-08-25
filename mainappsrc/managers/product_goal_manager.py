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

"""Utilities for managing shared product goals across events."""

from __future__ import annotations

from typing import Dict, Iterable, List


class ProductGoalManager:
    """Manage grouping of events by malfunction and shared goals."""

    def update_shared_product_goals(
        self,
        events: Iterable[object],
        shared_goals: Dict[str, Dict[str, str]],
    ) -> Dict[str, Dict[str, str]]:
        """Group events by malfunction and ensure shared goal names.

        Parameters
        ----------
        events:
            Collection of event-like objects that may define ``malfunction``
            attributes. Each event is mutated in-place when part of a shared
            goal group.
        shared_goals:
            Mapping from malfunction identifiers to shared goal dictionaries.

        Returns
        -------
        dict
            Updated shared goal mapping.
        """

        groups: Dict[str, List[object]] = {}
        for event in events:
            malfunction = getattr(event, "malfunction", "")
            if malfunction:
                groups.setdefault(malfunction, []).append(event)

        for malfunction, group in groups.items():
            if len(group) > 1:
                goal = shared_goals.get(malfunction)
                if not goal:
                    goal = {"name": group[0].user_name}
                    shared_goals[malfunction] = goal
                for evt in group:
                    evt.user_name = goal["name"]
                    evt.name_readonly = True
                    evt.product_goal = goal
            else:
                shared_goals.pop(malfunction, None)
                evt = group[0]
                evt.name_readonly = False
                evt.product_goal = None

        return shared_goals


__all__ = ["ProductGoalManager"]
