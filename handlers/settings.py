from telegram import Update
from telegram.ext import ContextTypes

import config
from services.sheets import sheets_service
from utils.validator import is_user_allowed


async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command to display bot status and configuration."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    mode = "Mock (Local)" if sheets_service.is_mock_mode else "Google Sheets Live API"
    allowed = ", ".join(str(u) for u in config.ALLOWED_USER_IDS) if config.ALLOWED_USER_IDS else "Semua User (Public)"

    msg = (
        f"⚙️ **Pengaturan & Status FinanceBot**\n\n"
        f"🌐 **Mode Database**: `{mode}`\n"
        f"⏱️ **Timezone**: `{config.TIMEZONE}`\n"
        f"💱 **Mata Uang**: `{config.CURRENCY}`\n"
        f"🔔 **Pengingat Harian**: `{config.DEFAULT_REMINDER_TIME}`\n"
        f"🔐 **Otorisasi User**: `{allowed}`\n\n"
        f" 📑 Spreadsheet: `{config.SPREADSHEET_NAME}`"
    )

    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown")
