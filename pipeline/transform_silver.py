# pipeline/transform_silver.py
import json
import logging
from db import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_bronze_to_silver():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Fetch unprocessed records from Bronze
        # We only process dates that aren't already in the Silver table
        query = """
            SELECT r.fetch_date, r.base_currency, r.raw_json
            FROM raw_rates r
            LEFT JOIN cleaned_rates c 
                ON r.fetch_date = c.date
            WHERE c.date IS NULL
        """
        cursor.execute(query)
        unprocessed_rows = cursor.fetchall()
        
        if not unprocessed_rows:
            logging.info("No new Bronze records to process into Silver.")
            return

        # List of currencies we *want* to track
        expected_targets = ['UZS', 'RUB', 'EUR', 'GBP']
        clean_records_to_insert = []

        # 2. Parse and Validate
        for row in unprocessed_rows:
            fetch_date = row.fetch_date
            base_currency = row.base_currency
            
            # Parse the JSON string back into a Python dictionary
            try:
                data = json.loads(row.raw_json)
                rates = data.get('rates', {})
            except json.JSONDecodeError:
                logging.error(f"Failed to parse JSON for date {fetch_date}. Skipping.")
                continue

            # 3. Handle missing data and validate rates
            for target in expected_targets:
                if target not in rates:
                    # This handles the missing UZS and RUB gracefully!
                    logging.warning(f"[{fetch_date}] Missing data for {target}. Skipping this currency.")
                    continue
                
                exchange_rate = rates[target]
                
                # Validation: Rate must be greater than 0
                if exchange_rate <= 0:
                    logging.warning(f"[{fetch_date}] Invalid rate ({exchange_rate}) for {target}. Skipping.")
                    continue
                
                # If it passes, add it to our list for insertion
                clean_records_to_insert.append((fetch_date, base_currency, target, exchange_rate))

        # 4. Load into Silver
        if clean_records_to_insert:
            insert_query = """
                INSERT INTO cleaned_rates (date, base_currency, target_currency, exchange_rate)
                VALUES (?, ?, ?, ?)
            """
            # executemany inserts all the valid records in one efficient batch
            cursor.executemany(insert_query, clean_records_to_insert)
            conn.commit()
            logging.info(f"Successfully loaded {len(clean_records_to_insert)} clean records into Silver layer.")
            
    except Exception as e:
        logging.error(f"Error during Silver transformation: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    process_bronze_to_silver()