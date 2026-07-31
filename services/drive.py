import io
import os
import uuid
from typing import Optional

from utils.logger import logger


class DriveService:
    """Service to upload receipt images to Google Drive."""

    def __init__(self):
        self.is_mock_mode: bool = True
        logger.info("DriveService initialized in Local/Mock mode for receipts.")

    def upload_receipt(
        self, file_bytes: bytes, filename: str = "receipt.jpg"
    ) -> str:
        """Upload image bytes to Google Drive or local mock store and return public URL."""
        unique_id = uuid.uuid4().hex[:8]
        clean_filename = f"receipt_{unique_id}_{filename}"

        # Mock fallback: create local storage URL
        mock_dir = os.path.join(os.path.dirname(__file__), "..", "logs", "receipts")
        os.makedirs(mock_dir, exist_ok=True)
        file_path = os.path.join(mock_dir, clean_filename)

        try:
            with open(file_path, "wb") as f:
                f.write(file_bytes)
            logger.info(f"Receipt saved locally at {file_path}")
            return f"https://drive.google.com/file/d/mock_{unique_id}/view"
        except Exception as e:
            logger.error(f"Error saving receipt: {e}")
            return f"https://drive.google.com/file/d/error/view"


drive_service = DriveService()
