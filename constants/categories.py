"""Category definitions, emojis, types, and keyword mappings for automatic detection."""

CATEGORIES = [
    # EXPENSES
    {
        "name": "Food",
        "emoji": "🍜",
        "type": "expense",
        "keywords": [
            "makan", "makanan", "bakso", "nasi", "kopi", "minum", "minuman",
            "restoran", "warteg", "gofood", "grabfood", "shopeefood", "snack",
            "sarapan", "siang", "malam", "cafe", "kafe", "roti", "susu", "boba", "ayam"
        ],
    },
    {
        "name": "Transport",
        "emoji": "🚗",
        "type": "expense",
        "keywords": [
            "gojek", "grab", "goride", "gocar", "bensin", "parkir", "tol",
            "bus", "kereta", "ojek", "mrt", "lrt", "taksi", "taxi", "pertalite", "pertamax"
        ],
    },
    {
        "name": "Shopping",
        "emoji": "🛒",
        "type": "expense",
        "keywords": [
            "beli", "belanja", "shopee", "tokped", "tokopedia", "lazada",
            "baju", "celana", "sepatu", "skincare", "supermarket", "indomaret", "alfa", "alfamart"
        ],
    },
    {
        "name": "Bills",
        "emoji": "📱",
        "type": "expense",
        "keywords": [
            "listrik", "air", "pdam", "internet", "pulsa", "wifi", "indihome",
            "biznet", "pln", "kuota", "langganan", "sewa", "kos", "kontrakan"
        ],
    },
    {
        "name": "Entertainment",
        "emoji": "🎮",
        "type": "expense",
        "keywords": [
            "nonton", "bioskop", "cinema", "game", "spotify", "netflix", "youtube",
            "hiburan", "liburan", "tiket", "jalan"
        ],
    },
    {
        "name": "Health",
        "emoji": "💊",
        "type": "expense",
        "keywords": [
            "obat", "dokter", "rumah sakit", "apotek", "vitamin", "klinik", "sehat"
        ],
    },
    {
        "name": "Education",
        "emoji": "📚",
        "type": "expense",
        "keywords": [
            "buku", "kursus", "kuliah", "les", "sekolah", "spp", "udemy", "seminar"
        ],
    },
    {
        "name": "Other Expense",
        "emoji": "📦",
        "type": "expense",
        "keywords": ["lainnya", "pengeluaran"],
    },
    # INCOME
    {
        "name": "Salary",
        "emoji": "💼",
        "type": "income",
        "keywords": ["gaji", "salary", "upah", "thr"],
    },
    {
        "name": "Freelance",
        "emoji": "💻",
        "type": "income",
        "keywords": ["freelance", "project", "klien", "sidegig", "projectan"],
    },
    {
        "name": "Transfer",
        "emoji": "💸",
        "type": "income",
        "keywords": ["transfer", "kiriman", "tf", "dapat"],
    },
    {
        "name": "Other Income",
        "emoji": "💰",
        "type": "income",
        "keywords": ["bonus", "hadiah", "cashback", "pemasukan", "untung", "bunga"],
    },
]

# Quick mappings for performance
DEFAULT_EXPENSE_CATEGORY = "Other Expense"
DEFAULT_INCOME_CATEGORY = "Other Income"


def get_category_info(category_name: str) -> dict:
    """Get category dict by name."""
    for cat in CATEGORIES:
        if cat["name"].lower() == category_name.lower():
            return cat
    return {"name": category_name, "emoji": "📝", "type": "expense", "keywords": []}
