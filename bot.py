import sys
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import config
from handlers.budget import budget_handler
from handlers.chart import callback_chart_handler, chart_handler
from handlers.export import export_handler
from handlers.receipt import photo_receipt_handler
from handlers.report import (
    hapus_handler,
    month_handler,
    saldo_handler,
    today_handler,
    week_handler,
)
from handlers.settings import settings_handler
from handlers.start import help_handler, start_handler
from handlers.transaction import (
    callback_confirmation_handler,
    text_transaction_handler,
    undo_handler,
)
from services.scheduler import setup_scheduler
from utils.logger import logger


async def post_init(application: Application) -> None:
    """Callback function executed after Application is initialized and event loop is running."""
    setup_scheduler(application)


def main():
    """Main entry point to initialize and start FinanceBot Telegram."""
    token = config.TELEGRAM_BOT_TOKEN

    if not token or token == "your_telegram_bot_token_here":
        logger.error(
            "TELEGRAM_BOT_TOKEN is missing or not set in .env file! "
            "Please copy .env.example to .env and set your token."
        )
        sys.exit(1)

    logger.info("Initializing FinanceBot Telegram...")
    app = ApplicationBuilder().token(token).post_init(post_init).build()

    # Register Basic & Help Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("settings", settings_handler))

    # Register Report Handlers (Phase 2)
    app.add_handler(CommandHandler("saldo", saldo_handler))
    app.add_handler(CommandHandler("today", today_handler))
    app.add_handler(CommandHandler("week", week_handler))
    app.add_handler(CommandHandler("month", month_handler))
    app.add_handler(CommandHandler("hapus", hapus_handler))
    app.add_handler(CommandHandler("undo", undo_handler))

    # Register Visualization & Budget Handlers (Phase 3)
    app.add_handler(CommandHandler("chart", chart_handler))
    app.add_handler(CommandHandler("budget", budget_handler))

    # Register Export Handler (Phase 4)
    app.add_handler(CommandHandler("export", export_handler))

    # Register Receipt Photo Handler
    app.add_handler(MessageHandler(filters.PHOTO, photo_receipt_handler))

    # Register Callback Handlers
    app.add_handler(CallbackQueryHandler(callback_chart_handler, pattern=r"^chart\|"))
    app.add_handler(CallbackQueryHandler(callback_confirmation_handler, pattern=r"^conf\|"))

    # Register Text Message Handler (for Transaction Input)
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), text_transaction_handler)
    )

    logger.info("Bot is polling for updates... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
