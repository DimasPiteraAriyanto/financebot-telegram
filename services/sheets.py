import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import gspread
from google.oauth2.service_account import Credentials

import config
from utils.cache import cache
from utils.formatter import format_date, format_datetime, format_time, get_current_datetime
from utils.logger import logger

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TRANSACTION_HEADERS = [
    "id",
    "date",
    "time",
    "type",
    "category",
    "amount",
    "note",
    "receipt_url",
    "balance",
    "created_at",
]


class SheetsService:
    """Service to interact with Google Sheets database."""

    def __init__(self):
        self.client: Optional[gspread.Client] = None
        self.spreadsheet: Optional[gspread.Spreadsheet] = None
        self.is_mock_mode: bool = False
        self._mock_data: List[Dict[str, Any]] = []
        self._init_connection()

    def _init_connection(self):
        """Initialize Google Sheets API client."""
        cred_file = config.GOOGLE_CREDENTIALS_FILE

        if os.path.exists(cred_file):
            try:
                creds = Credentials.from_service_account_file(cred_file, scopes=SCOPES)
                self.client = gspread.authorize(creds)
                logger.info("Successfully connected to Google Sheets API via credentials.json")
                self._ensure_spreadsheet()
                return
            except Exception as e:
                logger.warning(f"Failed to authorize Google Sheets API: {e}. Falling back to mock mode.")

        logger.info("Credentials file not found or invalid. Running SheetsService in Mock/Local mode.")
        self.is_mock_mode = True

    def _ensure_spreadsheet(self):
        """Ensure spreadsheet exists and has required worksheet structure."""
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

            # Ensure Transactions sheet exists
            try:
                worksheet = self.spreadsheet.worksheet("Transactions")
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title="Transactions", rows=1000, cols=10)
                worksheet.append_row(TRANSACTION_HEADERS)

            # Verify headers
            existing_headers = worksheet.row_values(1)
            if not existing_headers:
                worksheet.append_row(TRANSACTION_HEADERS)

            self.is_mock_mode = False
            logger.info("Google Sheets Service is FULLY ONLINE and connected!")

        except Exception as e:
            logger.warning(f"Google Sheets connection notice: {e}. Running in Graceful Local Mode.")
            self.is_mock_mode = True

    def get_current_balance(self) -> float:
        """Get latest running balance."""
        # Check cache first
        cached_bal = cache.get("current_balance")
        if cached_bal is not None:
            return cached_bal

        balance = 0.0

        if self.is_mock_mode:
            if self._mock_data:
                balance = float(self._mock_data[-1].get("balance", 0.0))
        else:
            try:
                worksheet = self.spreadsheet.worksheet("Transactions")
                records = worksheet.get_all_records()
                if records:
                    balance = float(records[-1].get("balance", 0.0))
            except Exception as e:
                logger.error(f"Error getting balance from Sheets: {e}")

        cache.set("current_balance", balance, ttl_seconds=300)
        return balance

    def append_transaction(
        self,
        txn_type: str,
        category: str,
        amount: float,
        note: str,
        receipt_url: str = "",
    ) -> Dict[str, Any]:
        """Append new transaction to Google Sheets database."""
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
                worksheet = self.spreadsheet.worksheet("Transactions")
                row_values = [row_data[col] for col in TRANSACTION_HEADERS]
                worksheet.append_row(row_values)
                logger.info(f"[GoogleSheets] Saved transaction {txn_id}")
            except Exception as e:
                logger.error(f"Error appending row to Google Sheets: {e}")
                # Save to mock as fallback to prevent data loss
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
                worksheet = self.spreadsheet.worksheet("Transactions")
                records = worksheet.get_all_records()
                if records:
                    last_row_index = len(records) + 1  # 1-indexed including header
                    deleted_record = records[-1]
                    worksheet.delete_rows(last_row_index)
                    
                    # Update balance cache
                    new_records = worksheet.get_all_records()
                    new_bal = float(new_records[-1]["balance"]) if new_records else 0.0
                    cache.set("current_balance", new_bal, ttl_seconds=300)
            except Exception as e:
                logger.error(f"Error deleting last transaction: {e}")

        cache.delete("recent_transactions")
        return deleted_record

    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all recorded transactions."""
        cached_txns = cache.get("recent_transactions")
        if cached_txns is not None:
            return cached_txns

        records = []
        if self.is_mock_mode:
            records = list(self._mock_data)
        else:
            try:
                worksheet = self.spreadsheet.worksheet("Transactions")
                records = worksheet.get_all_records()
            except Exception as e:
                logger.error(f"Error fetching transactions from Sheets: {e}")
                records = list(self._mock_data)

        cache.set("recent_transactions", records, ttl_seconds=300)
        return records


# Instantiate global sheets service
sheets_service = SheetsService()

