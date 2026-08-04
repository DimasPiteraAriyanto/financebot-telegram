from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants.messages import HELP_MESSAGE, UNAUTHORIZED_MESSAGE, WELCOME_MESSAGE
from utils.logger import logger
from utils.validator import is_user_allowed


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get persistent reply keyboard for Main Menu."""
    keyboard = [
        ["💸 Catat Pengeluaran", "💰 Catat Pemasukan"],
        ["📊 /saldo", "📈 /chart", "ℹ️ /help"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


def get_expense_keyboard() -> ReplyKeyboardMarkup:
    """Get persistent reply keyboard for Expense categories."""
    keyboard = [
        ["🍨 Jajan", "⛽ Bensin", "🛒 Kebutuhan"],
        ["🛍️ Belanja", "🏠 Rumah", "🤲 Amal"],
        ["📈 Trading", "🌱 Bibit", "📊 Saham"],
        ["📝 Lain", "🔙 Kembali Ke Menu Utama"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


def get_income_keyboard() -> ReplyKeyboardMarkup:
    """Get persistent reply keyboard for Income categories."""
    keyboard = [
        ["💰 Gaji", "💵 Pemasukan Lain"],
        ["📈 Profit Trading", "🔙 Kembali Ke Menu Utama"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


# For backward compatibility
def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    return get_main_menu_keyboard()


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
        reply_markup = get_main_menu_keyboard()
        await update.message.reply_text(
            WELCOME_MESSAGE + "\n\n💡 *Pilih menu di bawah: Catat Pengeluaran atau Catat Pemasukan!*",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    if update.message:
        reply_markup = get_main_menu_keyboard()
        await update.message.reply_text(
            HELP_MESSAGE,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


async def kategori_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /kategori command to show main category menu."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    if update.message:
        reply_markup = get_main_menu_keyboard()
        await update.message.reply_text(
            "🔤 *Menu Keuangan*\n\nPilih *💸 Catat Pengeluaran* atau *💰 Catat Pemasukan* di bawah:",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
