# pipeline/extract.py
import requests
import json
import logging
from datetime import date
from tenacity import retry, stop_after_attempt, wait_exponential
from db import get_db_connection

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://api.frankfurter.app"
BASE_CURRENCY = "USD"
TARGET_CURRENCIES = "UZS,RUB,EUR,GBP"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_rates(target_date="latest"):
    """Fetches exchange rates from the Frankfurter API with retry logic."""
    url = f"{BASE_URL}/{target_date}?from={BASE_CURRENCY}&to={TARGET_CURRENCIES}"
    logging.info(f"Fetching data from: {url}")
    
    response = requests.get(url)
    
    # Raise an exception for bad status codes (4xx or 5xx)
    response.raise_for_status() 
    return response.json()

def load_bronze(data, fetch_date):
    """Loads the raw JSON payload into the raw_rates (Bronze) table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert the Python dictionary back to a JSON string for SQL Server
    raw_json = json.dumps(data)
    
    try:
        # Check if we already have data for this date to avoid duplicates in Bronze (optional but good practice)
        cursor.execute("SELECT 1 FROM raw_rates WHERE fetch_date = ?", fetch_date)
        if cursor.fetchone():
            logging.info(f"Data for {fetch_date} already exists in Bronze layer. Skipping insert.")
            return

        query = """
        INSERT INTO raw_rates (fetch_date, base_currency, raw_json)
        VALUES (?, ?, ?)
        """
        cursor.execute(query, (fetch_date, BASE_CURRENCY, raw_json))
        conn.commit()
        logging.info(f"Successfully loaded data for {fetch_date} into Bronze layer.")
    
    except Exception as e:
        logging.error(f"Error loading data to Bronze: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def run_extraction(target_date="latest"):
    try:
        data = fetch_rates(target_date)
        
        # Determine the actual date of the data fetched
        # If 'latest' was passed, the API returns the date of the latest available rates
        actual_fetch_date = data.get('date') 
        
        load_bronze(data, actual_fetch_date)
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API Request failed: {e}")
    except Exception as e:
         logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Test the extraction for the latest rates
    run_extraction("latest")