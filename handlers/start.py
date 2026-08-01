from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants.messages import HELP_MESSAGE, UNAUTHORIZED_MESSAGE, WELCOME_MESSAGE
from utils.logger import logger
from utils.validator import is_user_allowed


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Get persistent reply keyboard with clickable category shortcuts."""
    keyboard = [
        ["🍨 Jajan", "⛽ Bensin", "🛒 Kebutuhan"],
        ["🛍️ Belanja", "🏠 Rumah", "🤲 Amal"],
        ["📈 Trading", "🌱 Bibit", "📊 Saham"],
        ["📝 Lain", "💰 Gaji", "📊 /saldo"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        logger.warning(f"Unauthorized access attempt by user_id={user.id if user else 'Unknown'}")
        if update.message:
            await update.message.reply_text(UNAUTHORIZED_MESSAGE)
        return

    logger.info(f"User {user.id} ({user.username}) started bot.")
    if update.message:
        reply_markup = get_main_reply_keyboard()
        await update.message.reply_text(
            WELCOME_MESSAGE + "\n\n💡 *Tombol Shortcut Kategori aktif di bawah keyboard Anda!*",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    if update.message:
        reply_markup = get_main_reply_keyboard()
        await update.message.reply_text(
            HELP_MESSAGE,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


async def kategori_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /kategori command to show clickable category menu."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    if update.message:
        reply_markup = get_main_reply_keyboard()
        await update.message.reply_text(
            "🔤 *Menu Shortcut Kategori*\n\nKlik salah satu tombol kategori di bawah keyboard untuk melihat contoh penggunaan cepat!",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
