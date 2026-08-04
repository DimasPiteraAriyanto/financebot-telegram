from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants.categories import get_category_info
from constants.messages import (
    INVALID_FORMAT_MESSAGE,
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


def make_step1_type_keyboard(amount: float, note: str) -> InlineKeyboardMarkup:
    """Step 1: Choose transaction type (Pengeluaran vs Pemasukan)."""
    note_short = note[:20].replace("|", " ")
    keyboard = [
        [
            InlineKeyboardButton(
                "➖ Pengeluaran",
                callback_data=f"wiz|sheet|expense|{amount:.0f}|{note_short}",
            ),
            InlineKeyboardButton(
                "➕ Pemasukan",
                callback_data=f"wiz|sheet|income|{amount:.0f}|{note_short}",
            ),
        ],
        [InlineKeyboardButton("❌ Batal", callback_data="wiz|cancel|0|0")],
    ]
    return InlineKeyboardMarkup(keyboard)


def make_step2_sheet_keyboard(txn_type: str, amount: float, note: str) -> InlineKeyboardMarkup:
    """Step 2: Choose target sheet (DP vs EP)."""
    note_short = note[:20].replace("|", " ")
    keyboard = [
        [
            InlineKeyboardButton(
                "📄 Sheet DP",
                callback_data=f"wiz|cat|{txn_type}|dp|{amount:.0f}|{note_short}",
            ),
            InlineKeyboardButton(
                "📄 Sheet EP",
                callback_data=f"wiz|cat|{txn_type}|ep|{amount:.0f}|{note_short}",
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ Kembali ke Jenis Transaksi",
                callback_data=f"wiz|type|{amount:.0f}|{note_short}",
            )
        ],
        [InlineKeyboardButton("❌ Batal", callback_data="wiz|cancel|0|0")],
    ]
    return InlineKeyboardMarkup(keyboard)


def make_step3_category_keyboard(
    txn_type: str, tab_type: str, amount: float, note: str
) -> InlineKeyboardMarkup:
    """Step 3: Choose category name."""
    note_short = note[:20].replace("|", " ")
    amt_str = f"{amount:.0f}"

    if txn_type == "expense":
        keyboard = [
            [
                InlineKeyboardButton("🍨 Jajan", callback_data=f"wiz|save|expense|{tab_type}|Jajan|{amt_str}|{note_short}"),
                InlineKeyboardButton("⛽ Bensin", callback_data=f"wiz|save|expense|{tab_type}|Bensin|{amt_str}|{note_short}"),
                InlineKeyboardButton("🛒 Kebutuhan", callback_data=f"wiz|save|expense|{tab_type}|Kebutuhan|{amt_str}|{note_short}"),
            ],
            [
                InlineKeyboardButton("🛍️ Belanja", callback_data=f"wiz|save|expense|{tab_type}|Belanja|{amt_str}|{note_short}"),
                InlineKeyboardButton("🏠 Rumah", callback_data=f"wiz|save|expense|{tab_type}|Rumah|{amt_str}|{note_short}"),
                InlineKeyboardButton("🤲 Amal", callback_data=f"wiz|save|expense|{tab_type}|Amal|{amt_str}|{note_short}"),
            ],
            [
                InlineKeyboardButton("📈 Trading", callback_data=f"wiz|save|expense|{tab_type}|Trading|{amt_str}|{note_short}"),
                InlineKeyboardButton("🌱 Bibit", callback_data=f"wiz|save|expense|{tab_type}|Bibit|{amt_str}|{note_short}"),
                InlineKeyboardButton("📊 Saham", callback_data=f"wiz|save|expense|{tab_type}|Saham|{amt_str}|{note_short}"),
            ],
            [
                InlineKeyboardButton("📝 Lain", callback_data=f"wiz|save|expense|{tab_type}|Lain|{amt_str}|{note_short}"),
            ],
            [
                InlineKeyboardButton("⬅️ Kembali ke Pilihan Sheet", callback_data=f"wiz|sheet|expense|{amt_str}|{note_short}"),
            ],
            [InlineKeyboardButton("❌ Batal", callback_data="wiz|cancel|0|0")],
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("💰 Gaji", callback_data=f"wiz|save|income|{tab_type}|Gaji|{amt_str}|{note_short}"),
                InlineKeyboardButton("💵 Pemasukan", callback_data=f"wiz|save|income|{tab_type}|Pemasukan|{amt_str}|{note_short}"),
                InlineKeyboardButton("📈 Trading", callback_data=f"wiz|save|income|{tab_type}|Trading|{amt_str}|{note_short}"),
            ],
            [
                InlineKeyboardButton("📝 Lain", callback_data=f"wiz|save|income|{tab_type}|Lain|{amt_str}|{note_short}"),
            ],
            [
                InlineKeyboardButton("⬅️ Kembali ke Pilihan Sheet", callback_data=f"wiz|sheet|income|{amt_str}|{note_short}"),
            ],
            [InlineKeyboardButton("❌ Batal", callback_data="wiz|cancel|0|0")],
        ]

    return InlineKeyboardMarkup(keyboard)


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
        return

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
                f"• `25k fore {cat_name.lower()}` ➔ Masuk sheet *dp*\n\n"
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

    # 4. Handle Smart Detection / Wizard Launch (3-Step Interactive Wizard)
    if parsed.is_smart_detected:
        formatted_amt = format_currency(parsed.amount)
        prompt_text = (
            f"🔍 *Pencatatan Transaksi Barus*\n\n"
            f"💰 Nominal: *{formatted_amt}*\n"
            f"📝 Catatan: *{parsed.note}*\n\n"
            f"1️⃣ *Langkah 1*: Pilih Jenis Transaksi di bawah:"
        )

        reply_markup = make_step1_type_keyboard(parsed.amount, parsed.note)
        await update.message.reply_text(
            prompt_text, parse_mode="Markdown", reply_markup=reply_markup
        )
        return

    # 5. Explicit format (e.g. 'dp 25k fore jajan'): Save transaction immediately
    budget_warning = None
    if parsed.type == "expense":
        budget_warning = check_budget_warning(parsed.category, parsed.amount)

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
    """Handle 3-Step Wizard Inline Button Callbacks."""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    data = query.data or ""
    parts = data.split("|")

    if len(parts) < 2:
        return

    prefix = parts[0]
    if prefix not in ["wiz", "conf", "cat"]:
        return

    # ----------------------------------------------------
    # Handle Interactive Wizard ('wiz')
    # ----------------------------------------------------
    if prefix == "wiz":
        step = parts[1]

        if step == "cancel":
            await query.edit_message_text("❌ Transaksi dibatalkan.")
            return

        # Wizard Step 1: Edits back to Type Selection
        if step == "type":
            # wiz|type|amount|note
            amount = float(parts[2])
            note = parts[3]
            formatted_amt = format_currency(amount)
            prompt = (
                f"🔍 *Pencatatan Transaksi*\n\n"
                f"💰 Nominal: *{formatted_amt}*\n"
                f"📝 Catatan: *{note}*\n\n"
                f"1️⃣ *Langkah 1*: Pilih Jenis Transaksi di bawah:"
            )
            markup = make_step1_type_keyboard(amount, note)
            await query.edit_message_text(prompt, parse_mode="Markdown", reply_markup=markup)
            return

        # Wizard Step 2: Edits to Sheet Selection (DP vs EP)
        if step == "sheet":
            # wiz|sheet|txn_type|amount|note
            txn_type = parts[2]
            amount = float(parts[3])
            note = parts[4]
            formatted_amt = format_currency(amount)
            type_label = "Pengeluaran ➖" if txn_type == "expense" else "Pemasukan ➕"
            prompt = (
                f"📄 *Pilih Sheet Target*\n\n"
                f"Jenis: *{type_label}*\n"
                f"💰 Nominal: *{formatted_amt}*\n"
                f"📝 Catatan: *{note}*\n\n"
                f"2️⃣ *Langkah 2*: Pilih Sheet tempat menyimpan:"
            )
            markup = make_step2_sheet_keyboard(txn_type, amount, note)
            await query.edit_message_text(prompt, parse_mode="Markdown", reply_markup=markup)
            return

        # Wizard Step 3: Edits to Category Selection
        if step == "cat":
            # wiz|cat|txn_type|tab_type|amount|note
            txn_type = parts[2]
            tab_type = parts[3]
            amount = float(parts[4])
            note = parts[5]
            formatted_amt = format_currency(amount)
            type_label = "Pengeluaran ➖" if txn_type == "expense" else "Pemasukan ➕"
            prompt = (
                f"🏷️ *Pilih Kategori*\n\n"
                f"Jenis: *{type_label}* | Target: *Sheet {tab_type.upper()}*\n"
                f"💰 Nominal: *{formatted_amt}*\n"
                f"📝 Catatan: *{note}*\n\n"
                f"3️⃣ *Langkah 3*: Pilih Kategori transaksi:"
            )
            markup = make_step3_category_keyboard(txn_type, tab_type, amount, note)
            await query.edit_message_text(prompt, parse_mode="Markdown", reply_markup=markup)
            return

        # Wizard Step 4: Final Save Transaction
        if step == "save":
            # wiz|save|txn_type|tab_type|CategoryName|amount|note
            txn_type = parts[2]
            tab_type = parts[3]
            cat_name = parts[4]
            amount = float(parts[5])
            note = parts[6]

            info = get_category_info(cat_name)
            cat_emoji = info["emoji"]

            budget_warning = None
            if txn_type == "expense":
                budget_warning = check_budget_warning(cat_name, amount)

            record = sheets_service.append_transaction(
                txn_type=txn_type,
                category=cat_name,
                amount=amount,
                note=note,
                tab_type=tab_type,
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

            msg += f"\n📑 Sheet Target: *{record.get('created_at', '').split(', ')[-1]} ({tab_type.upper()})*"

            if budget_warning:
                msg += f"\n\n{budget_warning}"

            await query.edit_message_text(msg, parse_mode="Markdown")
            return

    # Legacy confirmation handlers
    if prefix in ["conf", "cat"]:
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

        if prefix == "conf":
            cat_name, cat_emoji = detect_category(note, action)
            txn_type = action
        else:
            cat_name = parts[1]
            info = get_category_info(cat_name)
            cat_emoji = info["emoji"]
            txn_type = info["type"]

        budget_warning = None
        if txn_type == "expense":
            budget_warning = check_budget_warning(cat_name, amount)

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
