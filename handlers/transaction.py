from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants.messages import (
    INVALID_FORMAT_MESSAGE,
    SMART_DETECT_PROMPT,
    TRANSACTION_DELETED_MESSAGE,
    TRANSACTION_SUCCESS_MESSAGE,
    UNAUTHORIZED_MESSAGE,
)
from services.budget import check_budget_warning
from services.parser import detect_category, parse_transaction_input
from services.sheets import sheets_service
from utils.formatter import format_currency
from utils.logger import logger
from utils.validator import is_user_allowed


async def text_transaction_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle text input for adding transactions or smart detection."""
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

    if len(parts) < 4 or parts[0] != "conf":
        return

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

    # Check budget warning
    budget_warning = None
    if action == "expense":
        budget_warning = check_budget_warning(cat_name, amount)

    # Save transaction
    record = sheets_service.append_transaction(
        txn_type=action,
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
