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
