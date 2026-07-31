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
    is_smart_detected: bool = False


def detect_category(note: str, txn_type: str = "expense") -> tuple[str, str]:
    """Auto detect category name and emoji based on keywords in note."""
    clean_note = note.lower()

    # Match exact keywords first
    for cat in CATEGORIES:
        # Filter by type matching if known
        if txn_type != "unknown" and cat["type"] != txn_type:
            continue
        for keyword in cat["keywords"]:
            # Check full word or sub-word match
            if re.search(rf"\b{re.escape(keyword)}\b", clean_note) or keyword in clean_note:
                return cat["name"], cat["emoji"]

    # Fallback default category
    default_cat_name = (
        DEFAULT_INCOME_CATEGORY if txn_type == "income" else DEFAULT_EXPENSE_CATEGORY
    )
    info = get_category_info(default_cat_name)
    return info["name"], info["emoji"]


def parse_transaction_input(text: str) -> ParsedTransaction | None:
    """Parse text input into ParsedTransaction dataclass.
    Supports:
      1. '-25000 makan siang' or '-25k makan' (Expense)
      2. '+5000000 gaji juli' or '+5jt gaji' (Income)
      3. 'bakso 25000' or '25000 bakso' (Smart Detection)
    Returns ParsedTransaction or None if unrecognized.
    """
    raw_text = text.strip()
    if not raw_text:
        return None

    # Case 1 & 2: Explicit prefix '+' or '-'
    if raw_text.startswith("-") or raw_text.startswith("+"):
        prefix = raw_text[0]
        txn_type = "expense" if prefix == "-" else "income"
        body = raw_text[1:].strip()

        # Split amount token from note token
        tokens = body.split(maxsplit=1)
        if not tokens:
            return None

        amount_str = tokens[0]
        note_str = tokens[1] if len(tokens) > 1 else ""

        # Check if first token is numeric/amount shortcut
        parsed_amt = parse_amount(amount_str)
        if parsed_amt is None or not validate_amount(parsed_amt):
            # Check if last token is numeric (e.g. '-makan 25000')
            tokens = body.rsplit(maxsplit=1)
            if len(tokens) == 2:
                parsed_amt = parse_amount(tokens[1])
                note_str = tokens[0]

        if parsed_amt is None or not validate_amount(parsed_amt):
            return None

        note_clean = sanitize_note(note_str) if note_str else ("Pengeluaran" if txn_type == "expense" else "Pemasukan")
        cat_name, cat_emoji = detect_category(note_clean, txn_type)

        return ParsedTransaction(
            type=txn_type,
            amount=parsed_amt,
            note=note_clean,
            category=cat_name,
            category_emoji=cat_emoji,
            is_smart_detected=False,
        )

    # Case 3: Smart Detection (no prefix)
    # Looking for a number/shortcut token in string
    # Matches patterns like: 'bakso 25000', '25k kopi', 'nasi goreng 20.000'
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
        note_clean = sanitize_note(note_str)
        cat_name, cat_emoji = detect_category(note_clean, "expense")

        return ParsedTransaction(
            type="unknown",  # Requires user confirmation via inline buttons
            amount=amount_found,
            note=note_clean,
            category=cat_name,
            category_emoji=cat_emoji,
            is_smart_detected=True,
        )

    return None
