from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application

import config
from services.report import get_today_report
from utils.formatter import format_currency
from utils.logger import logger

scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)


async def _send_daily_reminder(app: Application):
    """Job to send daily reminder at 20:00 if no transactions recorded today."""
    logger.info("Executing daily reminder check...")
    report = get_today_report()

    if report["total_count"] == 0 and config.ALLOWED_USER_IDS:
        msg = (
            "👋 **Hai! Belum ada transaksi yang dicatat hari ini.**\n\n"
            "Sudah ada pengeluaran atau pemasukan yang lupa dicatat?\n"
            "Ketik langsung, contoh:\n"
            "`-25000 makan siang`"
        )
        for uid in config.ALLOWED_USER_IDS:
            try:
                await app.bot.send_message(chat_id=uid, text=msg, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error sending daily reminder to {uid}: {e}")


async def _send_daily_summary(app: Application):
    """Job to send daily summary at 21:00."""
    logger.info("Executing daily summary job...")
    report = get_today_report()

    if config.ALLOWED_USER_IDS:
        inc_fmt = format_currency(report["income"])
        exp_fmt = format_currency(report["expense"])

        msg = (
            f"📋 **Ringkasan Hari Ini — {report['date_formatted']}**\n\n"
            f"➕ Pemasukan  : {inc_fmt}\n"
            f"➖ Pengeluaran: {exp_fmt}\n\n"
            f"📈 Total Transaksi: {report['total_count']}\n\n"
            f"Selamat malam! 🌙"
        )
        for uid in config.ALLOWED_USER_IDS:
            try:
                await app.bot.send_message(chat_id=uid, text=msg, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error sending daily summary to {uid}: {e}")


def setup_scheduler(app: Application):
    """Setup and start AsyncIOScheduler with daily cron triggers."""
    try:
        # Schedule Daily Reminder at 20:00
        scheduler.add_job(
            _send_daily_reminder,
            "cron",
            hour=20,
            minute=0,
            args=[app],
            id="daily_reminder",
            replace_existing=True,
        )

        # Schedule Daily Summary at 21:00
        scheduler.add_job(
            _send_daily_summary,
            "cron",
            hour=21,
            minute=0,
            args=[app],
            id="daily_summary",
            replace_existing=True,
        )

        scheduler.start()
        logger.info("AsyncIOScheduler started successfully (Reminder: 20:00, Summary: 21:00).")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
