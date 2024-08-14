# main.py
import os
import json
import logging
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Request
from fastapi.responses import FileResponse as FastAPIFileResponse
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv

from auth import APIKeyValidator
from file_handler import FileHandler
from text_extractor import TextExtractor
# from text_classifier import TextClassifier  # Commented out for now
from database import DatabaseHandler

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        self.allowed_origins = os.getenv("allowed_origins", "*").split(",")
        self.json_storage_dir = os.getenv("JSON_STORAGE_DIR", "/json_files")  # ใช้พาธภายใน container
        self.upload_dir = os.getenv("UPLOAD_DIR", "/files")  # กำหนดค่า upload directory
        self.log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()

def get_settings():
    return Settings()

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)
# ปรับระดับ logging สำหรับ pdfminer ให้เป็น INFO ขึ้นไป
logging.getLogger('pdfminer').setLevel(logging.INFO)
logging.getLogger('multipart').setLevel(logging.INFO)

# Initialize the app and its dependencies
app = FastAPI()
api_key_validator = APIKeyValidator()
file_handler = FileHandler(upload_dir=settings.upload_dir) 
text_extractor = TextExtractor()
database_handler = DatabaseHandler()

@app.on_event("startup")
async def startup_event():
    # Ensure the JSON storage directory exists
    os.makedirs(settings.json_storage_dir, exist_ok=True)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือใช้ allowed_origins จาก .env
    allow_credentials=True,
    allow_methods=["*"],  # อนุญาตทุก HTTP Methods
    allow_headers=["*"],  # อนุญาตทุก Headers
)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Define the response model
class FileResponse(BaseModel):
    filename: str
    filetype: str
    extracted_text: Optional[str] = None
    file_id: Optional[str] = None
    
@app.post("/v1/text-extract", response_model=FileResponse)
@limiter.limit("20/minute")
async def text_extract(
    request: Request,
    file: UploadFile = File(...),
    api_key: str = Depends(api_key_validator.verify_api_key)
):
    if not file:
        logger.error("No file received in the request.")
        raise HTTPException(status_code=400, detail="No file received.")
        
    logger.info(f"Received a file: {file.filename} with content type: {file.content_type}")
    
    try:
        file_path = await file_handler.save_uploaded_file(file)
        logger.info(f"File saved to {file_path}")

        file_type = file_handler.classify_file(file_path)
        logger.info(f"Classified file type: {file_type}")
        
        if file_type == 'Unknown':
            raise HTTPException(status_code=400, detail="Unable to classify file type.")
        
        file_id = database_handler.insert_classification(filename=file.filename, file_type=file_type)
        logger.info(f"Stored file classification in the database with file_id: {file_id}")

        request_date = str(request.headers.get("date", "unknown"))
        extracted_text = text_extractor.extract_text(file_path, file_type)

        # Step 6: Save the extracted text as a JSON file
        json_data = {
            "filename": file.filename,
            "extracted_text": extracted_text,
            "metadata": {
                "created_at": request_date,
                "filetype": file_type
            }
        }
        json_filename = f"{file_id}.json"
        json_filepath = os.path.join(settings.json_storage_dir, json_filename)
        logger.info(f"Saving JSON file to (full path): {os.path.abspath(json_filepath)}")

        logger.info(f"Saving JSON file to: {json_filepath}")
        try:
            with open(json_filepath, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)
            logger.info(f"Extracted text saved as JSON file: {json_filepath}")
        except Exception as e:
            logger.error(f"Failed to save JSON file: {e}")

        response = FileResponse(
            filename=file.filename,
            filetype=file_type,
            extracted_text=extracted_text,
            file_id=file_id
        )
        logger.info(f"Response prepared successfully for file: {file.filename}")
        
        # Remove the file after processing
        file_handler.remove_file(file_path)
        logger.info(f"File removed: {file_path}")
        
        return response

    except Exception as e:
        logger.error(f"An error occurred during processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred during processing: {str(e)}")

@app.get("/v1/json/{file_id}")
async def get_json_file(file_id: str):
    json_filepath = os.path.join(settings.json_storage_dir, f"{file_id}.json")
    if os.path.exists(json_filepath):
        return FastAPIFileResponse(json_filepath, media_type="application/json", filename=f"{file_id}.json")
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
