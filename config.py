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
SPREADSHEET_ID = os.getenv(
    "SPREADSHEET_ID", "1mKESxM0hQc2oCUcWbqWiMssxeWz8ya0Fk5tQGbfVC90"
).strip().strip("'\"")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "FinanceBot_Database").strip().strip("'\"")

# Embedded fallback credentials for seamless zero-config cloud deployment
_DEFAULT_CREDENTIALS_B64 = """ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiYm90LWZpbmFuY2UtNTA0MTA4IiwKICAicHJpdmF0ZV9rZXlfaWQiOiAiNTE1MjVlY2U5OTEyMmIzZjE5NGQzNTRiYzM0MWJkYzg0OWM1ZDY4OSIsCiAgInByaXZhdGVfa2V5IjogIi0tLS0tQkVHSU4gUFJJVkFURSBLRVktLS0tLVxuTUlJRXZnSUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS2d3Z2dTa0FnRUFBb0lCQVFEQWtyZnBCeHdLNkMxOFxueURnRDRFb1VMYlNhQzZtam1IRjBvbnVhdFJ5K0RleVc2N0Q0UExOdVUzaU1VRDU0TXVFZXZkNEtuNktNUHAzbVxuUHlTK3hRTVQ0OEltbGxvTHkwajJnME9sbEl4TWZlL0tKTUpBMWdRa2U2RnpkMnU0TW4rS3UwWGtkeTNHYUZYNFxuaGRyMmNlRjNjMHpKUTJ3T2VsTjB3dlJVQjlSOVp0SXBuUzkyVGhJTGZKdkpocmJrdlVMbVMzWkRpT0pwTTZYNlxuVjZzQnpkWlMxWFZnNXdsS3F5VzhkTWhTSXp5VGU3YjhqTGxLRHhpNmQyQkUxeDNyV1F0QzYzNG1oZ21Oa1cxZlxuc1c2TXhDMklmMjV0REIxWDBRL3dTb0hiRE8rdmtDSUZ3b3IzYWhiMHdzNER0MHhpR09GOHUwczZvT1BBbGZwY1xub1FoUklUdEhBZ01CQUFFQ2dnRUFFbXBWYWxReTR5WWdmTW9teW43RWhzUE0wck1OSmhHdmFTc2FsOTVSb1NrZFxuWXJIODlVTFV3OWI1U2EyK0hqOTdWZ3NXZEpIMGVPWGZYVmtxSkpERzE3dys0UExJS2ZybTFOQVRydE5vUys1UFxuem9HNlk4OHppK0R1RW1mWCsycmZnSDczMHVrYURiQmFQRThNbnBHZ1crSEE5T1F5TFZEc1hJSkNNWUQ0THkrZlxuRTdzb09WSDA1OGd4cThDc0toMmxvOWk0eDFOTUI5OTBwNDZ5eVQ5bkJ5aFBZSjlPOFdTdmZyNVhvODErQVpOL1xuVWgraWNFcmRTSW10ZWJVTjkrek9EL0xxanN5azM3a2lwUHRuREJ2Y2xYQ1JEbkwwV2gxZ1RFcVdwUUNHMzIwRFxuUURUOWVrZEhadXRuRlBLQWRTTFpCcW5PVnJ1LzN3WmxKRTFJay9ReGNRS0JnUUQ0MmdVaWpsU0Zib09kQUFMc1xuQjRuVGkzRlczU3JMWGNaa2thVGxucVhuczN1QUNGLzE5TlA4aVdGaW1DTkVOeHc5VjN4TVZiT29Uek9DZ3BmbVxubjNjT0JSSkl3aTVQUkNNbnAwVGcrZERncXhQa2hoK09kd3Z4dEVqbngrRi8vZCtGRzJwRS9qMEgyRDV6bmR4K1xuUVdhMlg2TE8zb2ZpWEppdXdMRDZ0RWlJVVFLQmdRREdHdGZTamxWdkdzQ3BTQUdsM1ZhRkJLS0ExV1ZGZ0lmN1xuZ3RPVnhJNkNsMWhVY1RnbnA5bk9scDhuOVhFUXExYWl4Z2wzSHk0M3IzWk1rNmJvWkpXamJXVnMyUUNwQ25hbVxuekJjZ0hYU1ZIb0wveElzYWR6cjVjYkVVY0FYNktBN1NPZmUvemZnTzlkZVVtVGVuK0dGZFpaZi91WVVTSJo5a1xuMXBXbnM0bzhGd0tCZ1FEbmJFR0lRRnJqOThHWCtSRytsTWdkSGptWjhYWkJ5QVNmTkQ3b2Q2Q01HSU1Lcno4bVxuaWJlMnk3L3dJOUh3TjF3Z3c4SkpidzN6d1N3Qy9CWHRtSERzYmRUeUt2dE1KZTZYaXR2b2FRcFNWV2JiaDh2Q1xuL256eUc1b05Tdm92d0ZYbEFIalVqcWNOSzVId2pXY25Wd1VCSjNGTjl1N2htUUU0eXVRTFVpdDk4UUtCZ0h4UFxuK2VDNXltaTI2L0VPSzJLTzJ5MExkSUhONXdmUEdRVzkyZElnanFEcUlkYVRXWDZnK0srSG13WHpJZWtvNjJ1blxuUStkSlhMSTYyOHcvMXp2N2FsOHNWYm9SRGpZRlIrRnhMbzNMamczSklNRW83M1ZESG5ITFl5aUZCMnNyMmVrWFxuMFJ5K1BndjlQek9UVmZhRWlXeVhST09HNGpjMzRIb0JvZFdqZDNvdkFvR0JBTUFKL3NJQ3IvWWFPUFo1TmhMN1xubzJYaWZsUkM4RkwyK2ZUbFpPZjR6ZjNkeStBa29PNFdxWGZwa1FMZjFNbkszZnBUOUNHcHp0Q3QyVEs1c0F4cFxuRW54YVJ6SmlKYkhib2dGcUFwRDZ1cm91ekVQeGhHVDVnaFdkaXFUbjVlN0ZmZlp5TVg4UXBtSHcvczZvTG56aFxuL1lUckxNU21NMERyZUxtMks3UkY4eDN0XG4tLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tXG4iLAogICJjbGllbnRfZW1haWwiOiAiZmluYW5jZS1ib3RAYm90LWZpbmFuY2UtNTA0MTA4LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwNzc1MzQ3MTY0NjM4NzY4OTQ2NyIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvZmluYW5jZS1ib3QlNDBib3QtZmluYW5jZS01MDQxMDguaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"""

# Auto-generate credentials.json on disk if missing (for Railway/Cloud)
_cred_file_path = BASE_DIR / "credentials.json"
if not _cred_file_path.exists():
    try:
        import base64
        _content = GOOGLE_CREDENTIALS_JSON or _DEFAULT_CREDENTIALS_B64
        _content = _content.strip().strip("'\"")
        if not _content.startswith("{"):
            try:
                _content = base64.b64decode(_content).decode("utf-8")
            except Exception:
                pass
        with open(_cred_file_path, "w", encoding="utf-8") as _f:
            _f.write(_content)
    except Exception as _e:
        print(f"Warning: Failed to write credentials.json: {_e}")

# App Settings
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")
CURRENCY = os.getenv("CURRENCY", "IDR")
DEFAULT_REMINDER_TIME = os.getenv("DEFAULT_REMINDER_TIME", "20:00")
