import unittest
from services.budget import (
    check_budget_warning,
    get_budget_status,
    make_progress_bar,
    set_category_budget,
)
from services.charts import (
    generate_bar_chart,
    generate_cashflow_chart,
    generate_pie_chart,
)
from services.sheets import sheets_service
from utils.cache import cache


class TestChartAndBudgetService(unittest.TestCase):

    def setUp(self):
        cache.clear()
        sheets_service.is_mock_mode = True
        sheets_service.force_mock_mode = True
        sheets_service._mock_data.clear()

        # Add sample data
        sheets_service.append_transaction(
            txn_type="income", category="Salary", amount=5000000, note="gaji"
        )
        sheets_service.append_transaction(
            txn_type="expense", category="Food", amount=500000, note="makan"
        )
        sheets_service.append_transaction(
            txn_type="expense", category="Transport", amount=200000, note="bensin"
        )

    def test_progress_bar_formatter(self):
        bar = make_progress_bar(50.0)
        self.assertIn("50%", bar)
        self.assertIn("█████░░░░░", bar)

    def test_budget_status_calculation(self):
        set_category_budget("Food", 1000000)
        statuses = get_budget_status()
        food_status = next(s for s in statuses if s["category"] == "Food")

        self.assertEqual(food_status["limit"], 1000000)
        self.assertEqual(food_status["usage"], 500000)
        self.assertEqual(food_status["pct"], 50.0)
        self.assertEqual(food_status["status"], "ok")

    def test_budget_warning_threshold(self):
        set_category_budget("Food", 500000)
        # Adding 400000 to existing 500000 exceeds 100%
        warning = check_budget_warning("Food", 400000)
        self.assertIsNotNone(warning)
        self.assertIn("BUDGET TERLAMPAUI", warning)

    def test_charts_generation_buffers(self):
        pie_buf = generate_pie_chart()
        self.assertIsNotNone(pie_buf)
        self.assertTrue(len(pie_buf.getvalue()) > 1000)

        bar_buf = generate_bar_chart()
        self.assertIsNotNone(bar_buf)
        self.assertTrue(len(bar_buf.getvalue()) > 1000)

        cashflow_buf = generate_cashflow_chart()
        self.assertIsNotNone(cashflow_buf)
        self.assertTrue(len(cashflow_buf.getvalue()) > 1000)


if __name__ == "__main__":
    unittest.main()
