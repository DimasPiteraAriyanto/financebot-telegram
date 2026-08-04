from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants.categories import get_category_info
from constants.messages import (
    INVALID_FORMAT_MESSAGE,
    SMART_DETECT_PROMPT,
    TRANSACTION_DELETED_MESSAGE,
    TRANSACTION_SUCCESS_MESSAGE,
    UNAUTHORIZED_MESSAGE,
)
from handlers.start import (
    get_expense_keyboard,
    get_income_keyboard,
    get_main_menu_keyboard,
)
from services.budget import check_budget_warning
from services.parser import detect_category, parse_transaction_input
from services.sheets import sheets_service
from utils.formatter import format_currency
from utils.logger import logger
from utils.validator import is_user_allowed

CATEGORY_BUTTON_MAP = {
    "🍨 Jajan": ("Jajan", "🍨", "j", "expense"),
    "⛽ Bensin": ("Bensin", "⛽", "b", "expense"),
    "🛒 Kebutuhan": ("Kebutuhan", "🛒", "k", "expense"),
    "🛍️ Belanja": ("Belanja", "🛍️", "bl", "expense"),
    "🏠 Rumah": ("Rumah", "🏠", "r", "expense"),
    "🤲 Amal": ("Amal", "🤲", "a", "expense"),
    "📈 Trading": ("Trading", "📈", "t", "expense"),
    "🌱 Bibit": ("Bibit", "🌱", "bb", "expense"),
    "📊 Saham": ("Saham", "📊", "s", "expense"),
    "📝 Lain": ("Lain", "📝", "l", "expense"),
    "💰 Gaji": ("Gaji", "💰", "g", "income"),
    "💵 Pemasukan Lain": ("Pemasukan", "💵", "p", "income"),
    "📈 Profit Trading": ("Trading", "📈", "t", "income"),
}


async def text_transaction_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle text input for adding transactions, sub-menu navigation, or smart detection."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        if update.message:
            await update.message.reply_text(UNAUTHORIZED_MESSAGE)
        return

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    if text.startswith("/"):
        return  # Ignore command messages

    # 1. Handle Navigation Menu Taps
    if text in ["💸 Catat Pengeluaran", "Pengeluaran"]:
        reply_markup = get_expense_keyboard()
        await update.message.reply_text(
            "💸 *Menu Pengeluaran*\n\nPilih kategori pengeluaran Anda di bawah:",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
        return

    if text in ["💰 Catat Pemasukan", "Pemasukan"]:
        reply_markup = get_income_keyboard()
        await update.message.reply_text(
            "💰 *Menu Pemasukan*\n\nPilih kategori pemasukan Anda di bawah:",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
        return

    if text in ["🔙 Kembali Ke Menu Utama", "🔙 Kembali", "Kembali"]:
        reply_markup = get_main_menu_keyboard()
        await update.message.reply_text(
            "🏠 *Kembali ke Menu Utama*\n\nPilih menu yang Anda inginkan di bawah:",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
        return

    # 2. Handle Direct Category Button Tap
    if text in CATEGORY_BUTTON_MAP:
        cat_name, emoji, code, txn_type = CATEGORY_BUTTON_MAP[text]
        if txn_type == "expense":
            prompt = (
                f"{emoji} *Kategori Pengeluaran: {cat_name}*\n\n"
                f"Ketik nominal & catatan Anda. Contoh:\n"
                f"• `dp 25k fore {cat_name.lower()}` ➔ Masuk sheet *dp*\n"
                f"• `ep 25k fore {cat_name.lower()}` ➔ Masuk sheet *ep*\n"
                f"• `-25k fore {cat_name.lower()}` ➔ Masuk sheet *dp*\n\n"
                f"💡 *Atau shortcut cepat*: `-{code}: 25k fore`"
            )
        else:
            prompt = (
                f"{emoji} *Kategori Pemasukan: {cat_name}*\n\n"
                f"Ketik nominal & catatan Anda. Contoh:\n"
                f"• `+5jt gaji juli` ➔ Masuk sheet *dp*\n"
                f"• `+500k bonus ep` ➔ Masuk sheet *ep*"
            )

        await update.message.reply_text(prompt, parse_mode="Markdown")
        return

    # 3. Parse input text into transaction
    parsed = parse_transaction_input(text)
    if not parsed:
        await update.message.reply_text(INVALID_FORMAT_MESSAGE, parse_mode="Markdown")
        return

    # Handle Smart Detection (requires user confirmation via Inline Keyboard)
    if parsed.is_smart_detected:
        formatted_amt = format_currency(parsed.amount)
        prompt_text = SMART_DETECT_PROMPT.format(
            note=parsed.note,
            amount_formatted=formatted_amt,
            emoji=parsed.category_emoji,
            category=parsed.category,
        )

        note_short = parsed.note[:25].replace("|", " ")
        keyboard = [
            [
                InlineKeyboardButton(
                    "➖ Pengeluaran",
                    callback_data=f"conf|expense|{parsed.amount}|{note_short}",
                ),
                InlineKeyboardButton(
                    "➕ Pemasukan",
                    callback_data=f"conf|income|{parsed.amount}|{note_short}",
                ),
            ],
            [
                InlineKeyboardButton("🍨 Jajan", callback_data=f"cat|Jajan|{parsed.amount}|{note_short}"),
                InlineKeyboardButton("⛽ Bensin", callback_data=f"cat|Bensin|{parsed.amount}|{note_short}"),
                InlineKeyboardButton("🛒 Kebutuhan", callback_data=f"cat|Kebutuhan|{parsed.amount}|{note_short}"),
            ],
            [
                InlineKeyboardButton("🛍️ Belanja", callback_data=f"cat|Belanja|{parsed.amount}|{note_short}"),
                InlineKeyboardButton("🏠 Rumah", callback_data=f"cat|Rumah|{parsed.amount}|{note_short}"),
                InlineKeyboardButton("🤲 Amal", callback_data=f"cat|Amal|{parsed.amount}|{note_short}"),
            ],
            [
                InlineKeyboardButton("📈 Trading", callback_data=f"cat|Trading|{parsed.amount}|{note_short}"),
                InlineKeyboardButton("🌱 Bibit", callback_data=f"cat|Bibit|{parsed.amount}|{note_short}"),
                InlineKeyboardButton("💰 Gaji", callback_data=f"cat|Gaji|{parsed.amount}|{note_short}"),
            ],
            [InlineKeyboardButton("❌ Batal", callback_data="conf|cancel|0|none")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            prompt_text, parse_mode="Markdown", reply_markup=reply_markup
        )
        return

    # Check budget warning for expense
    budget_warning = None
    if parsed.type == "expense":
        budget_warning = check_budget_warning(parsed.category, parsed.amount)

    # Explicit format: Save transaction immediately
    record = sheets_service.append_transaction(
        txn_type=parsed.type,
        category=parsed.category,
        amount=parsed.amount,
        note=parsed.note,
        tab_type=parsed.tab_type,
    )

    formatted_amt = format_currency(record["amount"])
    formatted_bal = format_currency(record["balance"])

    msg = TRANSACTION_SUCCESS_MESSAGE.format(
        emoji=parsed.category_emoji,
        category=record["category"],
        amount_formatted=formatted_amt,
        note=record["note"],
        datetime_formatted=record["created_at"],
        balance_formatted=formatted_bal,
    )

    if budget_warning:
        msg += f"\n\n{budget_warning}"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def callback_confirmation_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle inline button callbacks for transaction confirmation."""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    data = query.data or ""
    parts = data.split("|")

    if len(parts) < 4:
        return

    prefix = parts[0]
    if prefix not in ["conf", "cat"]:
        return

    if prefix == "conf":
        action = parts[1]
        if action == "cancel":
            await query.edit_message_text("❌ Transaksi dibatalkan.")
            return

        try:
            amount = float(parts[2])
            note = parts[3]
        except ValueError:
            await query.edit_message_text("❌ Error memproses data transaksi.")
            return

        cat_name, cat_emoji = detect_category(note, action)
        txn_type = action
    elif prefix == "cat":
        cat_name = parts[1]
        try:
            amount = float(parts[2])
            note = parts[3]
        except ValueError:
            await query.edit_message_text("❌ Error memproses data transaksi.")
            return

        info = get_category_info(cat_name)
        cat_emoji = info["emoji"]
        txn_type = info["type"]

    # Check budget warning
    budget_warning = None
    if txn_type == "expense":
        budget_warning = check_budget_warning(cat_name, amount)

    # Save transaction
    record = sheets_service.append_transaction(
        txn_type=txn_type,
        category=cat_name,
        amount=amount,
        note=note,
    )

    formatted_amt = format_currency(record["amount"])
    formatted_bal = format_currency(record["balance"])

    msg = TRANSACTION_SUCCESS_MESSAGE.format(
        emoji=cat_emoji,
        category=record["category"],
        amount_formatted=formatted_amt,
        note=record["note"],
        datetime_formatted=record["created_at"],
        balance_formatted=formatted_bal,
    )

    if budget_warning:
        msg += f"\n\n{budget_warning}"

    await query.edit_message_text(msg, parse_mode="Markdown")


async def undo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /undo command to delete the last transaction."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    deleted = sheets_service.delete_last_transaction()
    if not deleted:
        if update.message:
            await update.message.reply_text("ℹ️ Tidak ada transaksi untuk dibatalkan.")
        return

    formatted_amt = format_currency(deleted["amount"])
    msg = TRANSACTION_DELETED_MESSAGE.format(
        transaction_id=deleted["id"], amount_formatted=formatted_amt
    )

    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown")
