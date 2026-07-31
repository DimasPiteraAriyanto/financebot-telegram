import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip().strip("'\"")

# Allowed Users (comma separated list of Telegram user IDs, or empty for public)
_allowed_users_raw = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS = [
    int(uid.strip()) for uid in _allowed_users_raw.split(",") if uid.strip().isdigit()
]

# Google API
GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_CREDENTIALS_FILE", str(BASE_DIR / "credentials.json")
).strip().strip("'\"")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip().strip("'\"")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "").strip().strip("'\"")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "FinanceBot_Database").strip().strip("'\"")

# App Settings
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")
CURRENCY = os.getenv("CURRENCY", "IDR")
DEFAULT_REMINDER_TIME = os.getenv("DEFAULT_REMINDER_TIME", "20:00")
