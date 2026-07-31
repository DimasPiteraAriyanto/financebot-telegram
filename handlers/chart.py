from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from services.charts import (
    generate_bar_chart,
    generate_cashflow_chart,
    generate_pie_chart,
)
from utils.logger import logger
from utils.validator import is_user_allowed


async def chart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /chart command."""
    user = update.effective_user
    if not user or not is_user_allowed(user.id):
        return

    keyboard = [
        [
            InlineKeyboardButton("🥧 Pie Chart", callback_data="chart|pie"),
            InlineKeyboardButton("📊 Bar Chart", callback_data="chart|bar"),
        ],
        [
            InlineKeyboardButton("💰 Cashflow", callback_data="chart|cashflow"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "📊 **Pilih jenis grafik keuangan yang ingin ditampilkan:**",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


async def callback_chart_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callback for chart selection buttons."""
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data or ""

    if not data.startswith("chart|"):
        return

    chart_type = data.split("|")[1]

    buf = None
    caption = ""

    if chart_type == "pie":
        buf = generate_pie_chart()
        caption = "🥧 **Grafik Pengeluaran per Kategori**"
    elif chart_type == "bar":
        buf = generate_bar_chart()
        caption = "📊 **Grafik Perbandingan Kategori**"
    elif chart_type == "cashflow":
        buf = generate_cashflow_chart()
        caption = "💰 **Grafik Cashflow Pemasukan vs Pengeluaran**"

    if buf is None:
        await query.edit_message_text(
            "ℹ️ Belum ada data transaksi yang cukup untuk membuat grafik ini."
        )
        return

    # Delete menu message and send image photo
    if query.message:
        await query.message.delete()
        await query.message.reply_photo(
            photo=buf, caption=caption, parse_mode="Markdown"
        )
