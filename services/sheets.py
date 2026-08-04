import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import gspread
from google.oauth2.service_account import Credentials

import config
from utils.cache import cache
from utils.formatter import format_date, format_datetime, format_time, parse_amount
from utils.logger import logger

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

MONTH_NAMES_ID = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

TRANSACTION_HEADERS = [
    "id", "date", "time", "type", "category", "amount", "note", "receipt_url", "balance", "created_at"
]


def get_current_datetime() -> datetime:
    """Get current datetime localized."""
    import pytz
    tz = pytz.timezone(config.TIMEZONE)
    return datetime.now(tz)


class SheetsService:
    """Service to handle CRUD operations with Google Sheets API."""

    def __init__(self):
        self.client: Optional[gspread.Client] = None
        self.spreadsheet: Optional[gspread.Spreadsheet] = None
        self.is_mock_mode: bool = False
        self._mock_data: List[Dict[str, Any]] = []
        self._init_connection()

    def _init_connection(self):
        """Initialize Google Sheets API client."""
        # 1. Try raw or base64 JSON string from environment variable first
        if config.GOOGLE_CREDENTIALS_JSON:
            try:
                import json, base64
                raw_val = config.GOOGLE_CREDENTIALS_JSON.strip().strip("'\"")
                if not raw_val.startswith("{"):
                    try:
                        raw_val = base64.b64decode(raw_val).decode("utf-8")
                    except Exception:
                        pass

                info = json.loads(raw_val)
                if isinstance(info, dict) and "private_key" in info:
                    info["private_key"] = info["private_key"].replace("\\n", "\n")
                creds = Credentials.from_service_account_info(info, scopes=SCOPES)
                self.client = gspread.authorize(creds)
                logger.info("Successfully connected to Google Sheets API via GOOGLE_CREDENTIALS_JSON env var")
                self._ensure_spreadsheet()
                return
            except Exception as e:
                logger.error(f"Failed to authorize via GOOGLE_CREDENTIALS_JSON env var: {e}")

        # 2. Try credentials.json file on disk
        cred_file = config.GOOGLE_CREDENTIALS_FILE
        if os.path.exists(cred_file):
            try:
                creds = Credentials.from_service_account_file(cred_file, scopes=SCOPES)
                self.client = gspread.authorize(creds)
                logger.info("Successfully connected to Google Sheets API via credentials.json file")
                self._ensure_spreadsheet()
                return
            except Exception as e:
                logger.error(f"Failed to authorize Google Sheets API via file: {e}")

        logger.warning("Credentials not found or invalid. Running SheetsService in Graceful Local Mock mode.")
        self.is_mock_mode = True

    def _ensure_spreadsheet(self):
        """Ensure spreadsheet exists and has required structure."""
        if not self.client:
            return

        try:
            if config.SPREADSHEET_ID:
                self.spreadsheet = self.client.open_by_key(config.SPREADSHEET_ID)
                logger.info(f"Opened shared Google Spreadsheet by key: {config.SPREADSHEET_ID}")
            else:
                try:
                    self.spreadsheet = self.client.open(config.SPREADSHEET_NAME)
                except gspread.SpreadsheetNotFound:
                    logger.info(f"Spreadsheet '{config.SPREADSHEET_NAME}' not found. Creating new...")
                    self.spreadsheet = self.client.create(config.SPREADSHEET_NAME)

            self.is_mock_mode = False
            logger.info("Google Sheets Service is FULLY ONLINE and connected!")

        except Exception as e:
            logger.warning(f"Google Sheets connection notice: {e}. Running in Graceful Local Mode.")
            self.is_mock_mode = True

    def _get_target_worksheet(self, dt: datetime, tab_suffix: str = "dp") -> gspread.Worksheet:
        """Get or create target worksheet for active month (e.g. 'Agustus dp')."""
        month_name = MONTH_NAMES_ID.get(dt.month, "Agustus")
        sheet_title = f"{month_name} {tab_suffix}"

        worksheets = {w.title.lower(): w for w in self.spreadsheet.worksheets()}
        if sheet_title.lower() in worksheets:
            return worksheets[sheet_title.lower()]
        
        # Fallback to first available worksheet if named sheet not found
        try:
            return self.spreadsheet.worksheet("Transactions")
        except Exception:
            return self.spreadsheet.sheet1

    def get_current_balance(self) -> float:
        """Get latest running balance."""
        cached_bal = cache.get("current_balance")
        if cached_bal is not None:
            return cached_bal

        txns = self.get_all_transactions()
        balance = txns[-1]["balance"] if txns else 0.0
        cache.set("current_balance", balance, ttl_seconds=300)
        return balance

    def append_transaction(
        self,
        txn_type: str,
        category: str,
        amount: float,
        note: str,
        receipt_url: str = "",
        tab_type: str = "dp",
    ) -> Dict[str, Any]:
        """Append new transaction to Google Sheets database."""
        if self.is_mock_mode and not getattr(self, "force_mock_mode", False):
            if config.GOOGLE_CREDENTIALS_JSON or os.path.exists(config.GOOGLE_CREDENTIALS_FILE):
                self._init_connection()

        now = get_current_datetime()
        txn_id = f"TXN-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        
        current_bal = self.get_current_balance()
        new_balance = current_bal + amount if txn_type == "income" else current_bal - amount

        row_data = {
            "id": txn_id,
            "date": format_date(now),
            "time": format_time(now),
            "type": txn_type,
            "category": category,
            "amount": amount,
            "note": note,
            "receipt_url": receipt_url,
            "balance": new_balance,
            "created_at": format_datetime(now),
        }

        if self.is_mock_mode:
            self._mock_data.append(row_data)
            logger.info(f"[MockSheets] Saved transaction: {row_data}")
        else:
            try:
                # Target active monthly sheet e.g. 'Agustus dp' or 'Agustus ep'
                ws = self._get_target_worksheet(now, tab_suffix=tab_type)
                
                # Check if worksheet is custom layout (has 'Tanggal' or 'Pengeluaran' in headers)
                all_rows = ws.get_all_values()
                if len(all_rows) >= 4 and any("tanggal" in (c or "").lower() for c in all_rows[3]):
                    # Custom Note Pengeluaran 2026 layout
                    target_row = 6
                    while target_row <= len(all_rows):
                        r = all_rows[target_row - 1]
                        # Stop if reached summary section
                        if len(r) > 1 and "TOTAL" in r[1].upper():
                            break
                        # Check if row is empty in cols F & H
                        f_val = r[5] if len(r) > 5 else ""
                        h_val = r[7] if len(r) > 7 else ""
                        c_val = r[2] if len(r) > 2 else ""
                        d_val = r[3] if len(r) > 3 else ""
                        e_val = r[4] if len(r) > 4 else ""
                        if not f_val and not h_val and not c_val and not d_val and not e_val:
                            break
                        target_row += 1

                    # Formatted amount
                    amt_str = f" Rp {amount:,.0f} ".replace(",", ".")
                    date_str = now.strftime("%d %m %Y")
                    
                    pemasukan_cat = category if txn_type == "income" else ""
                    pengeluaran_cat = category if txn_type == "expense" else ""
                    pemasukan_amt = amt_str if txn_type == "income" else ""
                    pengeluaran_amt = amt_str if txn_type == "expense" else ""

                    values = [
                        date_str,          # Col B
                        pemasukan_cat,     # Col C
                        pengeluaran_cat,   # Col D
                        pemasukan_amt,     # Col E
                        pengeluaran_amt,   # Col F
                        True,              # Col G (Checkbox status Lunas)
                        f" {note} "        # Col H (Keterangan)
                    ]
                    
                    ws.update(range_name=f"B{target_row}:H{target_row}", values=[values], value_input_option="USER_ENTERED")
                    logger.info(f"[GoogleSheets] Saved custom transaction {txn_id} to {ws.title} Row {target_row}")
                else:
                    # Standard Transactions sheet format
                    row_values = [row_data[col] for col in TRANSACTION_HEADERS]
                    ws.append_row(row_values)
                    logger.info(f"[GoogleSheets] Saved standard transaction {txn_id} to {ws.title}")

            except Exception as e:
                logger.error(f"Error appending row to Google Sheets: {e}")
                self._mock_data.append(row_data)

        # Update cache
        cache.set("current_balance", new_balance, ttl_seconds=300)
        cache.delete("recent_transactions")

        return row_data

    def delete_last_transaction(self) -> Optional[Dict[str, Any]]:
        """Delete the last recorded transaction (Undo)."""
        deleted_record = None

        if self.is_mock_mode:
            if self._mock_data:
                deleted_record = self._mock_data.pop()
                new_bal = self._mock_data[-1]["balance"] if self._mock_data else 0.0
                cache.set("current_balance", new_bal, ttl_seconds=300)
        else:
            try:
                now = get_current_datetime()
                ws = self._get_target_worksheet(now, tab_suffix="dp")
                all_rows = ws.get_all_values()
                if len(all_rows) >= 4 and any("tanggal" in (c or "").lower() for c in all_rows[3]):
                    # Find last non-empty row before summary
                    last_row = 5
                    for r_idx in range(6, len(all_rows) + 1):
                        r = all_rows[r_idx - 1]
                        if len(r) > 1 and "TOTAL" in r[1].upper():
                            break
                        f_val = r[5] if len(r) > 5 else ""
                        h_val = r[7] if len(r) > 7 else ""
                        if f_val or h_val:
                            last_row = r_idx

                    if last_row >= 6:
                        row_vals = all_rows[last_row - 1]
                        deleted_record = {
                            "category": row_vals[3] or row_vals[2] or "General",
                            "amount": parse_amount(row_vals[5] or row_vals[4] or "0"),
                            "note": row_vals[7] if len(row_vals) > 7 else "",
                        }
                        ws.update(range_name=f"B{last_row}:H{last_row}", values=[["", "", "", "", "", False, ""]], value_input_option="USER_ENTERED")
                else:
                    records = ws.get_all_records()
                    if records:
                        last_row_index = len(records) + 1
                        deleted_record = records[-1]
                        ws.delete_rows(last_row_index)
            except Exception as e:
                logger.error(f"Error deleting last transaction: {e}")

        cache.delete("recent_transactions")
        cache.delete("current_balance")
        return deleted_record

    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all recorded transactions from all sheets."""
        cached_txns = cache.get("recent_transactions")
        if cached_txns is not None:
            return cached_txns

        records = []
        if self.is_mock_mode:
            records = list(self._mock_data)
        else:
            try:
                worksheets = self.spreadsheet.worksheets()
                calc_balance = 0.0
                for ws in worksheets:
                    all_rows = ws.get_all_values()
                    if len(all_rows) >= 6 and any("tanggal" in (c or "").lower() for c in all_rows[3]):
                        for r_idx in range(6, len(all_rows) + 1):
                            r = all_rows[r_idx - 1]
                            if len(r) > 1 and "TOTAL" in r[1].upper():
                                break
                            
                            tgl = r[1] if len(r) > 1 else ""
                            pem_cat = r[2] if len(r) > 2 else ""
                            peng_cat = r[3] if len(r) > 3 else ""
                            pem_amt = parse_amount(r[4]) if len(r) > 4 else 0.0
                            peng_amt = parse_amount(r[5]) if len(r) > 5 else 0.0
                            status = r[6] if len(r) > 6 else ""
                            note = r[7].strip() if len(r) > 7 else ""

                            if not pem_amt and not peng_amt and not note:
                                continue

                            txn_type = "income" if pem_amt > 0 else "expense"
                            amt = pem_amt if pem_amt > 0 else peng_amt
                            cat = pem_cat if pem_cat else (peng_cat if peng_cat else "Lain")

                            calc_balance += (amt if txn_type == "income" else -amt)

                            records.append({
                                "id": f"TXN-{ws.title}-{r_idx}",
                                "date": tgl,
                                "time": "00:00:00",
                                "type": txn_type,
                                "category": cat,
                                "amount": amt,
                                "note": note,
                                "status": status,
                                "balance": calc_balance,
                                "created_at": f"{tgl}, {ws.title}",
                            })
                    else:
                        try:
                            std_recs = ws.get_all_records()
                            for r in std_recs:
                                records.append(r)
                        except Exception:
                            pass
            except Exception as e:
                logger.error(f"Error fetching transactions from Sheets: {e}")
                records = list(self._mock_data)

        cache.set("recent_transactions", records, ttl_seconds=300)
        return records


# Instantiate global sheets service
sheets_service = SheetsService()
