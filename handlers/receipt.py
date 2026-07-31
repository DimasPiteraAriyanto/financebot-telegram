from telegram import Update
from telegram.ext import ContextTypes

from services.drive import drive_service
from services.sheets import sheets_service
from utils.formatter import format_currency
from utils.logger import logger
from utils.validator import is_user_allowed


async def photo_receipt_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle photo upload for receipt proof."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    if not update.message or not update.message.photo:
        return

    # Get highest resolution photo
    photo = update.message.photo[-1]
    photo_file = await context.bot.get_file(photo.file_id)

    # Download file content as bytearray
    image_bytes = await photo_file.download_as_bytearray()

    # Upload to Google Drive
    url = drive_service.upload_receipt(bytes(image_bytes), f"user_{user.id}.jpg")

    # Link to recent transaction if available
    transactions = sheets_service.get_all_transactions()
    if not transactions:
        if update.message:
            await update.message.reply_text(
                f"📷 **Bukti tersimpan di Google Drive!**\n\nLink: {url}\n"
                f"ℹ️ Belum ada transaksi yang tercatat untuk ditautkan.",
                parse_mode="Markdown",
            )
        return

    last_txn = transactions[-1]
    last_txn["receipt_url"] = url

    amt_fmt = format_currency(last_txn["amount"])
    msg = (
        f"✅ **Bukti Transaksi Berhasil Ditautkan!**\n\n"
        f"📝 Transaksi: **{last_txn['note']}** ({amt_fmt})\n"
        f"📅 ID: `{last_txn['id']}`\n"
        f"🔗 Google Drive: [Lihat Bukti Foto]({url})"
    )

    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown")
