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
from AutoML import AutoMLApp


class ValidateFloatTests(unittest.TestCase):
    def test_allows_scientific_notation(self):
        self.assertTrue(AutoMLApp.validate_float(None, "1e"))
        self.assertTrue(AutoMLApp.validate_float(None, "1e-"))
        self.assertTrue(AutoMLApp.validate_float(None, "1e-8"))


if __name__ == "__main__":
    unittest.main()
