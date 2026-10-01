# pipeline/db.py

import os
import pyodbc
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the SQL Server database."""
    server = os.environ.get("DB_SERVER")
    database = os.environ.get("DB_DATABASE")
    driver = os.environ.get("DB_DRIVER")
    
    # Connection string for Windows Authentication
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise