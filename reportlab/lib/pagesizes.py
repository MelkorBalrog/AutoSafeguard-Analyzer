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

"""Minimal page size definitions used by the simplified ReportLab stub.

The real ReportLab library defines page sizes in points (1 point = 1/72 inch).
For our purposes we only need support for the US Letter size and the ability
to swap dimensions for landscape orientation.  These helpers provide reasonable
defaults so that PDF generation code can calculate available drawing areas.
"""

# Width and height of a US Letter page in points (8.5" x 11")
letter = (612.0, 792.0)


def landscape(pagesize):
    """Return the dimensions for a landscape oriented page.

    The real ReportLab `landscape` function simply swaps the width and height of
    the supplied page size.  Doing the same here keeps our stub compatible with
    code that expects this behaviour.
    """

    width, height = pagesize
    return height, width

