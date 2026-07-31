from telegram import Update
from telegram.ext import ContextTypes

from constants.messages import HELP_MESSAGE, UNAUTHORIZED_MESSAGE, WELCOME_MESSAGE
from utils.logger import logger
from utils.validator import is_user_allowed


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
        await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    if update.message:
        await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")
