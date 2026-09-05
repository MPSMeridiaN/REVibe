import unittest
from ledger import total


class TotalTests(unittest.TestCase):
    def test_positive_amounts(self):
        self.assertEqual(6, total([1, 2, 3]))
