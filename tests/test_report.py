import unittest
from services.report import (
    get_month_report,
    get_saldo_summary,
    get_today_report,
    get_week_report,
)
from services.sheets import sheets_service


class TestReportService(unittest.TestCase):

    def setUp(self):
        # Reset mock sheets service state and cache
        from utils.cache import cache
        cache.clear()
        sheets_service.is_mock_mode = True
        sheets_service._mock_data.clear()

        # Add sample data
        sheets_service.append_transaction(
            txn_type="income", category="Salary", amount=5000000, note="gaji juli"
        )
        sheets_service.append_transaction(
            txn_type="expense", category="Food", amount=25000, note="makan siang"
        )
        sheets_service.append_transaction(
            txn_type="expense", category="Transport", amount=15000, note="gojek"
        )

    def test_saldo_summary(self):
        summary = get_saldo_summary()
        self.assertEqual(summary["balance"], 4960000)
        self.assertEqual(summary["month_income"], 5000000)
        self.assertEqual(summary["month_expense"], 40000)

    def test_today_report(self):
        report = get_today_report()
        self.assertEqual(report["income"], 5000000)
        self.assertEqual(report["expense"], 40000)
        self.assertEqual(report["total_count"], 3)
        self.assertEqual(len(report["transactions"]), 3)

    def test_week_report(self):
        report = get_week_report()
        self.assertEqual(report["income"], 5000000)
        self.assertEqual(report["expense"], 40000)
        self.assertEqual(report["net"], 4960000)
        self.assertTrue(len(report["top_categories"]) >= 2)

    def test_month_report(self):
        report = get_month_report()
        self.assertEqual(report["income"], 5000000)
        self.assertEqual(report["expense"], 40000)
        self.assertEqual(report["net"], 4960000)
        self.assertEqual(report["total_count"], 3)


if __name__ == "__main__":
    unittest.main()
