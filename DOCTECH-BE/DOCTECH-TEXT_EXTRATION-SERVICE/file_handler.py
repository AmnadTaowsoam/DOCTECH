## file_handler.py
import os
import filetype
from fastapi import HTTPException, UploadFile
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

try:
    import aiofiles
    async_mode = True
except ImportError:
    async_mode = False

class FileHandler:
    def __init__(self, upload_dir: str = "/files"):  # ใช้ directory ที่ mount ใน container
        self.upload_dir = upload_dir
        self.ensure_upload_directory_exists()

    def ensure_upload_directory_exists(self, path: str = None):
        """Ensure the base upload directory and any necessary subdirectories exist."""
        directory = path if path else self.upload_dir
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

    async def save_uploaded_file(self, file: UploadFile) -> str:
        file_location = os.path.join(self.upload_dir, file.filename)
        directory = os.path.dirname(file_location)
        
        # Ensure the directory exists
        self.ensure_upload_directory_exists(directory)
        
        try:
            if async_mode:
                async with aiofiles.open(file_location, "wb") as f:
                    content = await file.read()
                    await f.write(content)
            else:
                with open(file_location, "wb") as f:
                    content = await file.read()
                    f.write(content)
            logger.info(f"File saved successfully: {file_location}")
            return file_location
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    def classify_file(self, file_path: str) -> str:
        kind = filetype.guess(file_path)
        if kind is None:
            logger.warning(f"Failed to classify file: {file_path}")
            return 'Unknown'
        logger.info(f"File classified as: {kind.mime}")
        return kind.mime

    def remove_file(self, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File removed: {file_path}")
        else:
            logger.warning(f"Tried to remove non-existent file: {file_path}")
