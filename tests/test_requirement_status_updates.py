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

"""Tests for requirement status synchronization."""

from types import SimpleNamespace

import pytest

from AutoML import AutoMLApp
from mainappsrc.managers.requirements_manager import RequirementsManagerSubApp
from analysis.models import global_requirements


class DummyReviewManager:
    def get_requirements_for_review(self, review):
        return getattr(review, "req_ids", set())


def _setup_app(reviews):
    app = AutoMLApp.__new__(AutoMLApp)
    app.reviews = reviews
    app.review_manager = DummyReviewManager()
    app.review_is_closed_for = lambda r: getattr(r, "closed", False)
    app.requirements_manager = RequirementsManagerSubApp(app)
    return app


@pytest.mark.parametrize(
    "reviews,expected",
    [
        ([], "draft"),
        ([SimpleNamespace(mode="peer", reviewed=False, req_ids={"R1"})], "in review"),
        ([SimpleNamespace(mode="peer", reviewed=True, req_ids={"R1"})], "peer reviewed"),
        ([SimpleNamespace(mode="joint", approved=False, req_ids={"R1"})], "pending approval"),
        ([SimpleNamespace(mode="joint", approved=True, closed=True, req_ids={"R1"})], "approved"),
    ],
)
def test_update_requirement_statuses(reviews, expected):
    global_requirements.clear()
    global_requirements["R1"] = {"id": "R1", "status": "draft"}
    app = _setup_app(reviews)
    app.update_requirement_statuses()
    assert global_requirements["R1"]["status"] == expected
