from telegram import Update
from telegram.ext import ContextTypes

from services.report import (
    get_month_report,
    get_saldo_summary,
    get_today_report,
    get_week_report,
)
from services.sheets import sheets_service
from utils.formatter import format_currency
from utils.logger import logger
from utils.validator import is_user_allowed


async def saldo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /saldo command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    summary = get_saldo_summary()
    bal_fmt = format_currency(summary["balance"])
    inc_fmt = format_currency(summary["month_income"])
    exp_fmt = format_currency(summary["month_expense"])

    msg = (
        f"💳 **Saldo Keuangan**\n\n"
        f"Saldo saat ini: **{bal_fmt}**\n\n"
        f"📊 **Bulan ini:**\n"
        f"  ➕ Pemasukan : {inc_fmt}\n"
        f"  ➖ Pengeluaran: {exp_fmt}\n\n"
        f"📅 Terakhir dicatat: {summary['last_date']}"
    )

    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown")


async def today_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /today command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    report = get_today_report()
    inc_fmt = format_currency(report["income"])
    exp_fmt = format_currency(report["expense"])

    msg_lines = [
        f"📋 **Laporan Hari Ini — {report['date_formatted']}**\n",
        f"➕ Pemasukan: {inc_fmt}",
        f"➖ Pengeluaran: {exp_fmt}\n",
    ]

    if report["transactions"]:
        msg_lines.append("Detail:")
        for t in report["transactions"]:
            prefix = "+" if t["type"] == "income" else "-"
            amt_fmt = format_currency(t["amount"])
            note_str = f" {t['note']}" if t["note"] else ""
            msg_lines.append(f"  {t['emoji']} `{prefix}{amt_fmt}`{note_str}")
    else:
        msg_lines.append("ℹ️ Belum ada transaksi hari ini.")

    msg_lines.append(f"\nTotal transaksi: {report['total_count']}")

    if update.message:
        await update.message.reply_text("\n".join(msg_lines), parse_mode="Markdown")


async def week_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /week command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    report = get_week_report()
    inc_fmt = format_currency(report["income"])
    exp_fmt = format_currency(report["expense"])
    net_fmt = format_currency(report["net"])

    msg_lines = [
        f"📋 **Laporan Minggu Ini**",
        f"{report['start_date']} - {report['end_date']}\n",
        f"➕ Pemasukan  : {inc_fmt}",
        f"➖ Pengeluaran: {exp_fmt}",
        f"📊 Net        : {net_fmt}\n",
    ]

    if report["top_categories"]:
        msg_lines.append("Top Pengeluaran:")
        for idx, cat in enumerate(report["top_categories"], 1):
            amt_fmt = format_currency(cat["amount"])
            msg_lines.append(f"  {idx}. {cat['emoji']} {cat['category']} : {amt_fmt} ({cat['pct']:.1f}%)")
    else:
        msg_lines.append("ℹ️ Tidak ada pengeluaran minggu ini.")

    diff = report["vs_last_week_pct"]
    arrow = "⬆️" if diff > 0 else "⬇️"
    msg_lines.append(f"\nvs Minggu lalu: {arrow} {abs(diff):.1f}% pengeluaran")

    if update.message:
        await update.message.reply_text("\n".join(msg_lines), parse_mode="Markdown")


async def month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /month command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    report = get_month_report()
    inc_fmt = format_currency(report["income"])
    exp_fmt = format_currency(report["expense"])
    net_fmt = format_currency(report["net"])
    bal_fmt = format_currency(report["balance"])

    msg_lines = [
        f"📋 **Laporan Bulanan — {report['month_name']}**\n",
        f"💰 **CASHFLOW**",
        f"  ➕ Pemasukan  : {inc_fmt}",
        f"  ➖ Pengeluaran: {exp_fmt}",
        f"  📊 Net        : {net_fmt}",
        f"  💳 Saldo      : {bal_fmt}\n",
    ]

    if report["top_categories"]:
        msg_lines.append("🏆 **TOP PENGELUARAN**")
        for idx, cat in enumerate(report["top_categories"], 1):
            amt_fmt = format_currency(cat["amount"])
            msg_lines.append(f"  {idx}. {cat['emoji']} {cat['category']} : {amt_fmt}")

    msg_lines.append(f"\n📈 Total Transaksi: {report['total_count']}")

    if update.message:
        await update.message.reply_text("\n".join(msg_lines), parse_mode="Markdown")


async def hapus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /hapus command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    deleted = sheets_service.delete_last_transaction()
    if not deleted:
        if update.message:
            await update.message.reply_text("ℹ️ Tidak ada transaksi untuk dihapus.")
        return

    formatted_amt = format_currency(deleted["amount"])
    msg = f"🗑️ Transaksi **{deleted['id']}** ({formatted_amt} - {deleted.get('note', '')}) berhasil dihapus."

    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown")
