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

# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
from gui.architecture import (
    parse_operations,
    operations_to_json,
    OperationDefinition,
    OperationParameter,
    format_operation,
)

class OperationParseTests(unittest.TestCase):
    def test_parse_json(self):
        raw = '[{"name": "op", "parameters": [{"name": "a", "type": "int"}], "return_type": "bool"}]'
        ops = parse_operations(raw)
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].name, "op")
        self.assertEqual(ops[0].parameters[0].name, "a")
        self.assertEqual(ops[0].parameters[0].type, "int")
        self.assertEqual(ops[0].return_type, "bool")

    def test_parse_comma(self):
        ops = parse_operations('foo, bar')
        self.assertEqual(len(ops), 2)
        self.assertEqual(ops[0].name, 'foo')

    def test_json_round_trip(self):
        op = OperationDefinition('f', [OperationParameter('x', 'int')], 'int')
        js = operations_to_json([op])
        parsed = parse_operations(js)
        self.assertEqual(format_operation(parsed[0]), 'f(x: int) : int')

if __name__ == '__main__':
    unittest.main()
