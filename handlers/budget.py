from telegram import Update
from telegram.ext import ContextTypes

from services.budget import get_budget_status, set_category_budget
from utils.formatter import format_currency, parse_amount
from utils.logger import logger
from utils.validator import is_user_allowed


async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /budget command (View or Set budget).
    Usage:
      /budget -> View all budgets
      /budget set Food 2000000 -> Set Food budget to 2.000.000
    """
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    args = context.args or []

    # Handle /budget set <category> <amount>
    if len(args) >= 3 and args[0].lower() == "set":
        cat_input = args[1]
        amt_input = args[2]

        amt = parse_amount(amt_input)
        if amt is None or amt <= 0:
            if update.message:
                await update.message.reply_text(
                    "❌ Nominal budget tidak valid.\nContoh: `/budget set Food 2000000`",
                    parse_mode="Markdown",
                )
            return

        set_category_budget(cat_input, amt)
        amt_fmt = format_currency(amt)
        if update.message:
            await update.message.reply_text(
                f"✅ Budget **{cat_input.capitalize()}** ditetapkan sebesar **{amt_fmt}**/bulan.",
                parse_mode="Markdown",
            )
        return

    # View budgets
    statuses = get_budget_status()
    if not statuses:
        if update.message:
            await update.message.reply_text("ℹ️ Belum ada budget kategori yang diatur.")
        return

    lines = ["📊 **STATUS BUDGET BULAN INI**\n"]
    for item in statuses:
        usage_fmt = format_currency(item["usage"])
        limit_fmt = format_currency(item["limit"])
        rem_fmt = format_currency(item["remaining"])

        status_emoji = "🟢"
        if item["status"] == "warning":
            status_emoji = "⚠️"
        elif item["status"] == "exceeded":
            status_emoji = "🚨"

        lines.append(
            f"{status_emoji} {item['emoji']} **{item['category']}**\n"
            f"   {item['progress_bar']}\n"
            f"   Terpakai: {usage_fmt} / {limit_fmt} (Sisa: {rem_fmt})\n"
        )

    lines.append("💡 *Ketik `/budget set <kategori> <nominal>` untuk mengubah.*")

    if update.message:
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
