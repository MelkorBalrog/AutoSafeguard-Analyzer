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
from analysis.utils import append_unique_insensitive

class MalfunctionUtilsTests(unittest.TestCase):
    def test_append_unique_insensitive(self):
        items = ['Brake Failure', 'Sensor Fault']
        append_unique_insensitive(items, 'brake failure')
        self.assertEqual(len(items), 2)
        append_unique_insensitive(items, '  SENSOR FAULT  ')
        self.assertEqual(len(items), 2)
        append_unique_insensitive(items, 'Power Loss')
        self.assertEqual(items[-1], 'Power Loss')
        self.assertEqual(len(items), 3)

if __name__ == '__main__':
    unittest.main()
