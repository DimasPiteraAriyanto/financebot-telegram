import re
from dataclasses import dataclass
from constants.categories import (
    CATEGORIES,
    DEFAULT_EXPENSE_CATEGORY,
    DEFAULT_INCOME_CATEGORY,
    get_category_info,
)
from utils.formatter import parse_amount
from utils.validator import sanitize_note, validate_amount


@dataclass
class ParsedTransaction:
    type: str  # "expense", "income", or "unknown"
    amount: float
    note: str
    category: str
    category_emoji: str
    tab_type: str = "dp"  # "dp" or "ep"
    is_smart_detected: bool = False


CATEGORY_SHORTCUTS = {
    "j": "Jajan", "jj": "Jajan", "jajn": "Jajan", "jajan": "Jajan",
    "b": "Bensin", "bs": "Bensin", "bsn": "Bensin", "bensin": "Bensin",
    "k": "Kebutuhan", "kb": "Kebutuhan", "kbt": "Kebutuhan", "kebutuhan": "Kebutuhan",
    "bl": "Belanja", "bj": "Belanja", "blj": "Belanja", "belanja": "Belanja",
    "r": "Rumah", "rm": "Rumah", "rmh": "Rumah", "rumah": "Rumah",
    "a": "Amal", "am": "Amal", "aml": "Amal", "amal": "Amal",
    "t": "Trading", "tr": "Trading", "trd": "Trading", "trading": "Trading",
    "bb": "Bibit", "bbt": "Bibit", "bibit": "Bibit",
    "s": "Saham", "sh": "Saham", "shm": "Saham", "saham": "Saham",
    "l": "Lain", "ln": "Lain", "lain": "Lain",
    "g": "Gaji", "gj": "Gaji", "gaji": "Gaji",
    "p": "Pemasukan", "pem": "Pemasukan", "pemasukan": "Pemasukan",
}


def parse_tab_and_category(note: str, txn_type: str = "expense") -> tuple[str, str, str, str]:
    """Parse tab_type ('dp'/'ep'), category_name, category_emoji, and cleaned note from input."""
    clean_note = note.strip()
    tab_type = "dp"

    # Check for 'ep' or 'dp' tab flag in note
    words = clean_note.split()
    filtered_words = []
    for w in words:
        w_lower = w.lower().strip(":")
        if w_lower in ["ep", "tab_ep", "tab-ep"]:
            tab_type = "ep"
        elif w_lower in ["dp", "tab_dp", "tab-dp"]:
            tab_type = "dp"
        else:
            filtered_words.append(w)

    clean_note = " ".join(filtered_words).strip()
    explicit_category = None

    # Check for category shortcut prefix (e.g. 'j: kopi fore' or 'j kopi fore')
    if ":" in clean_note:
        prefix, rest = clean_note.split(":", 1)
        prefix_key = prefix.strip().lower()
        if prefix_key in CATEGORY_SHORTCUTS:
            explicit_category = CATEGORY_SHORTCUTS[prefix_key]
            clean_note = rest.strip()

    if not explicit_category and clean_note:
        first_word = clean_note.split()[0].lower()
        if first_word in CATEGORY_SHORTCUTS:
            explicit_category = CATEGORY_SHORTCUTS[first_word]
            rest_words = clean_note.split()[1:]
            if rest_words:
                clean_note = " ".join(rest_words)

    if explicit_category:
        info = get_category_info(explicit_category)
        return tab_type, info["name"], info["emoji"], clean_note if clean_note else explicit_category

    # Fallback to keyword autodetect
    cat_name, cat_emoji = detect_category(clean_note, txn_type)
    return tab_type, cat_name, cat_emoji, clean_note if clean_note else "Transaksi"


def detect_category(note: str, txn_type: str = "expense") -> tuple[str, str]:
    """Auto detect category name and emoji based on keywords in note."""
    clean_note = note.lower()

    # Match exact keywords first
    for cat in CATEGORIES:
        if txn_type != "unknown" and cat["type"] != txn_type:
            continue
        for keyword in cat["keywords"]:
            if re.search(rf"\b{re.escape(keyword)}\b", clean_note) or keyword in clean_note:
                return cat["name"], cat["emoji"]

    default_cat_name = (
        DEFAULT_INCOME_CATEGORY if txn_type == "income" else DEFAULT_EXPENSE_CATEGORY
    )
    info = get_category_info(default_cat_name)
    return info["name"], info["emoji"]


def parse_transaction_input(text: str) -> ParsedTransaction | None:
    """Parse text input into ParsedTransaction dataclass.
    Supports natural format: 'dp 25k fore jajan', 'ep 50k pertamax b', '25k kopi jajan'
    as well as standard '-25k kopi jajan' and '+5jt gaji'.
    """
    raw_text = text.strip()
    if not raw_text:
        return None

    # Case 0: Natural Format '[sheet_type] [amount] [note...] [category/shortcut]'
    # Examples: 'dp 25k fore jajan', 'ep 50k pertamax b', '25k fore jajan', 'dp 25k fore'
    tokens = raw_text.split()
    if len(tokens) >= 2 and not raw_text.startswith("-") and not raw_text.startswith("+"):
        tab_type = "dp"
        start_idx = 0
        first_token = tokens[0].lower().strip(":")

        if first_token in ["dp", "ep"]:
            tab_type = first_token
            start_idx = 1

        if len(tokens) > start_idx:
            parsed_amt = parse_amount(tokens[start_idx])
            if parsed_amt is not None and validate_amount(parsed_amt):
                note_words = tokens[start_idx + 1:]
                explicit_cat = None

                if note_words:
                    last_word = note_words[-1].lower().strip(":")
                    if last_word in CATEGORY_SHORTCUTS:
                        explicit_cat = CATEGORY_SHORTCUTS[last_word]
                        note_words = note_words[:-1]
                    else:
                        for cat in CATEGORIES:
                            if cat["name"].lower() == last_word:
                                explicit_cat = cat["name"]
                                note_words = note_words[:-1]
                                break

                note_clean = " ".join(note_words).strip() if note_words else "Pengeluaran"
                if not explicit_cat:
                    cat_name, cat_emoji = detect_category(note_clean, "expense")
                else:
                    info = get_category_info(explicit_cat)
                    cat_name, cat_emoji = info["name"], info["emoji"]

                return ParsedTransaction(
                    type="expense",
                    amount=parsed_amt,
                    note=note_clean,
                    category=cat_name,
                    category_emoji=cat_emoji,
                    tab_type=tab_type,
                    is_smart_detected=False,
                )

    # Case 1 & 2: Explicit prefix '+' or '-'
    if raw_text.startswith("-") or raw_text.startswith("+"):
        prefix = raw_text[0]
        txn_type = "expense" if prefix == "-" else "income"
        body = raw_text[1:].strip()

        tokens = body.split(maxsplit=1)
        if not tokens:
            return None

        amount_str = tokens[0]
        note_str = tokens[1] if len(tokens) > 1 else ""

        parsed_amt = parse_amount(amount_str)
        if parsed_amt is None or not validate_amount(parsed_amt):
            tokens = body.rsplit(maxsplit=1)
            if len(tokens) == 2:
                parsed_amt = parse_amount(tokens[1])
                note_str = tokens[0]

        if parsed_amt is None or not validate_amount(parsed_amt):
            return None

        note_raw = sanitize_note(note_str) if note_str else ("Pengeluaran" if txn_type == "expense" else "Pemasukan")
        tab_type, cat_name, cat_emoji, note_clean = parse_tab_and_category(note_raw, txn_type)

        return ParsedTransaction(
            type=txn_type,
            amount=parsed_amt,
            note=note_clean,
            category=cat_name,
            category_emoji=cat_emoji,
            tab_type=tab_type,
            is_smart_detected=False,
        )

    # Case 3: Smart Detection (no prefix)
    tokens = raw_text.split()
    amount_found = None
    note_tokens = []

    for token in tokens:
        amt = parse_amount(token)
        if amt is not None and validate_amount(amt) and amount_found is None:
            amount_found = amt
        else:
            note_tokens.append(token)

    if amount_found is not None:
        note_str = " ".join(note_tokens) if note_tokens else "Transaksi"
        note_raw = sanitize_note(note_str)
        tab_type, cat_name, cat_emoji, note_clean = parse_tab_and_category(note_raw, "expense")

        return ParsedTransaction(
            type="unknown",
            amount=amount_found,
            note=note_clean,
            category=cat_name,
            category_emoji=cat_emoji,
            tab_type=tab_type,
            is_smart_detected=True,
        )

    return None
