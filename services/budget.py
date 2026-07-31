from typing import Any, Dict, List
from constants.categories import get_category_info
from services.report import get_month_report
from utils.cache import cache
from utils.formatter import format_currency


# In-memory store for category budget limits (Category -> Limit)
_BUDGET_STORE: Dict[str, float] = {
    "Food": 2000000.0,
    "Transport": 1000000.0,
    "Shopping": 1000000.0,
}


def set_category_budget(category: str, limit_amount: float) -> None:
    """Set monthly budget limit for a category."""
    cat_info = get_category_info(category)
    _BUDGET_STORE[cat_info["name"]] = limit_amount
    cache.delete("budget_status")


def make_progress_bar(pct: float, length: int = 10) -> str:
    """Generate ASCII progress bar string (e.g., '████████░░ 80%')."""
    filled_len = int(round(length * min(pct, 100) / 100))
    bar = "█" * filled_len + "░" * (length - filled_len)
    return f"`{bar}` {pct:.0f}%"


def get_budget_status() -> List[Dict[str, Any]]:
    """Get monthly budget status for all configured categories."""
    report = get_month_report()
    month_expense_by_cat = {
        cat["category"]: cat["amount"] for cat in report.get("top_categories", [])
    }

    result = []
    for cat_name, limit in _BUDGET_STORE.items():
        usage = month_expense_by_cat.get(cat_name, 0.0)
        pct = (usage / limit * 100) if limit > 0 else 0.0

        status = "ok"
        if pct >= 100:
            status = "exceeded"
        elif pct >= 80:
            status = "warning"

        cat_info = get_category_info(cat_name)
        result.append({
            "category": cat_name,
            "emoji": cat_info["emoji"],
            "limit": limit,
            "usage": usage,
            "remaining": max(0.0, limit - usage),
            "pct": pct,
            "progress_bar": make_progress_bar(pct),
            "status": status,
        })

    return result


def check_budget_warning(category: str, amount_added: float) -> str | None:
    """Check if adding amount breaches budget threshold (80% or 100%)."""
    cat_info = get_category_info(category)
    cat_name = cat_info["name"]

    if cat_name not in _BUDGET_STORE:
        return None

    limit = _BUDGET_STORE[cat_name]
    report = get_month_report()
    current_usage = sum(
        c["amount"] for c in report.get("top_categories", []) if c["category"] == cat_name
    )
    new_usage = current_usage + amount_added
    pct = (new_usage / limit * 100) if limit > 0 else 0.0

    limit_fmt = format_currency(limit)
    usage_fmt = format_currency(new_usage)

    if pct >= 100:
        return (
            f"🚨 **BUDGET TERLAMPAUI!**\n\n"
            f"{cat_info['emoji']} **{cat_name}** melebihi budget!\n"
            f"Terpakai: {usage_fmt} / {limit_fmt}\n\n"
            f"Transaksi tetap dicatat."
        )
    elif pct >= 80 and (current_usage / limit * 100) < 80:
        return (
            f"⚠️ **PERINGATAN BUDGET**\n\n"
            f"{cat_info['emoji']} **{cat_name}** telah mencapai {pct:.0f}%!\n"
            f"Terpakai: {usage_fmt} / {limit_fmt}\n\n"
            f"Hati-hati pengeluaran di kategori ini."
        )

    return None
