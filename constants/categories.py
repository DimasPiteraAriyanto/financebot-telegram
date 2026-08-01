"""Category definitions, emojis, types, and keyword mappings for custom Note Pengeluaran 2026 spreadsheet."""

from typing import Any, Dict

CATEGORIES = [
    # EXPENSES
    {
        "name": "Jajan",
        "emoji": "🍧",
        "type": "expense",
        "keywords": [
            "jajan", "kopi", "ngopi", "makan", "minum", "snack", "boba", "bakso",
            "mixue", "bahari", "couvee", "fore", "roket", "es", "teh", "cafe", "kafe"
        ],
    },
    {
        "name": "Kebutuhan",
        "emoji": "🛒",
        "type": "expense",
        "keywords": [
            "kebutuhan", "maksi", "makan siang", "makan malam", "kwetiaw",
            "sembako", "beras", "sabun", "shampoo", "minyak", "tisu", "popok"
        ],
    },
    {
        "name": "Bensin",
        "emoji": "⛽",
        "type": "expense",
        "keywords": [
            "bensin", "pertamax", "pertalite", "bbm", "motor", "mobil", "shell"
        ],
    },
    {
        "name": "Belanja",
        "emoji": "🛍️",
        "type": "expense",
        "keywords": [
            "belanja", "beli", "shopee", "tokped", "tokopedia", "lazada",
            "baju", "celana", "sepatu", "skincare", "kaos", "tas"
        ],
    },
    {
        "name": "Rumah",
        "emoji": "🏠",
        "type": "expense",
        "keywords": [
            "rumah", "kos", "kontrakan", "listrik", "wifi", "air", "pdam", "pln", "indihome", "biznet"
        ],
    },
    {
        "name": "Amal",
        "emoji": "🤲",
        "type": "expense",
        "keywords": [
            "amal", "sedekah", "infaq", "zakat", "donasi", "masjid", "anak yatim"
        ],
    },
    {
        "name": "Trading",
        "emoji": "📈",
        "type": "expense",
        "keywords": [
            "trading", "crypto", "forex", "binance", "tokocrypto"
        ],
    },
    {
        "name": "Bibit",
        "emoji": "🟢",
        "type": "expense",
        "keywords": [
            "bibit", "reksadana", "pasar uang"
        ],
    },
    {
        "name": "Saham",
        "emoji": "📊",
        "type": "expense",
        "keywords": [
            "saham", "stock", "idx", "ajaib", "stockbit"
        ],
    },
    {
        "name": "Lain",
        "emoji": "📦",
        "type": "expense",
        "keywords": [
            "lain", "potong", "recoil", "biaya", "admin", "parkir", "tol", "servis"
        ],
    },
    # INCOMES
    {
        "name": "Gaji",
        "emoji": "💵",
        "type": "income",
        "keywords": [
            "gaji", "paycheck", "payroll", "gajian"
        ],
    },
    {
        "name": "Pemasukan",
        "emoji": "💰",
        "type": "income",
        "keywords": [
            "pemasukan", "income", "transfer", "bonus", "thr", "freelance", "dapat", "terima", "dikasih"
        ],
    },
]

CATEGORY_BY_NAME = {c["name"]: c for c in CATEGORIES}
DEFAULT_EXPENSE_CATEGORY = "Jajan"
DEFAULT_INCOME_CATEGORY = "Pemasukan"


def get_category_info(category_name_or_keyword: str) -> Dict[str, Any]:
    """Find category info by exact name or keyword match."""
    key = category_name_or_keyword.lower().strip()

    # Try exact name match first
    for cat in CATEGORIES:
        if cat["name"].lower() == key:
            return cat

    # Try keyword match
    for cat in CATEGORIES:
        for kw in cat["keywords"]:
            if kw.lower() in key or key in kw.lower():
                return cat

    return {
        "name": DEFAULT_EXPENSE_CATEGORY,
        "emoji": "🍧",
        "type": "expense",
        "keywords": [],
    }
