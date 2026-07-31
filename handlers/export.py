import io
import pandas as pd
from telegram import Update
from telegram.ext import ContextTypes

from services.sheets import sheets_service
from utils.logger import logger
from utils.validator import is_user_allowed


async def export_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /export command to export all transactions as a CSV document."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    transactions = sheets_service.get_all_transactions()
    if not transactions:
        if update.message:
            await update.message.reply_text("ℹ️ Belum ada transaksi untuk diexport.")
        return

    df = pd.DataFrame(transactions)
    csv_bytes = io.BytesIO()
    df.to_csv(csv_bytes, index=False, encoding="utf-8")
    csv_bytes.seek(0)
    csv_bytes.name = "transactions_export.csv"

    if update.message:
        await update.message.reply_document(
            document=csv_bytes,
            caption="📂 **File Data Transaksi Keuangan (CSV)**",
            parse_mode="Markdown",
        )
