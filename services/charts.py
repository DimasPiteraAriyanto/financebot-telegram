import io
from typing import Dict, List
import matplotlib
# Use non-GUI Agg backend for headless server execution
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from constants.categories import get_category_info
from services.report import get_month_report, get_today_report, get_week_report
from services.sheets import sheets_service


def _apply_style():
    """Apply clean custom styling for matplotlib charts."""
    plt.style.use("ggplot")
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8


def generate_pie_chart() -> io.BytesIO | None:
    """Generate Pie Chart of current month expenses by category."""
    report = get_month_report()
    categories = report.get("top_categories", [])

    if not categories:
        return None

    labels = [cat["category"] for cat in categories]
    sizes = [cat["amount"] for cat in categories]
    colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#c2c2f0", "#ffb3e6"]

    _apply_style()
    fig, ax = plt.subplots(figsize=(6, 5), dpi=120)
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors[: len(sizes)],
        textprops=dict(color="#333333", fontsize=10),
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_weight("bold")

    ax.set_title(f"Pengeluaran Kategori ({report['month_name']})", fontsize=12, pad=15, weight="bold")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_bar_chart() -> io.BytesIO | None:
    """Generate Bar Chart comparing category expenses."""
    report = get_month_report()
    categories = report.get("top_categories", [])

    if not categories:
        return None

    labels = [cat["category"] for cat in categories]
    amounts = [cat["amount"] for cat in categories]

    _apply_style()
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=120)
    bars = ax.bar(labels, amounts, color="#4E79A7", edgecolor="#2B4C7E", width=0.55)

    ax.set_ylabel("Nominal (Rp)", fontsize=10)
    ax.set_title(f"Perbandingan Pengeluaran ({report['month_name']})", fontsize=12, pad=15, weight="bold")
    
    # Format Y ticks
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f"Rp{int(x):,}"))
    plt.xticks(rotation=15)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_cashflow_chart() -> io.BytesIO | None:
    """Generate Income vs Expense Cashflow Chart."""
    report = get_month_report()
    income = report.get("income", 0.0)
    expense = report.get("expense", 0.0)

    if income == 0 and expense == 0:
        return None

    labels = ["Pemasukan", "Pengeluaran"]
    values = [income, expense]
    colors = ["#2CA02C", "#D62728"]

    _apply_style()
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=120)
    bars = ax.bar(labels, values, color=colors, width=0.45)

    ax.set_ylabel("Nominal (Rp)", fontsize=10)
    ax.set_title(f"Cashflow Bulan ({report['month_name']})", fontsize=12, pad=15, weight="bold")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f"Rp{int(x):,}"))

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"Rp{int(height):,}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            weight="bold",
        )

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf
