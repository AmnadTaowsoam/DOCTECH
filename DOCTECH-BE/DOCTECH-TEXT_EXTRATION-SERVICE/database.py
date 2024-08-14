import os
import psycopg2
from psycopg2 import sql
from fastapi import HTTPException
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables from .env file
load_dotenv()

class DatabaseHandler:
    def __init__(self):
        # Load database configuration from environment variables
        self.db_name = os.getenv("TEXT_EXTRACT_DB_NAME")
        self.db_username = os.getenv("TEXT_EXTRACT_DB_USERNAME")
        self.db_password = os.getenv("TEXT_EXTRACT_DB_PASSWORD")
        self.db_host = os.getenv("TEXT_EXTRACT_DB_HOST")
        self.db_port = os.getenv("TEXT_EXTRACT_DB_PORT")

    def get_db_connection(self):
        try:
            return psycopg2.connect(
                dbname=self.db_name,
                user=self.db_username,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to the database: {str(e)}")

    def execute_query(self, query, params):
        """Helper function to execute a query and return the result."""
        conn = self.get_db_connection()
        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchone()[0] if cursor.description else None
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
        finally:
            conn.close()

    def insert_classification(self, filename: str, file_type: str) -> str:
        """Insert classification data into the 'doctech.file_type' table."""
        query = """
            INSERT INTO doctech.file_type (filename, filetype)
            VALUES (%s, %s) RETURNING file_id;
        """
        return self.execute_query(query, (filename, file_type))

    def insert_shipment_info(self, file_id: str, header_name: str, temperature: str, quantity: str,
                             booking: str, carrier: str, feeder: str, vessel: str, port: str,
                             etd: str, eta: str, cy_date: str, return_date: str, destination: str) -> str:
        """Insert shipment information into the 'doctech.shipment_info' table."""
        query = """
            INSERT INTO doctech.shipment_info (file_id, header_name, temperature, quantity,
                booking, carrier, feeder, vessel, port, etd, eta, cy_date, return_date, destination)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING shipment_id;
        """
        return self.execute_query(query, (
            file_id, header_name, temperature, quantity,
            booking, carrier, feeder, vessel, port,
            etd, eta, cy_date, return_date, destination
        ))
