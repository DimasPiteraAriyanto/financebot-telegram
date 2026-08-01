import unittest
from services.parser import parse_transaction_input
from utils.formatter import format_currency, parse_amount


class TestParserAndFormatter(unittest.TestCase):

    def test_amount_parsing(self):
        self.assertEqual(parse_amount("25000"), 25000)
        self.assertEqual(parse_amount("25k"), 25000)
        self.assertEqual(parse_amount("25rb"), 25000)
        self.assertEqual(parse_amount("5jt"), 5000000)
        self.assertEqual(parse_amount("5m"), 5000000)
        self.assertEqual(parse_amount("2.5jt"), 2500000)
        self.assertEqual(parse_amount("25.000"), 25000)

    def test_currency_formatter(self):
        self.assertEqual(format_currency(25000), "Rp25.000")
        self.assertEqual(format_currency(5000000), "Rp5.000.000")
        self.assertEqual(format_currency(-15000), "-Rp15.000")

    def test_standard_expense_parsing(self):
        result = parse_transaction_input("-25000 makan siang")
        self.assertIsNotNone(result)
        self.assertEqual(result.type, "expense")
        self.assertEqual(result.amount, 25000)
        self.assertEqual(result.note, "makan siang")
        self.assertIn(result.category, ["Jajan", "Kebutuhan"])
        self.assertFalse(result.is_smart_detected)

    def test_shortcut_expense_parsing(self):
        result = parse_transaction_input("-15k bensin kantor")
        self.assertIsNotNone(result)
        self.assertEqual(result.type, "expense")
        self.assertEqual(result.amount, 15000)
        self.assertEqual(result.note, "bensin kantor")
        self.assertEqual(result.category, "Bensin")

    def test_income_parsing(self):
        result = parse_transaction_input("+5jt gaji juli")
        self.assertIsNotNone(result)
        self.assertEqual(result.type, "income")
        self.assertEqual(result.amount, 5000000)
        self.assertEqual(result.note, "gaji juli")
        self.assertEqual(result.category, "Gaji")

    def test_smart_detection_parsing(self):
        result = parse_transaction_input("bakso 25000")
        self.assertIsNotNone(result)
        self.assertEqual(result.type, "unknown")
        self.assertEqual(result.amount, 25000)
        self.assertEqual(result.note, "bakso")
        self.assertEqual(result.category, "Jajan")
        self.assertTrue(result.is_smart_detected)

    def test_invalid_input(self):
        self.assertIsNone(parse_transaction_input("hello world"))
        self.assertIsNone(parse_transaction_input(""))


if __name__ == "__main__":
    unittest.main()
