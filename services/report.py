from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
import pytz

import config
from constants.categories import get_category_info
from services.sheets import sheets_service
from utils.formatter import get_current_datetime


def _parse_date(date_str: str) -> Optional[date]:
    """Safely parse YYYY-MM-DD string to date object."""
    try:
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None



def get_saldo_summary() -> Dict[str, Any]:
    """Get current total balance and current month cashflow summary."""
    now = get_current_datetime()
    current_month_str = now.strftime("%Y-%m")

    transactions = sheets_service.get_all_transactions()
    balance = sheets_service.get_current_balance()

    month_income = 0.0
    month_expense = 0.0
    last_date_str = "-"

    for txn in transactions:
        d = _parse_date(txn.get("date", ""))
        if d:
            last_date_str = d.strftime("%d %b %Y")
            if d.strftime("%Y-%m") == current_month_str:
                amt = float(txn.get("amount", 0.0))
                if txn.get("type") == "income":
                    month_income += amt
                elif txn.get("type") == "expense":
                    month_expense += amt

    return {
        "balance": balance,
        "month_income": month_income,
        "month_expense": month_expense,
        "last_date": last_date_str,
    }


def get_today_report() -> Dict[str, Any]:
    """Get summary and transaction list for today."""
    now = get_current_datetime()
    today_date = now.date()

    transactions = sheets_service.get_all_transactions()

    today_income = 0.0
    today_expense = 0.0
    today_txns = []

    for txn in transactions:
        d = _parse_date(txn.get("date", ""))
        if d and d == today_date:
            amt = float(txn.get("amount", 0.0))
            txn_type = txn.get("type", "expense")
            if txn_type == "income":
                today_income += amt
            else:
                today_expense += amt

            cat_info = get_category_info(txn.get("category", ""))
            today_txns.append({
                "type": txn_type,
                "category": txn.get("category", ""),
                "emoji": cat_info["emoji"],
                "amount": amt,
                "note": txn.get("note", ""),
                "time": txn.get("time", ""),
            })

    return {
        "date_formatted": now.strftime("%d %b %Y"),
        "income": today_income,
        "expense": today_expense,
        "transactions": today_txns,
        "total_count": len(today_txns),
    }


def get_week_report() -> Dict[str, Any]:
    """Get summary for the last 7 days vs previous 7 days."""
    now = get_current_datetime()
    today = now.date()
    start_this_week = today - timedelta(days=6)
    start_last_week = today - timedelta(days=13)
    end_last_week = today - timedelta(days=7)

    transactions = sheets_service.get_all_transactions()

    this_week_income = 0.0
    this_week_expense = 0.0
    last_week_expense = 0.0

    category_expenses: Dict[str, float] = {}

    for txn in transactions:
        d = _parse_date(txn.get("date", ""))
        if not d:
            continue

        amt = float(txn.get("amount", 0.0))
        txn_type = txn.get("type", "expense")

        # This week (last 7 days)
        if start_this_week <= d <= today:
            if txn_type == "income":
                this_week_income += amt
            elif txn_type == "expense":
                this_week_expense += amt
                cat = txn.get("category", "Other Expense")
                category_expenses[cat] = category_expenses.get(cat, 0.0) + amt

        # Last week (days 8 to 14 ago)
        elif start_last_week <= d <= end_last_week:
            if txn_type == "expense":
                last_week_expense += amt

    # Calculate top categories
    sorted_cats = sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
    top_categories = []
    for cat_name, amt in sorted_cats[:5]:
        cat_info = get_category_info(cat_name)
        pct = (amt / this_week_expense * 100) if this_week_expense > 0 else 0.0
        top_categories.append({
            "category": cat_name,
            "emoji": cat_info["emoji"],
            "amount": amt,
            "pct": pct,
        })

    # Compare vs last week expense
    diff_pct = 0.0
    if last_week_expense > 0:
        diff_pct = ((this_week_expense - last_week_expense) / last_week_expense) * 100

    return {
        "start_date": start_this_week.strftime("%d %b"),
        "end_date": today.strftime("%d %b %Y"),
        "income": this_week_income,
        "expense": this_week_expense,
        "net": this_week_income - this_week_expense,
        "top_categories": top_categories,
        "vs_last_week_pct": diff_pct,
    }


def get_month_report() -> Dict[str, Any]:
    """Get summary for current month."""
    now = get_current_datetime()
    current_month_str = now.strftime("%Y-%m")

    transactions = sheets_service.get_all_transactions()

    month_income = 0.0
    month_expense = 0.0
    category_expenses: Dict[str, float] = {}
    total_count = 0

    for txn in transactions:
        d = _parse_date(txn.get("date", ""))
        if d and d.strftime("%Y-%m") == current_month_str:
            total_count += 1
            amt = float(txn.get("amount", 0.0))
            txn_type = txn.get("type", "expense")

            if txn_type == "income":
                month_income += amt
            elif txn_type == "expense":
                month_expense += amt
                cat = txn.get("category", "Other Expense")
                category_expenses[cat] = category_expenses.get(cat, 0.0) + amt

    # Top categories
    sorted_cats = sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
    top_categories = []
    for cat_name, amt in sorted_cats[:5]:
        cat_info = get_category_info(cat_name)
        top_categories.append({
            "category": cat_name,
            "emoji": cat_info["emoji"],
            "amount": amt,
        })

    balance = sheets_service.get_current_balance()

    return {
        "month_name": now.strftime("%B %Y"),
        "income": month_income,
        "expense": month_expense,
        "net": month_income - month_expense,
        "balance": balance,
        "top_categories": top_categories,
        "total_count": total_count,
    }
