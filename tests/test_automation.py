import unittest
import pandas as pd
from services.sheets import sheets_service
from utils.cache import cache


class TestAutomationAndExport(unittest.TestCase):

    def setUp(self):
        cache.clear()
        sheets_service.is_mock_mode = True
        sheets_service._mock_data.clear()

        sheets_service.append_transaction(
            txn_type="income", category="Salary", amount=5000000, note="gaji"
        )
        sheets_service.append_transaction(
            txn_type="expense", category="Food", amount=25000, note="makan"
        )

    def test_csv_export_generation(self):
        transactions = sheets_service.get_all_transactions()
        self.assertEqual(len(transactions), 2)

        df = pd.DataFrame(transactions)
        self.assertIn("amount", df.columns)
        self.assertIn("category", df.columns)
        self.assertEqual(len(df), 2)


if __name__ == "__main__":
    unittest.main()
