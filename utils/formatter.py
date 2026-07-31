import re
from datetime import datetime
import pytz
import config


def format_currency(amount: float | int, currency_symbol: str = "Rp") -> str:
    """Format numeric amount into currency string.
    Example: 25000 -> 'Rp25.000', -15000 -> '-Rp15.000'
    """
    is_negative = amount < 0
    abs_amount = abs(int(amount))
    formatted = f"{abs_amount:,}".replace(",", ".")
    prefix = "-" if is_negative else ""
    return f"{prefix}{currency_symbol}{formatted}"


def parse_amount(text: str) -> float | None:
    """Parse amount strings supporting shortcuts like '25k', '25rb', '5jt', '5m', '25.000'.
    Returns float amount or None if invalid.
    """
    clean_text = text.lower().strip()
    
    # Replace dots in numbers if formatted as thousands (e.g., 25.000 -> 25000)
    # Check if dot is thousands separator (not a decimal point like 2.5jt)
    if re.match(r"^\d{1,3}(\.\d{3})+$", clean_text):
        clean_text = clean_text.replace(".", "")
    
    # Handle shortcuts
    multiplier = 1
    if clean_text.endswith("k") or clean_text.endswith("rb"):
        multiplier = 1_000
        clean_text = re.sub(r"(k|rb)$", "", clean_text)
    elif clean_text.endswith("jt") or clean_text.endswith("m"):
        multiplier = 1_000_000
        clean_text = re.sub(r"(jt|m)$", "", clean_text)
    
    # Replace comma with dot for decimals (e.g., 2,5jt -> 2.5 * 1_000_000)
    clean_text = clean_text.replace(",", ".")
    
    try:
        val = float(clean_text)
        return val * multiplier
    except ValueError:
        return None


def get_current_datetime(timezone_str: str = config.TIMEZONE) -> datetime:
    """Get current timezone-aware datetime."""
    tz = pytz.timezone(timezone_str)
    return datetime.now(tz)


def format_datetime(dt: datetime = None) -> str:
    """Format datetime for user response display (e.g., '31 Jul 2026, 14:30')."""
    if dt is None:
        dt = get_current_datetime()
    return dt.strftime("%d %b %Y, %H:%M")


def format_date(dt: datetime = None) -> str:
    """Format date string YYYY-MM-DD for database."""
    if dt is None:
        dt = get_current_datetime()
    return dt.strftime("%Y-%m-%d")


def format_time(dt: datetime = None) -> str:
    """Format time string HH:MM:SS for database."""
    if dt is None:
        dt = get_current_datetime()
    return dt.strftime("%H:%M:%S")
