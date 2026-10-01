# pipeline/backfill.py
import logging
from datetime import date, timedelta
from extract import run_extraction
from transform_silver import process_bronze_to_silver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_backfill(days=14):
    """
    Backfills historical data for a specified number of days.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    logging.info(f"Starting backfill from {start_date} to {end_date}")
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        logging.info(f"--- Fetching historical data for {date_str} ---")
        
        # 1. Fetch and load to Bronze
        run_extraction(date_str)
        
        current_date += timedelta(days=1)
        
    logging.info("Historical data loaded to Bronze. Starting Silver transformation...")
    
    # 2. Process all new Bronze records into Silver
    process_bronze_to_silver()
    
    logging.info("Backfill complete!")

if __name__ == "__main__":
    # You can change the number of days to backfill here
    run_backfill(days=14)