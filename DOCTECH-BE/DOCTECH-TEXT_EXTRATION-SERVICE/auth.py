# auth.py
from fastapi import Header, HTTPException
import os
from dotenv import load_dotenv

class APIKeyValidator:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Define the API key from environment variables
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY not found in environment variables.")

    async def verify_api_key(self, x_api_key: str = Header(...)):
        """Verify that the provided API key matches the expected API key."""
        if x_api_key != self.api_key:
            raise HTTPException(status_code=401, detail="Invalid API Key")
